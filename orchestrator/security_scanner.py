import xml.etree.ElementTree as ET
import zipfile
import os
import tarfile

def scan_xml_for_xxe(filepath):
    """
    Scans an XML file for signs of a basic XXE payload.
    It checks for the presence of `<!ENTITY` and `SYSTEM` keywords.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if "<!ENTITY" in content and "SYSTEM" in content:
        return True
    return False

def scan_xml_for_billion_laughs(filepath):
    """
    Scans an XML file for signs of a Billion Laughs attack.
    It checks for a high number of nested entity references.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    # A simple heuristic: count the number of entity declarations and references.
    declarations = content.count("<!ENTITY")
    references = content.count("&")
    if declarations > 5 and references > 80:
        return True
    return False

def scan_zip_for_traversal(filepath):
    """
    Scans a zip file for path traversal attempts.
    """
    with zipfile.ZipFile(filepath, 'r') as zf:
        for name in zf.namelist():
            if name.startswith("../") or os.path.isabs(name):
                return True
    return False

def scan_zip_for_bomb(filepath, max_ratio=10):
    """
    Scans a zip file for signs of a zip bomb by checking the compression ratio.
    """
    total_uncompressed_size = 0
    for zinfo in zipfile.ZipFile(filepath, 'r').infolist():
        total_uncompressed_size += zinfo.file_size

    compressed_size = os.path.getsize(filepath)
    if compressed_size > 0 and (total_uncompressed_size / compressed_size) > max_ratio:
        return True
    return False

def scan_json_for_deserialization(filepath):
    """
    Scans a JSON file for keywords often used in insecure deserialization.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if '"__type__":' in content or '"object_type":' in content:
        return True
    return False

def scan_pdf_for_js(filepath):
    """
    Scans a PDF file for embedded JavaScript.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    if b'/JS' in content or b'/JavaScript' in content:
        return True
    return False

def scan_csv_for_dde(filepath):
    """
    Scans a CSV file for DDE payloads.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if content.strip().startswith("="):
        return True
    return False

def scan_for_pdf_zip_polyglot(filepath):
    """
    Scans for a PDF/ZIP polyglot by checking for both headers.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(b'%PDF') and b'PK\x03\x04' in content:
        return True
    return False

def scan_docx_for_links(filepath):
    """
    Scans a DOCX file for potentially malicious links.
    """
    with zipfile.ZipFile(filepath, 'r') as zf:
        if 'word/document.xml' in zf.namelist():
            with zf.open('word/document.xml') as f:
                content = f.read().decode('utf-8')
                if 'file:///' in content:
                    return True
    return False

def scan_xls_for_formulas(filepath):
    """
    Scans an XLS file for formulas by looking for the FORMULA record opcode.
    """
    # This heuristic looks for the BIFF8 FORMULA record opcode (0x0006).
    formula_opcode = b'\x06\x00'
    with open(filepath, 'rb') as f:
        content = f.read()
        if formula_opcode in content:
            return True
    return False

def scan_pickle_for_rce(filepath):
    """
    Scans a pickle file for the REDUCE opcode, which is a sign of RCE.
    """
    # This heuristic looks for the REDUCE opcode ('R').
    with open(filepath, 'rb') as f:
        content = f.read()
        if b'R' in content:
            return True
    return False

def scan_tar_for_traversal(filepath):
    """
    Scans a tar file for path traversal attempts.
    """
    with tarfile.open(filepath, 'r') as tf:
        for member in tf.getmembers():
            if member.name.startswith("../") or os.path.isabs(member.name):
                return True
    return False

def scan_yaml_for_deserialization(filepath):
    """
    Scans a YAML file for deserialization payloads.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if '!!python/object/apply' in content:
        return True
    return False