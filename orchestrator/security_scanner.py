import xml.etree.ElementTree as ET
import zipfile
import os
import tarfile
import PyPDF2

def scan_xml_for_xxe(filepath):
    """
    Scans an XML file for signs of a basic XXE payload.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if "<!ENTITY" in content and "SYSTEM" in content:
        return {"status": "vulnerable", "details": "XXE payload detected."}
    return {"status": "clean", "details": "No XXE payload detected."}

def scan_xml_for_billion_laughs(filepath):
    """
    Scans an XML file for signs of a Billion Laughs attack.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    declarations = content.count("<!ENTITY")
    references = content.count("&")
    if declarations > 5 and references > 80:
        return {"status": "vulnerable", "details": "Billion Laughs attack detected."}
    return {"status": "clean", "details": "No Billion Laughs attack detected."}

def scan_zip_for_traversal(filepath):
    """
    Scans a zip file for path traversal attempts.
    """
    with zipfile.ZipFile(filepath, 'r') as zf:
        for name in zf.namelist():
            if name.startswith("../") or os.path.isabs(name):
                return {"status": "vulnerable", "details": f"Path traversal detected in file: {name}"}
    return {"status": "clean", "details": "No path traversal detected."}

def scan_zip_for_bomb(filepath, max_ratio=10):
    """
    Scans a zip file for signs of a zip bomb.
    """
    total_uncompressed_size = sum(zinfo.file_size for zinfo in zipfile.ZipFile(filepath, 'r').infolist())
    compressed_size = os.path.getsize(filepath)
    ratio = total_uncompressed_size / compressed_size if compressed_size > 0 else 0
    if ratio > max_ratio:
        return {"status": "vulnerable", "details": f"High compression ratio ({ratio:.2f}) detected."}
    return {"status": "clean", "details": "Normal compression ratio."}

def scan_json_for_deserialization(filepath):
    """
    Scans a JSON file for deserialization keywords.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if '"__type__":' in content or '"object_type":' in content:
        return {"status": "vulnerable", "details": "Potential JSON deserialization vulnerability detected."}
    return {"status": "clean", "details": "No JSON deserialization keywords found."}

def scan_pdf_for_js(filepath):
    """
    Scans a PDF file for embedded JavaScript.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    if b'/JS' in content or b'/JavaScript' in content:
        return {"status": "vulnerable", "details": "Embedded JavaScript detected in PDF."}
    return {"status": "clean", "details": "No embedded JavaScript found in PDF."}

def scan_csv_for_dde(filepath):
    """
    Scans a CSV file for DDE payloads.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if content.strip().startswith("="):
        return {"status": "vulnerable", "details": "DDE payload detected in CSV."}
    return {"status": "clean", "details": "No DDE payload found in CSV."}

def scan_for_pdf_zip_polyglot(filepath):
    """
    Scans for a PDF/ZIP polyglot.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
    if content.startswith(b'%PDF') and b'PK\x03\x04' in content:
        return {"status": "vulnerable", "details": "PDF/ZIP polyglot detected."}
    return {"status": "clean", "details": "File is not a PDF/ZIP polyglot."}

def scan_docx_for_links(filepath):
    """
    Scans a DOCX file for potentially malicious links.
    """
    with zipfile.ZipFile(filepath, 'r') as zf:
        if 'word/document.xml' in zf.namelist():
            with zf.open('word/document.xml') as f:
                content = f.read().decode('utf-8')
                if 'file:///' in content:
                    return {"status": "vulnerable", "details": "External file link detected in DOCX."}
    return {"status": "clean", "details": "No external file links found in DOCX."}

def scan_xls_for_formulas(filepath):
    """
    Scans an XLS file for formulas.
    """
    formula_opcode = b'\x06\x00'
    with open(filepath, 'rb') as f:
        content = f.read()
        if formula_opcode in content:
            return {"status": "vulnerable", "details": "Formula detected in XLS file."}
    return {"status": "clean", "details": "No formulas detected in XLS file."}

def scan_pickle_for_rce(filepath):
    """
    Scans a pickle file for the REDUCE opcode.
    """
    with open(filepath, 'rb') as f:
        content = f.read()
        if b'R' in content:
            return {"status": "vulnerable", "details": "REDUCE opcode detected in pickle file."}
    return {"status": "clean", "details": "No REDUCE opcode found in pickle file."}

def scan_tar_for_traversal(filepath):
    """
    Scans a tar file for path traversal.
    """
    with tarfile.open(filepath, 'r') as tf:
        for member in tf.getmembers():
            if member.name.startswith("../") or os.path.isabs(member.name):
                return {"status": "vulnerable", "details": f"Path traversal detected in TAR file: {member.name}"}
    return {"status": "clean", "details": "No path traversal detected in TAR file."}

def scan_yaml_for_deserialization(filepath):
    """
    Scans a YAML file for deserialization payloads.
    """
    with open(filepath, 'r') as f:
        content = f.read()
    if '!!python/object/apply' in content:
        return {"status": "vulnerable", "details": "Potential YAML deserialization vulnerability detected."}
    return {"status": "clean", "details": "No YAML deserialization keywords found."}

def scan_image_for_malicious_metadata(filepath):
    """
    Scans an image file for malicious metadata.
    """
    # This is a simplified scanner. A real one would need to parse EXIF data.
    # For now, we'll just check for the presence of a script tag.
    with open(filepath, 'rb') as f:
        content = f.read()
        if b'<script>' in content:
            return {"status": "vulnerable", "details": "Script tag detected in image metadata."}
    return {"status": "clean", "details": "No script tags found in image metadata."}

def scan_pdf_for_hidden_text(filepath):
    """
    Scans a PDF file for hidden text by checking the text rendering mode.
    """
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                if '/Contents' in page:
                    contents = page['/Contents'].get_object()
                    if hasattr(contents, 'get_data'):
                        data = contents.get_data()
                        # Check for the text rendering mode '3' (invisible)
                        if b' 3 Tr' in data:
                            return {"status": "vulnerable", "details": "Hidden text detected in PDF."}
    except Exception:
        # If parsing fails, it's not a standard PDF or is corrupted.
        pass
    return {"status": "clean", "details": "No hidden text found in PDF."}