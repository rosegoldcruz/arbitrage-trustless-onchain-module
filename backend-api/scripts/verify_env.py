import os, json
keys = ["ENV","REDIS_HOST","REDIS_PORT","REDIS_DB","STREAM_NAMESPACE","CORS_ORIGINS"]
print(json.dumps({"missing":[k for k in keys if not os.getenv(k)],
                  "sample":{k:os.getenv(k) for k in keys}}, indent=2))
exit(1 if any(not os.getenv(k) for k in keys) else 0)