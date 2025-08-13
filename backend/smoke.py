#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
try:
    from main import app
    print("✅ App import successful")
    # Simple in-process health check
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    print("✅ Health endpoint returns 200")
    print("✅ Smoke test passed")
    sys.exit(0)
except Exception as e:
    print(f"❌ Smoke test failed: {e}")
    sys.exit(1)

