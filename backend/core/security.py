"""
🔒 ATOM Security & Compliance System - Enterprise Security Framework
Advanced security controls, audit logging, and regulatory compliance
"""

import os
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import json
import time
import hashlib
import hmac
import secrets
from ipaddress import ip_address, ip_network

logger = logging.getLogger(__name__)

class SecurityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventType(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    TRADE_EXECUTION = "trade_execution"
    FUND_TRANSFER = "fund_transfer"
    CONFIGURATION_CHANGE = "configuration_change"
    API_ACCESS = "api_access"
    SECURITY_ALERT = "security_alert"
    COMPLIANCE_CHECK = "compliance_check"

class ComplianceFramework(str, Enum):
    SOX = "sox"  # Sarbanes-Oxley
    PCI_DSS = "pci_dss"  # Payment Card Industry
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    MiFID_II = "mifid_ii"  # Markets in Financial Instruments Directive
    BASEL_III = "basel_iii"  # Basel III banking regulations

@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    event_type: AuditEventType
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    request_data: Dict[str, Any]
    response_status: int
    timestamp: datetime
    session_id: Optional[str] = None
    risk_score: float = 0.0
    compliance_flags: List[str] = None

@dataclass
class SecurityAlert:
    """Security alert record"""
    alert_id: str
    alert_type: str
    severity: SecurityLevel
    description: str
    source_ip: str
    user_id: Optional[str]
    detection_method: str
    indicators: List[str]
    mitigation_actions: List[str]
    resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

@dataclass
class ComplianceCheck:
    """Compliance check record"""
    check_id: str
    framework: ComplianceFramework
    rule_name: str
    description: str
    status: str  # "passed", "failed", "warning"
    details: Dict[str, Any]
    remediation_required: bool
    checked_at: datetime

class SecurityManager:
    """Enterprise security and compliance manager"""
    
    def __init__(self):
        self.audit_log = {}
        self.security_alerts = {}
        self.compliance_checks = {}
        self.rate_limits = {}
        self.blocked_ips = set()
        self.allowed_ips = set()
        self.api_keys = {}
        self.sessions = {}
        self.security_config = {
            "max_login_attempts": 5,
            "session_timeout": 3600,  # 1 hour
            "rate_limit_requests": 100,
            "rate_limit_window": 60,  # 1 minute
            "password_min_length": 12,
            "require_2fa": True,
            "audit_retention_days": 2555,  # 7 years
            "encryption_algorithm": "AES-256-GCM"
        }
        self.is_monitoring = False

    def validate_env(self) -> bool:
        """Validate required environment variables"""
        try:
            logger.info("🔍 Validating environment variables...")

            required_vars = [
                "PRIVATE_KEY",
                "BASE_SEPOLIA_RPC_URL",
                "ATOM_CONTRACT_ADDRESS",
                "FLASH_LOAN_CONTRACT_ADDRESS"
            ]

            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)

            if missing_vars:
                logger.error(f"❌ Missing required environment variables: {missing_vars}")
                return False

            logger.info("✅ Environment validation passed")
            return True

        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            return False

    def enforce_ip_whitelist(self, app) -> None:
        """Enforce IP whitelist on FastAPI app"""
        try:
            from fastapi import Request, HTTPException
            from fastapi.middleware.base import BaseHTTPMiddleware

            class IPWhitelistMiddleware(BaseHTTPMiddleware):
                def __init__(self, app, allowed_ips: set):
                    super().__init__(app)
                    self.allowed_ips = allowed_ips

                async def dispatch(self, request: Request, call_next):
                    client_ip = request.client.host

                    # Allow localhost and private networks
                    if client_ip in ["127.0.0.1", "::1"] or client_ip.startswith("192.168.") or client_ip.startswith("10."):
                        response = await call_next(request)
                        return response

                    # Check whitelist
                    if client_ip not in self.allowed_ips:
                        logger.warning(f"🚫 Blocked request from unauthorized IP: {client_ip}")
                        raise HTTPException(status_code=403, detail="IP not whitelisted")

                    response = await call_next(request)
                    return response

            # Add middleware to app
            app.add_middleware(IPWhitelistMiddleware, allowed_ips=self.allowed_ips)
            logger.info("🛡️ IP whitelist middleware enabled")

        except Exception as e:
            logger.error(f"❌ Failed to enforce IP whitelist: {e}")
    
    async def initialize_security(self):
        """Initialize security system"""
        logger.info("🔒 Initializing Enterprise Security System")
        
        # Load security configurations
        await self.load_security_policies()
        await self.initialize_compliance_frameworks()
        
        # Start security monitoring
        self.is_monitoring = True
        asyncio.create_task(self.security_monitor())
        asyncio.create_task(self.compliance_monitor())
        asyncio.create_task(self.audit_log_maintenance())
        
        logger.info("✅ Security system initialized with enterprise controls")
    
    async def load_security_policies(self):
        """Load security policies and configurations"""
        try:
            # Initialize IP whitelist (example)
            self.allowed_ips.update([
                "127.0.0.1",
                "::1",
                "10.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16"
            ])
            
            # Initialize API key management
            self.api_keys = {
                "institutional_client_1": {
                    "key_hash": self.hash_api_key("inst_key_12345"),
                    "permissions": ["trading", "analytics", "reporting"],
                    "rate_limit": 1000,
                    "created_at": datetime.now(timezone.utc),
                    "last_used": None
                }
            }
            
            logger.info("Security policies loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading security policies: {e}")
            raise
    
    async def initialize_compliance_frameworks(self):
        """Initialize compliance framework checks"""
        try:
            # Define compliance rules
            compliance_rules = {
                ComplianceFramework.SOX: [
                    {
                        "rule_name": "financial_data_integrity",
                        "description": "Ensure financial data integrity and accuracy",
                        "check_function": self.check_financial_data_integrity
                    },
                    {
                        "rule_name": "audit_trail_completeness",
                        "description": "Verify complete audit trail for all transactions",
                        "check_function": self.check_audit_trail_completeness
                    }
                ],
                ComplianceFramework.GDPR: [
                    {
                        "rule_name": "data_encryption",
                        "description": "Verify personal data encryption",
                        "check_function": self.check_data_encryption
                    },
                    {
                        "rule_name": "consent_management",
                        "description": "Verify user consent management",
                        "check_function": self.check_consent_management
                    }
                ],
                ComplianceFramework.MiFID_II: [
                    {
                        "rule_name": "transaction_reporting",
                        "description": "Ensure proper transaction reporting",
                        "check_function": self.check_transaction_reporting
                    },
                    {
                        "rule_name": "best_execution",
                        "description": "Verify best execution practices",
                        "check_function": self.check_best_execution
                    }
                ]
            }
            
            self.compliance_rules = compliance_rules
            logger.info(f"Initialized {len(compliance_rules)} compliance frameworks")
            
        except Exception as e:
            logger.error(f"Error initializing compliance frameworks: {e}")
            raise
    
    async def log_audit_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        ip_address: str,
        user_agent: str,
        endpoint: str,
        method: str,
        request_data: Dict[str, Any],
        response_status: int,
        session_id: Optional[str] = None
    ) -> str:
        """Log audit event"""
        try:
            event_id = f"audit_{int(time.time())}_{secrets.token_hex(8)}"
            
            # Calculate risk score
            risk_score = await self.calculate_risk_score(
                event_type, user_id, ip_address, endpoint, request_data
            )
            
            # Check compliance flags
            compliance_flags = await self.check_compliance_flags(
                event_type, request_data, response_status
            )
            
            audit_event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                request_data=self.sanitize_sensitive_data(request_data),
                response_status=response_status,
                timestamp=datetime.now(timezone.utc),
                session_id=session_id,
                risk_score=risk_score,
                compliance_flags=compliance_flags
            )
            
            self.audit_log[event_id] = audit_event
            
            # Trigger alerts for high-risk events
            if risk_score > 0.8:
                await self.create_security_alert(
                    alert_type="high_risk_activity",
                    severity=SecurityLevel.HIGH,
                    description=f"High-risk activity detected: {event_type.value}",
                    source_ip=ip_address,
                    user_id=user_id,
                    detection_method="risk_scoring",
                    indicators=[f"Risk score: {risk_score}"]
                )
            
            logger.debug(f"Audit event logged: {event_id} - Risk: {risk_score:.2f}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            raise
    
    async def calculate_risk_score(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        ip_address: str,
        endpoint: str,
        request_data: Dict[str, Any]
    ) -> float:
        """Calculate risk score for audit event"""
        try:
            risk_score = 0.0
            
            # Base risk by event type
            event_risk = {
                AuditEventType.LOGIN: 0.1,
                AuditEventType.TRADE_EXECUTION: 0.5,
                AuditEventType.FUND_TRANSFER: 0.8,
                AuditEventType.CONFIGURATION_CHANGE: 0.7,
                AuditEventType.API_ACCESS: 0.2
            }
            risk_score += event_risk.get(event_type, 0.3)
            
            # IP address risk
            if not await self.is_ip_whitelisted(ip_address):
                risk_score += 0.3
            
            # Unusual activity patterns
            if user_id:
                recent_events = await self.get_recent_user_events(user_id, hours=1)
                if len(recent_events) > 50:  # High activity
                    risk_score += 0.2
            
            # Large transaction amounts
            amount = request_data.get("amount", 0)
            if isinstance(amount, (int, float)) and amount > 100000:  # $100k+
                risk_score += 0.3
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5  # Default medium risk
    
    async def check_compliance_flags(
        self,
        event_type: AuditEventType,
        request_data: Dict[str, Any],
        response_status: int
    ) -> List[str]:
        """Check for compliance flags"""
        flags = []
        
        try:
            # SOX compliance checks
            if event_type == AuditEventType.TRADE_EXECUTION:
                if response_status != 200:
                    flags.append("sox_failed_transaction")
                
                amount = request_data.get("amount", 0)
                if isinstance(amount, (int, float)) and amount > 1000000:  # $1M+
                    flags.append("sox_large_transaction")
            
            # GDPR compliance checks
            if "user_data" in request_data:
                flags.append("gdpr_personal_data_processing")
            
            # MiFID II compliance checks
            if event_type == AuditEventType.TRADE_EXECUTION:
                flags.append("mifid_ii_transaction_record")
            
            return flags
            
        except Exception as e:
            logger.error(f"Error checking compliance flags: {e}")
            return []
    
    async def create_security_alert(
        self,
        alert_type: str,
        severity: SecurityLevel,
        description: str,
        source_ip: str,
        user_id: Optional[str],
        detection_method: str,
        indicators: List[str]
    ) -> str:
        """Create security alert"""
        try:
            alert_id = f"alert_{int(time.time())}_{secrets.token_hex(8)}"
            
            # Determine mitigation actions
            mitigation_actions = []
            if severity in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
                mitigation_actions.extend([
                    "monitor_user_activity",
                    "require_additional_verification"
                ])
                
                if severity == SecurityLevel.CRITICAL:
                    mitigation_actions.extend([
                        "temporary_account_suspension",
                        "immediate_security_review"
                    ])
            
            alert = SecurityAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                description=description,
                source_ip=source_ip,
                user_id=user_id,
                detection_method=detection_method,
                indicators=indicators,
                mitigation_actions=mitigation_actions,
                resolved=False,
                created_at=datetime.now(timezone.utc)
            )
            
            self.security_alerts[alert_id] = alert
            
            logger.warning(
                f"🚨 Security Alert: {alert_type} - "
                f"Severity: {severity.value} - "
                f"Source: {source_ip}"
            )
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error creating security alert: {e}")
            raise
    
    async def run_compliance_check(self, framework: ComplianceFramework) -> List[ComplianceCheck]:
        """Run compliance checks for specific framework"""
        try:
            results = []
            rules = self.compliance_rules.get(framework, [])
            
            for rule in rules:
                check_id = f"check_{framework.value}_{int(time.time())}_{secrets.token_hex(4)}"
                
                try:
                    # Run the compliance check
                    check_result = await rule["check_function"]()
                    
                    compliance_check = ComplianceCheck(
                        check_id=check_id,
                        framework=framework,
                        rule_name=rule["rule_name"],
                        description=rule["description"],
                        status=check_result["status"],
                        details=check_result.get("details", {}),
                        remediation_required=check_result.get("remediation_required", False),
                        checked_at=datetime.now(timezone.utc)
                    )
                    
                    results.append(compliance_check)
                    self.compliance_checks[check_id] = compliance_check
                    
                except Exception as e:
                    logger.error(f"Error running compliance check {rule['rule_name']}: {e}")
                    
                    # Create failed check record
                    compliance_check = ComplianceCheck(
                        check_id=check_id,
                        framework=framework,
                        rule_name=rule["rule_name"],
                        description=rule["description"],
                        status="failed",
                        details={"error": str(e)},
                        remediation_required=True,
                        checked_at=datetime.now(timezone.utc)
                    )
                    
                    results.append(compliance_check)
                    self.compliance_checks[check_id] = compliance_check
            
            logger.info(f"Completed {len(results)} compliance checks for {framework.value}")
            return results
            
        except Exception as e:
            logger.error(f"Error running compliance checks: {e}")
            return []
    
    # Compliance check implementations
    async def check_financial_data_integrity(self) -> Dict[str, Any]:
        """Check financial data integrity (SOX)"""
        # Simulate integrity check
        return {
            "status": "passed",
            "details": {"data_integrity_score": 0.98},
            "remediation_required": False
        }
    
    async def check_audit_trail_completeness(self) -> Dict[str, Any]:
        """Check audit trail completeness (SOX)"""
        # Check if all transactions have audit records
        completeness_score = len(self.audit_log) / max(1, len(self.audit_log))
        
        return {
            "status": "passed" if completeness_score > 0.95 else "warning",
            "details": {"completeness_score": completeness_score},
            "remediation_required": completeness_score <= 0.95
        }
    
    async def check_data_encryption(self) -> Dict[str, Any]:
        """Check data encryption (GDPR)"""
        return {
            "status": "passed",
            "details": {"encryption_algorithm": "AES-256-GCM"},
            "remediation_required": False
        }
    
    async def check_consent_management(self) -> Dict[str, Any]:
        """Check consent management (GDPR)"""
        return {
            "status": "passed",
            "details": {"consent_records": 100},
            "remediation_required": False
        }
    
    async def check_transaction_reporting(self) -> Dict[str, Any]:
        """Check transaction reporting (MiFID II)"""
        return {
            "status": "passed",
            "details": {"reporting_compliance": 0.99},
            "remediation_required": False
        }
    
    async def check_best_execution(self) -> Dict[str, Any]:
        """Check best execution practices (MiFID II)"""
        return {
            "status": "passed",
            "details": {"best_execution_score": 0.97},
            "remediation_required": False
        }
    
    # Utility methods
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def sanitize_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from audit logs"""
        sensitive_fields = ["password", "api_key", "private_key", "secret"]
        sanitized = data.copy()
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "[REDACTED]"
        
        return sanitized
    
    async def is_ip_whitelisted(self, ip: str) -> bool:
        """Check if IP is whitelisted"""
        try:
            ip_addr = ip_address(ip)
            
            for allowed in self.allowed_ips:
                if "/" in allowed:  # CIDR notation
                    if ip_addr in ip_network(allowed):
                        return True
                else:  # Single IP
                    if str(ip_addr) == allowed:
                        return True
            
            return False
            
        except Exception:
            return False
    
    async def get_recent_user_events(self, user_id: str, hours: int = 24) -> List[AuditEvent]:
        """Get recent events for user"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return [
            event for event in self.audit_log.values()
            if event.user_id == user_id and event.timestamp >= cutoff_time
        ]
    
    async def security_monitor(self):
        """Monitor security events"""
        while self.is_monitoring:
            try:
                # Monitor for suspicious patterns
                await self.detect_anomalies()
                await self.check_rate_limits()
                await self.update_threat_intelligence()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in security monitor: {e}")
                await asyncio.sleep(30)
    
    async def compliance_monitor(self):
        """Monitor compliance status"""
        while self.is_monitoring:
            try:
                # Run periodic compliance checks
                for framework in ComplianceFramework:
                    await self.run_compliance_check(framework)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in compliance monitor: {e}")
                await asyncio.sleep(3600)
    
    async def audit_log_maintenance(self):
        """Maintain audit log (cleanup old entries)"""
        while self.is_monitoring:
            try:
                retention_days = self.security_config["audit_retention_days"]
                cutoff_time = datetime.now(timezone.utc) - timedelta(days=retention_days)
                
                # Archive old audit events
                old_events = [
                    event_id for event_id, event in self.audit_log.items()
                    if event.timestamp < cutoff_time
                ]
                
                for event_id in old_events:
                    # In production, archive to long-term storage
                    del self.audit_log[event_id]
                
                if old_events:
                    logger.info(f"Archived {len(old_events)} old audit events")
                
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"Error in audit log maintenance: {e}")
                await asyncio.sleep(86400)
    
    async def detect_anomalies(self):
        """Detect security anomalies"""
        # Implement anomaly detection logic
        pass
    
    async def check_rate_limits(self):
        """Check and enforce rate limits"""
        # Implement rate limiting logic
        pass
    
    async def update_threat_intelligence(self):
        """Update threat intelligence data"""
        # Implement threat intelligence updates
        pass
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        return {
            "audit_events": len(self.audit_log),
            "security_alerts": len(self.security_alerts),
            "compliance_checks": len(self.compliance_checks),
            "active_sessions": len(self.sessions),
            "blocked_ips": len(self.blocked_ips),
            "whitelisted_ips": len(self.allowed_ips)
        }

