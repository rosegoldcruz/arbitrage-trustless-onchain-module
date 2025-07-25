#!/usr/bin/env node
/**
 * 🤖 ATOM BOT - Advanced Triangular Opportunity Monitor
 * 🚀 Automated arbitrage execution with 23bps threshold enforcement
 * 
 * This bot runs every 30 seconds and:
 * 1. Checks Chainlink feeds for price updates
 * 2. Scans Uniswap/Balancer/Curve pools for opportunities
 * 3. Calculates spread in basis points
 * 4. Triggers executeArbitrage(...) when conditions are met
 */

const axios = require('axios');
const { ethers } = require('ethers');
const WebSocket = require('ws');
require('dotenv').config();

// ============================================================================
// 🔧 CONFIGURATION
// ============================================================================
const CONFIG = {
    // Network & RPC
    RPC_URL: process.env.BASE_SEPOLIA_RPC_URL || 'https://base-sepolia.g.alchemy.com/v2/ESBtk3UKjPt2rK2Yz0hnzUj0tIJGTe-d',
    CHAIN_ID: 84532, // Base Sepolia
    
    // Contract Addresses
    ATOM_CONTRACT: process.env.ATOM_CONTRACT_ADDRESS || '0xb3800E6bC7847E5d5a71a03887EDc5829DF4133b',
    
    // Bot Settings
    SCAN_INTERVAL: parseInt(process.env.ATOM_SCAN_INTERVAL) || 30000, // 30 seconds
    MIN_PROFIT_THRESHOLD: parseFloat(process.env.ATOM_MIN_PROFIT_THRESHOLD) || 10.0,
    MAX_GAS_PRICE: parseInt(process.env.ATOM_MAX_GAS_PRICE) || 50,
    MAX_CONCURRENT_TRADES: parseInt(process.env.ATOM_MAX_CONCURRENT_TRADES) || 3,
    EXECUTION_TIMEOUT: parseInt(process.env.ATOM_EXECUTION_TIMEOUT) || 30000,
    RETRY_ATTEMPTS: parseInt(process.env.ATOM_RETRY_ATTEMPTS) || 3,
    
    // API Endpoints
    BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://152.42.234.243:3001',
    TRIGGER_ENDPOINT: process.env.ATOM_ENDPOINT || 'http://152.42.234.243:3002/api/execute-trade',
    
    // Token Triples for Monitoring
    TOKEN_TRIPLES: [
        ['DAI', 'USDC', 'GHO'],   // Stablecoin triangle
        ['WETH', 'DAI', 'USDC'],  // ETH-stable triangle
        ['WETH', 'USDC', 'GHO'],  // ETH-stable-GHO triangle
    ],
    
    // Token Addresses (Base Sepolia)
    TOKENS: {
        'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
        'USDC': '0x036CbD53842c5426634e7929541eC2318f3dCF7e', 
        'WETH': '0x4200000000000000000000000000000000000006',
        'GHO': '0x40D16FC0246aD3160Ccc09B8D0D3A2cD28aE6C2f'
    }
};

// ============================================================================
// 🤖 ATOM BOT CLASS
// ============================================================================
class AtomBot {
    constructor() {
        this.provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
        this.isRunning = false;
        this.activeTrades = new Set();
        this.stats = {
            scansCompleted: 0,
            opportunitiesFound: 0,
            tradesExecuted: 0,
            totalProfit: 0,
            lastScanTime: null
        };
        
        console.log('🤖 ATOM Bot initialized');
        console.log(`📡 RPC: ${CONFIG.RPC_URL}`);
        console.log(`⏱️  Scan interval: ${CONFIG.SCAN_INTERVAL}ms`);
        console.log(`💰 Min profit: $${CONFIG.MIN_PROFIT_THRESHOLD}`);
    }
    
    /**
     * 🚀 Start the ATOM bot monitoring loop
     */
    async start() {
        if (this.isRunning) {
            console.log('⚠️  ATOM Bot already running');
            return;
        }
        
        this.isRunning = true;
        console.log('🚀 ATOM Bot starting...');
        
        // Start monitoring loop
        this.monitoringLoop();
        
        // Setup graceful shutdown
        process.on('SIGINT', () => this.stop());
        process.on('SIGTERM', () => this.stop());
    }
    
