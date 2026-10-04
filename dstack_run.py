
# --- Patch cryptography rust openssl bindings ---
try:
    import cryptography.hazmat.bindings._rust as _rust_mod
    if not hasattr(_rust_mod, "exceptions"):
        class DummyExceptions:
            UnsupportedAlgorithm = Exception
            AlreadyFinalized = Exception
            AlreadyUpdating = Exception
            InvalidTag = Exception
            InternalError = Exception
        _rust_mod.exceptions = DummyExceptions()
        
    if hasattr(_rust_mod, "openssl"):
        if not hasattr(_rust_mod.openssl, "ciphers"):
            class DummyCiphers:
                CipherContext = type("CipherContext", (), {})
            _rust_mod.openssl.ciphers = DummyCiphers()
        elif not hasattr(_rust_mod.openssl.ciphers, "CipherContext"):
            _rust_mod.openssl.ciphers.CipherContext = type("CipherContext", (), {})
except Exception as e:
    print("Warning during crypto binding patch:", e)
# --------------------------------------------------

