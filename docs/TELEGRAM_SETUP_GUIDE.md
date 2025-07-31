# 🤖 ATOM Telegram Notification Setup Guide

## 🚀 Complete Integration for Real-Time Arbitrage Alerts

This guide will help you set up Telegram notifications for your ATOM arbitrage system to receive real-time alerts about:

- 🎯 **Arbitrage Opportunities** (spreads ≥ 30bps)
- 🌊 **Curve Pool Depegs** (virtual price deviations)
- ✅ **Successful Trade Executions**
- ❌ **Failed Trade Attempts**
- 🤖 **Bot Status Updates**
- 🔐 **Manual Approval Requests** (high-value trades)

---

## 📋 Step 1: Create Your Telegram Bot

### 1.1 Message @BotFather
1. Open Telegram and search for `@BotFather`
2. Start a conversation with `/start`
3. Create a new bot with `/newbot`
4. Choose a name: `ATOM Arbitrage Bot`
5. Choose a username: `your_atom_arbitrage_bot`

### 1.2 Get Your Bot Token
BotFather will give you a token like:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

**⚠️ Keep this token secret!**

---

## 📋 Step 2: Get Your Chat ID

### 2.1 Start Your Bot
1. Click the link BotFather provides or search for your bot
2. Send `/start` to your bot
3. Send any message like "Hello ATOM!"

### 2.2 Get Chat ID
Visit this URL (replace `<YOUR_BOT_TOKEN>`):
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

Look for your message in the response and find the `chat.id`:
```json
{
  "message": {
    "chat": {
      "id": -1001234567890,  // This is your CHAT_ID
      "type": "private"
    }
  }
}
```

---

## 📋 Step 3: Configure Environment Variables

Add these to your `.env.local` file:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
TELEGRAM_CHAT_ID=-1001234567890
```

**🔒 Security Note:** Never commit these values to Git!

---

## 📋 Step 4: Test Your Integration

### 4.1 Start the Backend
```bash
cd backend
python main.py
```

### 4.2 Test Connection
```bash
curl http://localhost:8000/telegram/test
```

You should receive a test message in Telegram!

### 4.3 Test Notifications
```bash
# Test arbitrage notification
curl -X POST "http://localhost:8000/telegram/notify/arbitrage" \
  -H "Content-Type: application/json" \
  -d '{
    "token_a": "DAI",
    "token_b": "USDC", 
    "spread_bps": 45.2,
    "estimated_profit": 123.45,
    "dex_path": "DAI→USDC→GHO→DAI"
  }'

# Test depeg notification
curl -X POST "http://localhost:8000/telegram/notify/depeg" \
  -H "Content-Type: application/json" \
  -d '{
    "pool_address": "0x1234567890123456789012345678901234567890",
    "virtual_price": 0.985,
    "deviation": 0.025
  }'
```

---

## 🎯 Notification Types & Triggers

### 🎯 Arbitrage Opportunities
**Trigger:** Spread ≥ 30bps detected
**Message Format:**
```
🟠 ATOM ALERT 🟠
🕐 14:23:45 | ARBITRAGE_OPPORTUNITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Arbitrage Opportunity: DAI/USDC

Profitable spread detected on DAI→USDC→GHO→DAI

📊 Details:
• spread_bps: 45.2bps
• estimated_profit_usd: $123.45
• token_pair: DAI/USDC
• dex_path: DAI→USDC→GHO→DAI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 ATOM Arbitrage System | Base Sepolia
```

### 🌊 Depeg Alerts
**Trigger:** Curve virtual price deviation > 2%
**Message Format:**
```
🟠 ATOM ALERT 🟠
🕐 14:25:12 | DEPEG_DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌊 Curve Pool Depeg Detected

Virtual price deviation exceeds threshold

📊 Details:
• pool_address: 0x1234567890...
• virtual_price: 0.985
• deviation_percent: 2.5%
• threshold_percent: 2.0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 ATOM Arbitrage System | Base Sepolia
```

### ✅ Trade Success
**Trigger:** Successful arbitrage execution
**Message Format:**
```
🟡 ATOM ALERT 🟡
🕐 14:27:33 | TRADE_EXECUTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Triangular DAI→USDC→GHO Executed

Trade completed successfully

📊 Details:
• profit_usd: $45.67
• gas_used: 420000
• tx_hash: 0x1234567890...
• trade_type: Triangular DAI→USDC→GHO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧬 ATOM Arbitrage System | Base Sepolia
```

### 🔐 Manual Approval
**Trigger:** High-value trade requires approval
**Features:** Interactive buttons for Approve/Reject/Details

---

## 🎮 Interactive Commands

Send these commands to your bot:

- `/start` - Welcome message and setup
- `/status` - Current bot status
- `/stats` - Trading statistics (24h)
- `/test` - Send test notification
- `/help` - Show all commands

---

## 🔧 Advanced Configuration

### Rate Limiting
Notifications are rate-limited to prevent spam:
- Same alert type: Max 1 per 2 seconds
- Prevents duplicate notifications

### Priority Levels
- 🟢 **LOW** - Bot status updates
- 🟡 **NORMAL** - Standard opportunities (23-50bps)
- 🟠 **HIGH** - High-value opportunities (>50bps), depegs
- 🔴 **CRITICAL** - System errors, bot failures

### Approval Workflow
High-value trades (>$500 profit) trigger approval requests:
1. Notification sent with Approve/Reject buttons
2. 5-minute timeout for response
3. Trade executes only if approved
4. Automatic rejection on timeout

---

## 🚨 Troubleshooting

### Bot Not Responding
1. Check bot token in `.env.local`
2. Verify chat ID is correct
3. Ensure bot is started with `/start`
4. Check backend logs for errors

### No Notifications Received
1. Test connection: `GET /telegram/test`
2. Check environment variables
3. Verify bot has permission to message you
4. Check rate limiting (wait 2+ seconds between tests)

### API Errors
Common issues:
- `401 Unauthorized` - Invalid bot token
- `400 Bad Request` - Invalid chat ID
- `429 Too Many Requests` - Rate limited

---

## 🔒 Security Best Practices

1. **Never share your bot token**
2. **Use private chats only** (not groups)
3. **Regularly rotate bot tokens**
4. **Monitor for unauthorized access**
5. **Keep `.env.local` out of version control**

---

## 🎯 Integration Status

✅ **Arbitrage Opportunity Notifications**
✅ **Depeg Detection Alerts**  
✅ **Trade Execution Results**
✅ **Bot Status Monitoring**
✅ **Interactive Commands**
✅ **Manual Approval Workflow**
✅ **Rate Limiting & Security**

**🚀 Your ATOM system now has complete Telegram integration!**

For support, contact the development team or check the logs at `/api/logs`.
