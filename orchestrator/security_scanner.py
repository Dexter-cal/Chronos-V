import xml.etree.ElementTree as ET
import zipfile
import os

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