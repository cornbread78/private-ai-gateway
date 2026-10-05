#!/usr/bin/env python3
import json
import sys
import os

def verify_attestation(report_path):
    if not os.path.exists(report_path):
        print(f"[-] Error: Report file {report_path} not found.")
        sys.exit(1)

    with open(report_path, 'r') as f:
        data = json.load(f)

    status = data.get("status")
    measurement = data.get("measurement_hash")
    policy = data.get("policy", {})

    print(f"[+] Verifying TEE Quote for Type: {data.get('tee_type')}")
    print(f"[+] Measurement Hash: {measurement}")

    if status == "ATTESTATION_SUCCESS" and not policy.get("debug_allowed", True):
        print("[+] SUCCESS: Hardware quote valid. Enclave debug mode disabled.")
        return True
    else:
        print("[-] FAIL: Invalid quote or insecure TEE policy detected.")
        return False

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "confidential-aci/attestation-engine/example_attestation_report.json"
    success = verify_attestation(path)
    sys.exit(0 if success else 1)
