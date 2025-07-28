const { utils } = require('ethers');
const TelegramBot = require('node-telegram-bot-api');

class SpreadMonitor {
  constructor(dexEndpoints, alertThresholdBps = 23) {
    this.dexes = dexEndpoints;
    this.threshold = alertThresholdBps;
    this.bot = new TelegramBot(process.env.TELEGRAM_TOKEN);
  }

  async startMonitoring() {
    setInterval(async () => {
      for (const pair of Object.keys(this.dexes)) {
        const [tokenA, tokenB] = pair.split('/');
        const spreads = [];
        
        for (const dex of this.dexes[pair]) {
          const price = await this.fetchDexPrice(dex, tokenA, tokenB);
          spreads.push(price);
        }
        
        const maxSpread = this.calculateMaxSpreadBps(spreads);
        if (maxSpread > this.threshold) {
          this.triggerAlert(pair, maxSpread, spreads);
        }
      }
    }, 1500); // 1.5 second intervals
  }

  calculateMaxSpreadBps(prices) {
    const sorted = [...prices].sort((a,b) => a - b);
    const min = sorted[0];
    const max = sorted[sorted.length - 1];
    return utils.parseUnits(max.sub(min).mul(10000).div(min).toString());
  }

  async fetchDexPrice(dex, tokenA, tokenB) {
    // Implementation for:
    // - Curve: virtual price + amplification factor
    // - Balancer: weighted math (80/20, 98/2)
    // - Uniswap V2/V3
  }

  triggerAlert(pair, spreadBps, prices) {
    const msg = `🚨 ${pair} SPREAD ALERT!\n` + 
                `📊 Spread: ${spreadBps}bps\n` +
                `🏦 DEX Prices:\n${this.formatPrices(prices)}`;
    
    this.bot.sendMessage(process.env.CHAT_ID, msg);
  }
}

module.exports = SpreadMonitor;