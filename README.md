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
# Work in progress (hybrid approach PQC/JWT auth).
* **Rate Limiting:** IP-based throttling via `slowapi` to prevent DDoS and compute exhaustion.
* **Role-Based Auth:** JWT-secured endpoints separating standard users from Admins.

## Testing
Run the comprehensive test suite inside the container terminal:
```bash
pytest -s -v tests
```

# Hybrid ML-KEM:
The routes (/pqc-handshake and /pqc-complete) from https://github.com/daniel-mar/vault_project/blob/main/app/api/routers/auth.py
are first creating a secure connection. The client and server exchange two sets of keys instead of one.

**Exchange Keys**
* Both sides calculate a public secret and a ML-KEM PQ-secret key. (Mathematically Quantum Safe).
* In Quantum, like hashing algorithms, both can derive the same pattern. Think: A text with the same salt value can create the same hash value. Quantum can create true randomness (refer to https://github.com/daniel-mar/quantum-rng).
* These secrets are combined mathematically into a secure master key.
Attackers must be able to crack both traditional encryption methods and PQC algorithms to read said data being passed.

**Establish Tunnel**
* Establishing a quantum-safe tunnel before credentials are passed within the /login route. Maintaining session state via tokens derived from the initial ephemeral exchange.

**Security Researchers** may try to:

* **Reuse** a valid token (token expiration used.)
* **Forge** or create a fake token (requires the unique shared_secret) or
* **Cross-polinate** by using another users(A) token's secret to access another user's(B) resources (validation logic in kyber_secret via session_id is embedded in the token).

OQS Library helps with agility by allowing the use of other PQC algorithms for different security and speed, depending on the needs.
