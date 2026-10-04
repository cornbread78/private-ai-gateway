# 🤖 Rosie AI Gateway

> **Self-Contained, Hardware-Attested Confidential AI Proxy & Router**

Rosie AI Gateway is a lightweight, high-performance API proxy and routing gateway built for private, zero-leakage inference. It acts as an OpenAI- and Anthropic-compatible interface that leverages **Trusted Execution Environments (TEEs)** and **Attested Confidential Inference (ACI)** to guarantee complete data privacy down to the hardware memory layer.

---

## ✨ Key Features

* **🔒 Hardware-Level Privacy**: Executes inside isolated TEE hardware memory. Prompts and completions are inaccessible to host operators, cloud providers, or third parties.
* **🛡️ Attested Confidential Inference (ACI)**: Cryptographically verifies hardware attestation reports directly from the TEE vendor before transmitting any prompt payload.
* **⚡ OpenAI & Anthropic Compatibility**: Drop-in proxy replacement for standard `/v1/chat/completions` and Anthropic Messages API formats.
* **📦 100% Self-Contained Engine**: Standalone scripts and containerized configuration isolate local routing, memory, and updater routines from external data leakage.
* **🛑 Fail-Closed Routing**: Automatically rejects requests unless the upstream model route satisfies its own cryptographic attestation and channel-binding verification checks.

---

## 📁 Repository Architecture

```text
private-ai-gateway/
├── 🤖 rosie-core/            # Standalone execution runtime & API routing scripts
│   ├── gateway.py            # Local OpenAI/Anthropic compatible gateway process
│   ├── chat.sh               # Terminal client interface to Rosie
│   ├── updater.sh            # One-click environment updater script
│   └── compose.yaml          # Containerized isolated environment configuration
│
├── 🛡️ confidential-aci/      # TEE hardware attestation & channel-binding logic
│   ├── attestation-engine/   # TEE quote verification against vendor root
│   ├── key-custody/          # TLS channel binding to protected memory keys
│   └── zero-knowledge-proofs/# Verification logs and receipt validation
│
├── 🔑 rosie-proxy-cli/       # Client verification & proxy helpers
│   └── pap-curl.sh           # Hardware report verification wrapper for curl
│
└── 📚 rosie-docs/            # Security architecture & API documentation
    ├── self-contained-ai.md  # Memory isolation & privacy threat model
    └── api-reference.md      # REST routes & ACI verification specs
```

---

## 🚀 Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/cornbread78/private-ai-gateway.git
cd private-ai-gateway/rosie-core
```

### 2. Launch the Gateway
Start the self-contained Rosie engine using Docker Compose:
```bash
docker compose up -d
```

### 3. Send a Verified Request
Execute a chat session through the hardware-verified proxy wrapper:
```bash
../rosie-proxy-cli/pap-curl.sh https://your-tee-endpoint/v1/chat/completions   --header "Authorization: Bearer YOUR_API_KEY"   --header "Content-Type: application/json"   --data '{
    "model": "rosie-private",
    "messages": [{"role": "user", "content": "How does Rosie protect my data?"}],
    "provider": {"aci_verified": true}
  }'
```

---

## 🔒 Threat Model & Verification Flow

```text
+---------------+      1. Attestation Report Check      +---------------------------------+
|               |  ---------------------------------->  |                                 |
|  Rosie Client |                                       | Attested Workload (TEE Gateway) |
|  (pap / CLI)  |  <----------------------------------  |  - TLS key generated in memory  |
|               |      2. Pinned TLS Channel Bound      |  - Public code hash verified    |
+---------------+                                       +---------------------------------+
        |                                                                |
        +------------------ 3. Verified Prompt Request ------------------+
```

1. **Hardware Quote Verification**: The proxy fetches a fresh TEE report and checks vendor root credentials.
2. **Channel Binding**: The network connection pins strictly to cryptographic TLS keys generated inside TEE memory.
3. **Execution**: Prompts are processed strictly within protected hardware memory.

---

## 📄 License

Distributed under the Apache License 2.0. See `LICENSE` for details.
