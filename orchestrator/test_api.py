import unittest
from fastapi.testclient import TestClient
from orchestrator.main import app
import os

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.output_dir = "generated_files"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def tearDown(self):
        # Clean up any generated files
        if os.path.exists(self.output_dir):
            for f in os.listdir(self.output_dir):
                os.remove(os.path.join(self.output_dir, f))
            os.rmdir(self.output_dir)
        # Clean up temp uploads
        temp_dir = "temp_uploads"
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, f))
            os.rmdir(temp_dir)

    def test_generate_endpoint(self):
        response = self.client.get("/generate/xxe")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers['content-disposition'].startswith('attachment; filename='))

    def test_scan_endpoint_clean(self):
        with open("clean_file.txt", "w") as f:
            f.write("This is a clean file.")
        with open("clean_file.txt", "rb") as f:
            response = self.client.post("/scan", files={"file": ("clean_file.txt", f, "text/plain")})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['scan_results'][0]['status'], 'clean')
        os.remove("clean_file.txt")

    def test_scan_endpoint_vulnerable(self):
        # Generate a vulnerable file
        from orchestrator import badfiles_generator
        filename = "test_xxe_for_api.xml"
        filepath = os.path.join(self.output_dir, filename)
        badfiles_generator.generate_xxe_file(filepath)

        with open(filepath, "rb") as f:
            response = self.client.post("/scan", files={"file": (filename, f, "application/xml")})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['scan_results'][0]['status'], 'vulnerable')

if __name__ == '__main__':
    unittest.main()