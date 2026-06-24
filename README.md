# Post-Quantum Secure Vault API

A modular, enterprise-grade FastAPI backend testing Post-Quantum Cryptography (PQC) standards (Kyber768, ML-DSA-65) alongside standard RESTful authentication.

## Environment Setup
This project is built to run entirely inside an isolated Docker container using VS Code DevContainers, ensuring the C-based `liboqs` library compiles regardless of your host OS.

1. Open the project folder in VS Code.
2. Press `Ctrl+Shift+P` and select **"Dev Containers: Rebuild and Reopen in Container"**.
3. The environment will automatically install Python 3.12, Rust, and all required `requirements.txt` dependencies.

## Key Features
* **PQC Handshakes:** Kyber768 Key Encapsulation.
* **PQC Verification:** ML-DSA-65 Digital Signatures.
- Work in progress (hybrid apporach PQC/JWT auth).
* **Rate Limiting:** IP-based throttling via `slowapi` to prevent DDoS and compute exhaustion.
* **Role-Based Auth:** JWT-secured endpoints separating standard users from Admins.

## Testing
Run the comprehensive test suite inside the container terminal:
```bash
pytest -s tests/test_api.py