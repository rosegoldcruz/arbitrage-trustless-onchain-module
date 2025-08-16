from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import base64

router = APIRouter()

# No placeholder. Your real signing secret (from Clerk)
CLERK_WEBHOOK_SECRET = "whsec_xiG-3dTxxED8KhMBI6y-K_2oovIzhh8RXeqDZo5"

def verify_signature(payload: bytes, signature: str, timestamp: str, secret: str) -> bool:
    try:
        to_sign = f"{timestamp}.{payload.decode()}".encode()
        mac = hmac.new(key=base64.b64decode(secret), msg=to_sign, digestmod=hashlib.sha256)
        expected_signature = base64.b64encode(mac.digest()).decode()
        return hmac.compare_digest(expected_signature, signature)
    except Exception:
        return False

@router.post("/api/clerk-webhook")
async def clerk_webhook(
    request: Request,
    svix_id: str = Header(..., convert_underscores=False),
    svix_signature: str = Header(..., convert_underscores=False),
    svix_timestamp: str = Header(..., convert_underscores=False)
):
    body = await request.body()

    if not verify_signature(body, svix_signature, svix_timestamp, CLERK_WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("type", "unknown")
    data = payload.get("data", {})

    print(f"[Clerk] 🔔 {event_type} received")

    # User events
    if event_type.startswith("user."):
        print(f"[User] {event_type}: {data.get('id')}")

    # Session events
    elif event_type.startswith("session."):
        print(f"[Session] {event_type}: {data.get('user_id')}")

    # Subscription + Billing
    elif event_type.startswith("subscription") or event_type.startswith("subscriptionItem"):
        print(f"[Billing] {event_type}: {data.get('id')}")

    # Role + Permission
    elif event_type.startswith("role.") or event_type.startswith("permission."):
        print(f"[Role/Permission] {event_type}: {data.get('id')}")

    # Payment attempt
    elif event_type.startswith("paymentAttempt."):
        print(f"[Payment] {event_type}: {data.get('id')}")

    # SMS / Email
    elif event_type.startswith("sms.") or event_type.startswith("email."):
        print(f"[Comms] {event_type}: {data.get('email_address_id', 'unknown')}")

    # Wallet list
    elif event_type.startswith("walletListEntry."):
        print(f"[Wallet] {event_type}: {data.get('id')}")

    else:
        print(f"[Clerk] ⚠️ Skipped unused or org-based event: {event_type}")

    return {"status": "ok"}
