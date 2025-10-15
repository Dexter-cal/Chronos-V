import unittest
import os
from orchestrator import badfiles_generator
from orchestrator import security_scanner

class TestSecurityScanner(unittest.TestCase):

    def test_xxe_detection(self):
        filename = "test_xxe.xml"
        badfiles_generator.generate_xxe_file(filename)
        self.assertTrue(security_scanner.scan_xml_for_xxe(filename))

    def test_billion_laughs_detection(self):
        filename = "test_billion_laughs.xml"
        badfiles_generator.generate_billion_laughs_file(filename)
        self.assertTrue(security_scanner.scan_xml_for_billion_laughs(filename))

    def test_zip_traversal_detection(self):
        filename = "test_zip_traversal.zip"
        badfiles_generator.create_archive_with_traversal(filename)
        self.assertTrue(security_scanner.scan_zip_for_traversal(filename))

    def test_zip_bomb_detection(self):
        filename = "test_zip_bomb.zip"
        badfiles_generator.create_compressed_archive_bomb(filename)
        self.assertTrue(security_scanner.scan_zip_for_bomb(filename))

    def tearDown(self):
        # Clean up any generated files after each test
        for f in os.listdir():
            if f.endswith((".xml", ".zip", ".gz", ".svg", ".csv", ".gif", ".txt", ".exe", ".sh")):
                os.remove(f)

if __name__ == '__main__':
    unittest.main()