# 🔒 ATOM Environment Setup Guide

> **SECURITY NOTICE**: This repository contains NO environment files. All secrets must be configured manually.

## 🚨 Critical Security Policy

**ZERO TOLERANCE for environment files in Git:**
- ❌ No `.env` files of any kind
- ❌ No `.env.example` files  
- ❌ No `.env.local` files
- ❌ No environment templates
- ❌ No sample configurations
- ❌ No fake/dummy env files

**ALL environment variables must be set manually on each deployment environment.**

## 🔧 Required Environment Variables

### Frontend Environment Variables
Create these manually in your deployment environment:

```bash
# Web3Auth Configuration
NEXT_PUBLIC_WEB3AUTH_CLIENT_ID=your_web3auth_client_id_here

# Supabase Configuration  
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
```

### Backend Environment Variables
Create these manually in your deployment environment:

```bash
# Database
DATABASE_URL=your_supabase_database_url_here
SUPABASE_KEY=your_supabase_service_key_here

# Blockchain
PRIVATE_KEY=your_wallet_private_key_here
RPC_URL_BASE_SEPOLIA=https://sepolia.base.org
RPC_URL_BASE_MAINNET=https://mainnet.base.org

# API Keys
ALCHEMY_API_KEY=your_alchemy_key_here
INFURA_API_KEY=your_infura_key_here

# Security
JWT_SECRET=your_jwt_secret_here
API_SECRET_KEY=your_api_secret_here

# Environment
PYTHON_ENV=development
```

## 🔑 How to Get Required Keys

### 1. Web3Auth Client ID
1. Go to https://dashboard.web3auth.io/
2. Create a new project
3. Copy the Client ID
4. Set as `NEXT_PUBLIC_WEB3AUTH_CLIENT_ID`

### 2. Supabase Keys
1. Go to https://supabase.com/dashboard
2. Create/select your project
3. Go to Settings → API
4. Copy URL and anon key
5. Set as `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### 3. Blockchain Keys
1. Create a new wallet for development
2. Export private key (NEVER use mainnet wallet)
3. Set as `PRIVATE_KEY`
4. Get Base Sepolia ETH from faucet

### 4. API Keys
1. Alchemy: https://dashboard.alchemy.com/
2. Infura: https://infura.io/dashboard

## 🚀 Local Development Setup

### 1. Frontend Setup
```bash
cd frontend
pnpm install

# Manually create .env.local with required variables
# (File will be ignored by Git)

pnpm run dev
```

### 2. Backend Setup  
```bash
cd backend
pip install -r requirements.txt

# Manually create .env with required variables
# (File will be ignored by Git)

python start.py
```

## 🌐 Deployment Environments

### Vercel (Frontend)
1. Go to Vercel dashboard
2. Add environment variables in Settings
3. Deploy from Git

### Railway/DigitalOcean (Backend)
1. Set environment variables in platform dashboard
2. Deploy from Git

## ⚠️ Security Best Practices

1. **Never commit environment files**
2. **Use different keys for dev/staging/prod**
3. **Rotate keys regularly**
4. **Use least-privilege access**
5. **Monitor for leaked secrets**
6. **Use secure key management services**

## 🔍 Verification Checklist

Before deployment, verify:
- [ ] All required environment variables are set
- [ ] Keys are valid and working
- [ ] No environment files in Git
- [ ] Different keys for each environment
- [ ] Secrets are properly secured

## 🆘 Troubleshooting

### "Environment variable not found"
- Check variable name spelling
- Ensure variable is set in deployment environment
- Restart application after setting variables

### "Invalid API key"
- Verify key is correct
- Check key permissions
- Ensure key is for correct environment

### "Database connection failed"
- Verify Supabase URL and key
- Check network connectivity
- Ensure database is running

## 📞 Support

For environment setup issues:
1. Check this guide first
2. Verify all keys are set correctly
3. Test in development environment
4. Contact team if issues persist

---

**Remember: Security is paramount. Never compromise on environment variable protection.**
