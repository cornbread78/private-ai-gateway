import unittest
import os
import sys

# Append parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestRosieGateway(unittest.TestCase):
    def test_environment_setup(self):
        """Ensure core configuration files exist."""
        self.assertTrue(os.path.exists('compose.yaml') or os.path.exists('../compose.yaml'))

    def test_attestation_report_exists(self):
        """Ensure attestation engine proof output exists."""
        proof_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../confidential-aci/attestation-engine/example_attestation_report.json'))
        self.assertTrue(os.path.exists(proof_path))

if __name__ == '__main__':
    unittest.main()