    /**
     * 🛑 Stop the ATOM bot
     */
    async stop() {
        console.log('🛑 ATOM Bot stopping...');
        this.isRunning = false;
        
        // Wait for active trades to complete
        if (this.activeTrades.size > 0) {
            console.log(`⏳ Waiting for ${this.activeTrades.size} active trades to complete...`);
            while (this.activeTrades.size > 0) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        
        console.log('✅ ATOM Bot stopped');
        process.exit(0);
    }
    
    /**
     * 🔄 Main monitoring loop - runs every 30 seconds
     */
    async monitoringLoop() {
        while (this.isRunning) {
            try {
                await this.scanForOpportunities();
                this.stats.scansCompleted++;
                this.stats.lastScanTime = new Date().toISOString();
                
                // Log stats every 10 scans
                if (this.stats.scansCompleted % 10 === 0) {
                    this.logStats();
                }
                
            } catch (error) {
                console.error('❌ Monitoring loop error:', error.message);
            }
            
            // Wait for next scan
            await new Promise(resolve => setTimeout(resolve, CONFIG.SCAN_INTERVAL));
        }
    }
    
    /**
     * 🔍 Scan all token triples for arbitrage opportunities
     */
    async scanForOpportunities() {
        console.log(`🔍 Scanning ${CONFIG.TOKEN_TRIPLES.length} token triples...`);
        
        for (const triple of CONFIG.TOKEN_TRIPLES) {
            if (this.activeTrades.size >= CONFIG.MAX_CONCURRENT_TRADES) {
                console.log('⏸️  Max concurrent trades reached, skipping scan');
                break;
            }
            
            try {
                await this.checkTriple(triple);
            } catch (error) {
                console.error(`❌ Error checking triple ${triple.join('->')}:`, error.message);
            }
        }
    }
    
    /**
     * 🎯 Check a specific token triple for arbitrage opportunity
     */
    async checkTriple(triple) {
        const [tokenA, tokenB, tokenC] = triple;
        const tokenAddresses = [
            CONFIG.TOKENS[tokenA],
            CONFIG.TOKENS[tokenB], 
            CONFIG.TOKENS[tokenC]
        ];
        
        // Calculate trade amount (1 ETH equivalent)
        const amount = ethers.parseEther('1.0');
        
        console.log(`🔍 Checking ${tokenA} → ${tokenB} → ${tokenC} → ${tokenA}`);
        
        try {
            // Call backend trigger endpoint
            const response = await axios.post(`${CONFIG.BACKEND_URL}/arbitrage/trigger`, {
                token_triple: tokenAddresses,
                amount: amount.toString(),
                force_execute: false
            }, {
                timeout: 10000,
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = response.data;
            
            if (result.triggered) {
                this.stats.opportunitiesFound++;
                this.stats.tradesExecuted++;
                this.stats.totalProfit += result.expected_profit;
                
                console.log(`🚀 ARBITRAGE TRIGGERED!`);
                console.log(`   Triple: ${triple.join(' → ')}`);
                console.log(`   Spread: ${result.spread_bps}bps`);
                console.log(`   Profit: $${result.expected_profit.toFixed(2)}`);
                console.log(`   Gas: $${result.gas_estimate.toFixed(2)}`);
                console.log(`   TX: ${result.transaction_hash}`);
                
                // Track active trade
                this.activeTrades.add(result.transaction_hash);
                
                // Remove from active trades after execution time
                setTimeout(() => {
                    this.activeTrades.delete(result.transaction_hash);
                }, result.execution_time * 1000);
                
            } else {
                console.log(`⏭️  ${triple.join('->')}: ${result.reason}`);
            }
            
        } catch (error) {
            if (error.code === 'ECONNREFUSED') {
                console.error('❌ Backend connection refused - is the server running?');
            } else {
                console.error(`❌ API call failed for ${triple.join('->')}:`, error.message);
            }
        }
    }
    
    /**
     * 📊 Log bot statistics
     */
    logStats() {
        console.log('\n📊 ATOM BOT STATISTICS');
        console.log('========================');
        console.log(`🔍 Scans completed: ${this.stats.scansCompleted}`);
        console.log(`🎯 Opportunities found: ${this.stats.opportunitiesFound}`);
        console.log(`💰 Trades executed: ${this.stats.tradesExecuted}`);
        console.log(`💵 Total profit: $${this.stats.totalProfit.toFixed(2)}`);
        console.log(`🔄 Active trades: ${this.activeTrades.size}`);
        console.log(`⏰ Last scan: ${this.stats.lastScanTime}`);
        console.log('========================\n');
    }
}

// ============================================================================
// 🚀 MAIN EXECUTION
// ============================================================================
async function main() {
    console.log('🧬 ATOM - Advanced Triangular Opportunity Monitor');
    console.log('🚀 Starting automated arbitrage bot...\n');
    
    const bot = new AtomBot();
    await bot.start();
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

// Start the bot
if (require.main === module) {
    main().catch(console.error);
}

module.exports = AtomBot;
