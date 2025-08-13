# 🚀 ATOM ARBITRAGE SYSTEM - PRODUCTION DEPLOYMENT GUIDE

## 📋 Prerequisites

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/rosegoldcruz/arbitrage-trustless-onchain-module.git
cd atom

# Install dependencies
pnpm install  # Frontend
pip install -r backend/requirements.txt  # Backend
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env.local

# Required environment variables:
PRIVATE_KEY=your_wallet_private_key_here
BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASESCAN_API_KEY=your_basescan_api_key
THEATOM_API_KEY=your_0x_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

### 3. Get Test Funds
- **Base Sepolia ETH**: https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet
- **Basescan API Key**: https://basescan.org/apis
- **0x API Key**: https://0x.org/docs/introduction/getting-started

---

## 🔗 Smart Contract Deployment

### 1. Compile Contracts
```bash
npm run compile
```

### 2. Deploy to Base Sepolia
```bash
node deploy-contracts.js
```

This will:
- Deploy FlashLoanArbitrage, AEON, PriceMonitor, TriangularArbitrage contracts
- Verify contracts on Basescan
- Update .env.local with contract addresses
- Save deployment summary to deployments/

### 3. Fund Contracts
```bash
node fund-contracts.js
```

---

## 🖥️ Backend Deployment

### 1. Start Backend API
```bash
cd backend
python main.py
```

Backend will be available at: http://localhost:8000

### 2. Verify Backend Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/monitoring/performance
```

### 3. Test Arbitrage Endpoints
```bash
# Test triangular arbitrage
curl -X POST http://localhost:8000/arbitrage/triangular \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{
    "token_a": "WETH",
    "token_b": "USDC", 
    "token_c": "DAI",
    "amount": 1.0
  }'

# Test flash loan
curl -X POST http://localhost:8000/flashloan/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_auth_token" \
  -d '{
    "token": "WETH",
    "amount": 10.0,
    "strategy": "triangular"
  }'
```

---

## 🌐 Frontend Deployment

### 1. Local Development
```bash
cd frontend
pnpm run dev
```

Frontend will be available at: http://localhost:3000

### 2. Production Build
```bash
pnpm run build
```

### 3. Deploy to Vercel
```bash
# Commit and push to main branch
git add .
git commit -m "Production deployment"
git push origin main

# Vercel will auto-deploy from GitHub
```

Frontend will be live at: https://aeoninvestmentstechnologies.com

---

## 🔧 Production Configuration

### 1. Update Frontend API URL
In `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://137.184.184.67:8000
```

### 2. Configure CORS
Backend automatically allows:
- https://aeoninvestmentstechnologies.com
- http://localhost:3000

### 3. Database Setup
Supabase tables are auto-created via backend/real_orchestrator.py

---

## 🧪 Testing & Validation

### 1. Run Contract Tests
```bash
npm run test
```

### 2. Test Backend Integration
```bash
python -m pytest backend/tests/
```

### 3. Validate Frontend
```bash
cd frontend
pnpm run lint
pnpm run type-check
```

---

## 📊 Monitoring & Alerts

### 1. Dashboard Monitoring
- **Performance**: https://aeoninvestmentstechnologies.com/dashboard
- **Trade History**: /monitoring/trades endpoint
- **System Health**: /health endpoint

### 2. Real-time Alerts
- Failed trades automatically logged
- Low profit warnings
- High gas cost alerts
- System health degradation

### 3. Supabase Logging
All trades logged to:
- `trade_executions` table
- `arbitrage_trades` table
- `system_alerts` table

---

## 🚨 Security Checklist

- ✅ All API endpoints protected with authentication
- ✅ Rate limiting implemented (10 requests/minute)
- ✅ Environment variables secured (not in Git)
- ✅ Smart contracts verified on Basescan
- ✅ Mandatory validation enforced (23bps spread, 0.25% ROI)
- ✅ Web3 transaction signing secured

---

## 🔄 Maintenance

### 1. Update Contract Addresses
After redeployment, update .env.local:
```bash
node deploy-contracts.js  # Auto-updates environment
```

### 2. Monitor System Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/monitoring/performance
```

### 3. Backup & Recovery
- Supabase auto-backups enabled
- Contract source code in Git
- Environment variables documented

---

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] Smart contracts deployed and verified
- [ ] Backend API running and healthy
- [ ] Frontend deployed to Vercel
- [ ] Database tables created
- [ ] Authentication working
- [ ] Monitoring endpoints responding
- [ ] Test trades executed successfully

---

## 🆘 Troubleshooting

### Common Issues:

1. **Contract deployment fails**
   - Check PRIVATE_KEY and BASE_SEPOLIA_RPC_URL
   - Ensure sufficient ETH balance
   - Verify network connectivity

2. **Backend API errors**
   - Check all environment variables
   - Verify Supabase connection
   - Check contract addresses

3. **Frontend build fails**
   - Run `pnpm run lint` and fix issues
   - Check TypeScript errors
   - Verify API_URL configuration

4. **Authentication issues**
   - Verify Clerk configuration
   - Check JWT token validation
   - Ensure CORS settings

---

## 📞 Support

For deployment issues:
1. Check logs in backend/logs/
2. Verify environment configuration
3. Test individual components
4. Review monitoring alerts

**System is now ready for production arbitrage execution! 🎉**
