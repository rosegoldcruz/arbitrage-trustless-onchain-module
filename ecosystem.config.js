module.exports = {
  apps: [{
    name: "atom-arbitrage",
    script: "backend/main.py",
    interpreter: "./venv/bin/python",
    cwd: "/var/www/arbitrage-trustless-onchain-module",
    watch: false,
    autorestart: true,
    max_memory_restart: "512M",
    env: {
      PYTHONUNBUFFERED: "1"
    }
  }]
};

