#!/bin/bash

# ============================================================================
# 🚀 ATOM PLUG & PLAY SETUP SCRIPT
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}🧬 ATOM - ARBITRAGE TRUSTLESS ON-CHAIN MODULE${NC}"
echo -e "${BLUE}🚀 PLUG & PLAY SETUP SCRIPT${NC}"
echo -e "${BLUE}============================================================================${NC}"

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from the frontend directory${NC}"
    exit 1
fi

# 1. Install dependencies
echo -e "\n${BLUE}📦 Installing dependencies...${NC}"
if command -v pnpm &> /dev/null; then
    pnpm install
    echo -e "${GREEN}✅ Dependencies installed with pnpm${NC}"
else
    echo -e "${YELLOW}⚠️  pnpm not found, using npm...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencies installed with npm${NC}"
fi

# 2. Check environment file
echo -e "\n${BLUE}🔧 Checking environment configuration...${NC}"
if [ -f ".env.local" ]; then
    echo -e "${GREEN}✅ .env.local file exists${NC}"
    
    # Check for placeholder contract addresses
    if grep -q "0x0000000000000000000000000000000000000000" .env.local; then
        echo -e "${YELLOW}⚠️  WARNING: Some contract addresses are placeholders${NC}"
        echo -e "${YELLOW}   Please update the following in .env.local:${NC}"
        echo -e "${YELLOW}   - ATOM_TRIANGULAR_ARBITRAGE_ADDRESS${NC}"
        echo -e "${YELLOW}   - ATOM_PRICE_MONITOR_ADDRESS${NC}"
        echo -e "${YELLOW}   - ATOM_EXECUTION_ENGINE_ADDRESS${NC}"
    fi
else
    echo -e "${RED}❌ .env.local file not found${NC}"
    echo -e "${BLUE}📋 Creating .env.local from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        echo -e "${GREEN}✅ .env.local created${NC}"
    else
        echo -e "${RED}❌ .env.example not found either${NC}"
        exit 1
    fi
fi

# 3. Verify Clerk configuration
echo -e "\n${BLUE}🔐 Checking Clerk configuration...${NC}"
if grep -q "pk_test_" .env.local && grep -q "sk_test_" .env.local; then
    echo -e "${GREEN}✅ Clerk keys configured${NC}"
    echo -e "${BLUE}📝 Remember to enable Web3 in Clerk Dashboard:${NC}"
    echo -e "${BLUE}   1. Go to https://dashboard.clerk.com/${NC}"
    echo -e "${BLUE}   2. Navigate to: User & Authentication > Web3${NC}"
    echo -e "${BLUE}   3. Enable: MetaMask, Coinbase Wallet, OKX Wallet${NC}"
else
    echo -e "${YELLOW}⚠️  Clerk keys may need configuration${NC}"
fi

# 4. Check Supabase configuration
echo -e "\n${BLUE}🗄️  Checking Supabase configuration...${NC}"
if grep -q "nmjvebcauoyqzjlnluos.supabase.co" .env.local; then
    echo -e "${GREEN}✅ Supabase configured for ATOM project${NC}"
else
    echo -e "${YELLOW}⚠️  Supabase configuration may need updates${NC}"
fi

# 5. Check blockchain configuration
echo -e "\n${BLUE}⛓️  Checking blockchain configuration...${NC}"
if grep -q "84532" .env.local; then
    echo -e "${GREEN}✅ Base Sepolia network configured${NC}"
else
    echo -e "${YELLOW}⚠️  Blockchain network configuration may need updates${NC}"
fi

# 6. Start development server
echo -e "\n${BLUE}🌐 Starting development server...${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo -e "\n${GREEN}🎯 ATOM Dashboard will be available at:${NC}"
echo -e "${GREEN}   Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}   Dashboard: http://localhost:3000/dashboard${NC}"
echo -e "${GREEN}   Wallet Test: http://localhost:3000/wallet-test${NC}"

# Start the server
if command -v pnpm &> /dev/null; then
    pnpm run dev
else
    npm run dev
fi