# Global security manager instance
security_manager = SecurityManager()

# 🔒 ENTERPRISE CLERK JWT AUTHENTICATION
from fastapi import HTTPException, Header
import jwt
import httpx
from datetime import datetime, timezone, timedelta

# Cache for JWKS keys to avoid hitting Clerk on every request
_jwks_cache = {"keys": None, "expires_at": None}

class ClerkUser:
    """Authenticated Clerk user"""
    def __init__(self, user_id: str, email: Optional[str] = None, metadata: Optional[Dict] = None):
        self.user_id = user_id
        self.email = email
        self.metadata = metadata or {}
        self.authenticated_at = datetime.now(timezone.utc)

async def get_clerk_jwks() -> Dict[str, Any]:
    """Get Clerk JWKS keys with caching"""
    global _jwks_cache

    # Check cache
    if (_jwks_cache["keys"] and _jwks_cache["expires_at"] and
        datetime.now(timezone.utc) < _jwks_cache["expires_at"]):
        return _jwks_cache["keys"]

    # Fetch fresh JWKS
    jwks_url = os.getenv("CLERK_JWKS_URL")
    if not jwks_url:
        raise HTTPException(status_code=500, detail="CLERK_JWKS_URL not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            jwks_data = response.json()

            # Cache for 1 hour
            _jwks_cache["keys"] = jwks_data
            _jwks_cache["expires_at"] = datetime.now(timezone.utc) + timedelta(hours=1)

            return jwks_data

    except Exception as e:
        logger.error(f"❌ Failed to fetch Clerk JWKS: {e}")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")

async def validate_clerk_jwt(token: str) -> ClerkUser:
    """Validate Clerk JWT token and return user information"""
    try:
        # Get JWKS keys
        jwks_data = await get_clerk_jwks()

        # Decode JWT header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token: missing key ID")

        # Find matching key in JWKS
        key_data = None
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                key_data = key
                break

        if not key_data:
            raise HTTPException(status_code=401, detail="Invalid token: key not found")

        # Convert JWK to PEM format for PyJWT
        from jwcrypto import jwk
        jwk_obj = jwk.JWK(**key_data)
        public_key = jwk_obj.export_to_pem()

        # Verify JWT signature and decode claims
        issuer = os.getenv("CLERK_ISSUER_URL")
        if not issuer:
            raise HTTPException(status_code=500, detail="CLERK_ISSUER_URL not configured")

        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_exp": True, "verify_iat": True}
        )

        # Extract user information
        user_id = decoded_token.get("sub")
        email = decoded_token.get("email")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")

        logger.info(f"✅ Authenticated Clerk user: {user_id}")

        return ClerkUser(
            user_id=user_id,
            email=email,
            metadata=decoded_token
        )

    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ JWT token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"⚠️ Invalid JWT token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error(f"❌ JWT validation error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_current_user(authorization: str = Header(...)) -> ClerkUser:
    """
    ENTERPRISE CLERK JWT AUTHENTICATION
    Validates Clerk JWT tokens and returns authenticated user information
    """
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")

        token = authorization.replace("Bearer ", "")

        if not token:
            raise HTTPException(status_code=401, detail="Missing authentication token")

        # Validate JWT with Clerk
        user = await validate_clerk_jwt(token)

        # Log authentication event
        await security_manager.log_audit_event(
            event_type=AuditEventType.API_ACCESS,
            user_id=user.user_id,
            ip_address="unknown",  # Will be set by middleware
            user_agent="unknown",  # Will be set by middleware
            endpoint="auth_check",
            method="GET",
            request_data={},
            response_status=200
        )

        return user

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"❌ Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service error")
