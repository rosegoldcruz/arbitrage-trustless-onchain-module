import json, os, redis
def _redis():
    url = os.getenv("REDIS_URL","redis://127.0.0.1:6379/0")
    return redis.from_url(url, decode_responses=True)
class Bus:
    def __init__(self, cfg=None): self.r = _redis()
    def publish(self, ch, msg): self.r.publish(ch, json.dumps(msg))
    def subscribe(self, ch, handler):
        ps = self.r.pubsub(ignore_subscribe_messages=True); ps.subscribe(ch)
        for m in ps.listen():
            try: handler(json.loads(m["data"]))
            except Exception as e: print(f"[bus:{ch}] handler error: {e}")
