"""
Contact form router
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import asyncio
from datetime import datetime

router = APIRouter()

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
    subject: Optional[str] = None
    priority: Optional[str] = "normal"

class ContactResponse(BaseModel):
    success: bool
    message: str
    ticket_id: Optional[str] = None

@router.post("/", response_model=ContactResponse)
async def send_contact_message(request: ContactRequest):
    """Send contact form message"""
    try:
        # Simulate email processing
        await asyncio.sleep(1)
        
        # Generate ticket ID
        ticket_id = f"ATOM-{datetime.now().strftime('%Y%m%d')}-{hash(request.email) % 10000:04d}"
        
        # In a real implementation, you would:
        # 1. Validate the input
        # 2. Send email via SMTP or email service
        # 3. Store in database
        # 4. Send confirmation email
        
        # Mock successful submission
        return ContactResponse(
            success=True,
            message=f"Thank you {request.name}! Your message has been received. We'll respond within 24 hours.",
            ticket_id=ticket_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/faq")
async def get_faq():
    """Get frequently asked questions"""
    faq_items = [
        {
            "question": "What is arbitrage and how does ATOM make it risk-free?",
            "answer": "Arbitrage involves buying an asset on one exchange and selling it on another to profit from price differences. ATOM makes this risk-free by using flash loans - you borrow the capital, execute the trade, and repay the loan all in a single transaction.",
            "category": "basics"
        },
        {
            "question": "Do I need any capital to start using ATOM?",
            "answer": "No! Flash loans provide the necessary funds for each arbitrage opportunity. You only pay a small fee (typically 0.05-0.09%) on the borrowed amount and keep all the profits.",
            "category": "getting_started"
        },
        {
            "question": "How much can I expect to earn?",
            "answer": "Earnings vary based on market conditions and gas fees. Users typically see returns ranging from 5-20% APY, with higher returns during volatile periods.",
            "category": "earnings"
        },
        {
            "question": "What are the risks involved?",
            "answer": "The main risks are gas fees for failed transactions and smart contract risks. The arbitrage itself is risk-free due to atomic flash loan transactions.",
            "category": "risks"
        },
        {
            "question": "Which blockchains does ATOM support?",
            "answer": "ATOM supports Ethereum, Base, Arbitrum, and Polygon networks, with integrations to major DEXs like Uniswap, Curve, and SushiSwap.",
            "category": "technical"
        }
    ]
    
    return {
        "faq": faq_items,
        "categories": ["basics", "getting_started", "earnings", "risks", "technical"],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/support-hours")
async def get_support_hours():
    """Get support availability information"""
    return {
        "support_hours": {
            "monday_friday": "9:00 AM - 6:00 PM UTC",
            "saturday": "10:00 AM - 4:00 PM UTC",
            "sunday": "Closed"
        },
        "response_times": {
            "general_inquiries": "24 hours",
            "technical_support": "12 hours",
            "urgent_issues": "4 hours",
            "enterprise_support": "2 hours"
        },
        "contact_methods": [
            {
                "method": "Email",
                "address": "support@atom-defi.com",
                "best_for": "General inquiries and detailed questions"
            },
            {
                "method": "Enterprise Email",
                "address": "enterprise@atom-defi.com",
                "best_for": "Enterprise solutions and partnerships"
            },
            {
                "method": "Discord",
                "address": "discord.gg/atom-defi",
                "best_for": "Community support and quick questions"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/submit", response_model=ContactResponse)
async def submit_contact_form(request: ContactRequest):
    """Submit contact form - alias for the main contact endpoint"""
    try:
        # Simulate form processing
        await asyncio.sleep(1)

        # Generate ticket ID
        ticket_id = f"ATOM-{datetime.now().strftime('%Y%m%d')}-{hash(request.email) % 10000:04d}"

        # Validate priority
        valid_priorities = ["low", "normal", "high", "urgent"]
        if request.priority not in valid_priorities:
            request.priority = "normal"

        # In a real implementation, you would:
        # 1. Validate the input more thoroughly
        # 2. Send email via SMTP or email service (SendGrid, AWS SES, etc.)
        # 3. Store in database with proper schema
        # 4. Send confirmation email to user
        # 5. Create internal ticket in support system
        # 6. Send notification to support team based on priority

        # Simulate different response times based on priority
        if request.priority == "urgent":
            response_time = "2 hours"
        elif request.priority == "high":
            response_time = "4 hours"
        elif request.priority == "normal":
            response_time = "24 hours"
        else:
            response_time = "48 hours"

        # Mock successful submission
        return ContactResponse(
            success=True,
            message=f"Thank you {request.name}! Your {request.priority} priority message has been received. "
                   f"We'll respond within {response_time}. Your ticket ID is {ticket_id}.",
            ticket_id=ticket_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit contact form: {str(e)}")

@router.get("/tickets/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """Get status of a support ticket"""
    try:
        # Validate ticket ID format
        if not ticket_id.startswith("ATOM-") or len(ticket_id) != 18:
            raise HTTPException(status_code=404, detail="Invalid ticket ID format")

        # Mock ticket status
        statuses = ["open", "in_progress", "waiting_for_response", "resolved"]
        status = random.choice(statuses)

        # Generate mock ticket data
        created_date = datetime.now() - timedelta(days=random.randint(0, 7))

        return {
            "ticket_id": ticket_id,
            "status": status,
            "priority": random.choice(["low", "normal", "high"]),
            "subject": "Support Request",
            "created_at": created_date.isoformat(),
            "last_updated": (created_date + timedelta(hours=random.randint(1, 48))).isoformat(),
            "assigned_agent": "Support Team",
            "estimated_resolution": "24-48 hours",
            "messages_count": random.randint(1, 5),
            "satisfaction_rating": random.choice([None, 4, 5]) if status == "resolved" else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ticket status: {str(e)}")

@router.get("/categories")
async def get_contact_categories():
    """Get available contact categories for better routing"""
    return {
        "categories": [
            {
                "id": "technical_support",
                "name": "Technical Support",
                "description": "Issues with trading bots, API, or platform functionality",
                "estimated_response": "12 hours",
                "priority": "high"
            },
            {
                "id": "account_issues",
                "name": "Account Issues",
                "description": "Login problems, account settings, or access issues",
                "estimated_response": "24 hours",
                "priority": "normal"
            },
            {
                "id": "trading_questions",
                "name": "Trading Questions",
                "description": "Questions about arbitrage strategies or trading performance",
                "estimated_response": "24 hours",
                "priority": "normal"
            },
            {
                "id": "billing_support",
                "name": "Billing Support",
                "description": "Subscription, payment, or billing related inquiries",
                "estimated_response": "24 hours",
                "priority": "normal"
            },
            {
                "id": "feature_request",
                "name": "Feature Request",
                "description": "Suggestions for new features or improvements",
                "estimated_response": "48 hours",
                "priority": "low"
            },
            {
                "id": "partnership",
                "name": "Partnership",
                "description": "Business partnerships and enterprise solutions",
                "estimated_response": "48 hours",
                "priority": "normal"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
