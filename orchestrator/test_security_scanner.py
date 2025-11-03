import unittest
import os
from orchestrator import badfiles_generator
from orchestrator import security_scanner

class TestSecurityScanner(unittest.TestCase):

    def test_xxe_detection(self):
        filename = "test_xxe.xml"
        badfiles_generator.generate_xxe_file(filename)
        self.assertEqual(security_scanner.scan_xml_for_xxe(filename)['status'], 'vulnerable')

    def test_billion_laughs_detection(self):
        filename = "test_billion_laughs.xml"
        badfiles_generator.generate_billion_laughs_file(filename)
        self.assertEqual(security_scanner.scan_xml_for_billion_laughs(filename)['status'], 'vulnerable')

    def test_zip_traversal_detection(self):
        filename = "test_zip_traversal.zip"
        badfiles_generator.create_archive_with_traversal(filename)
        self.assertEqual(security_scanner.scan_zip_for_traversal(filename)['status'], 'vulnerable')

    def test_zip_bomb_detection(self):
        filename = "test_zip_bomb.zip"
        badfiles_generator.create_compressed_archive_bomb(filename)
        self.assertEqual(security_scanner.scan_zip_for_bomb(filename)['status'], 'vulnerable')

    def test_json_deserialization_detection(self):
        filename = "test_payload.json"
        badfiles_generator.generate_json_deserialization_payload(filename)
        self.assertEqual(security_scanner.scan_json_for_deserialization(filename)['status'], 'vulnerable')


    def test_dde_detection(self):
        filename = "test_dde.csv"
        badfiles_generator.generate_dde_payload(filename)
        self.assertEqual(security_scanner.scan_csv_for_dde(filename)['status'], 'vulnerable')

    def test_pdf_zip_polyglot_detection(self):
        filename = "test_polyglot.pdf"
        badfiles_generator.generate_pdf_zip_polyglot(filename)
        self.assertEqual(security_scanner.scan_for_pdf_zip_polyglot(filename)['status'], 'vulnerable')


    def test_xls_formula_detection(self):
        filename = "test_malicious.xls"
        badfiles_generator.generate_malicious_xls(filename)
        self.assertEqual(security_scanner.scan_xls_for_formulas(filename)['status'], 'vulnerable')

    def test_pickle_rce_detection(self):
        filename = "test_payload.pkl"
        badfiles_generator.generate_pickle_payload(filename)
        self.assertEqual(security_scanner.scan_pickle_for_rce(filename)['status'], 'vulnerable')

    def test_tar_traversal_detection(self):
        filename = "test_traversal.tar"
        badfiles_generator.generate_tar_traversal(filename)
        self.assertEqual(security_scanner.scan_tar_for_traversal(filename)['status'], 'vulnerable')

    def test_yaml_deserialization_detection(self):
        filename = "test_payload.yaml"
        badfiles_generator.generate_yaml_payload(filename)
        self.assertEqual(security_scanner.scan_yaml_for_deserialization(filename)['status'], 'vulnerable')

    def test_image_metadata_detection(self):
        filename = "test_metadata.jpg"
        badfiles_generator.generate_image_with_malicious_metadata(filename)
        self.assertEqual(security_scanner.scan_image_for_malicious_metadata(filename)['status'], 'vulnerable')

    def test_fake_magic_bytes_detection(self):
        filename = "test_fake_magic.gif"
        badfiles_generator.generate_fake_magic_bytes(filename)
        self.assertEqual(security_scanner.scan_for_fake_magic_bytes(filename)['status'], 'vulnerable')

    def test_csv_html_detection(self):
        filename = "test_csv_xss.csv"
        badfiles_generator.generate_csv_with_html_payload(filename)
        self.assertEqual(security_scanner.scan_csv_for_html(filename)['status'], 'vulnerable')

    def test_rtf_ole_link_detection(self):
        filename = "test_ole.rtf"
        badfiles_generator.generate_rtf_with_ole_link(filename)
        self.assertEqual(security_scanner.scan_rtf_for_ole(filename)['status'], 'vulnerable')


    def tearDown(self):
        # Clean up any generated files after each test
        for f in os.listdir():
            if f.endswith((".xml", ".zip", ".gz", ".svg", ".csv", ".gif", ".txt", ".exe", ".sh")):
                os.remove(f)

if __name__ == '__main__':
    unittest.main()