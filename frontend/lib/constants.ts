// Supported networks
export const NETWORKS = {
  ETHEREUM: 'ethereum',
  BASE: 'base',
  ARBITRUM: 'arbitrum',
  POLYGON: 'polygon',
} as const;

export type Network = typeof NETWORKS[keyof typeof NETWORKS];

// Supported DEXs
export const DEXS = {
  UNISWAP: 'uniswap',
  CURVE: 'curve',
  SUSHISWAP: 'sushiswap',
  BALANCER: 'balancer',
} as const;

export type Dex = typeof DEXS[keyof typeof DEXS];

// AI Agents
export const AGENTS = {
  ATOM: 'atom',
  ADOM: 'adom',
  MEV_SENTINEL: 'mev_sentinel',
} as const;

export type Agent = typeof AGENTS[keyof typeof AGENTS];

// Trading modes
export const TRADING_MODES = {
  TEST: 'test',
  LIVE: 'live',
} as const;

export type TradingMode = typeof TRADING_MODES[keyof typeof TRADING_MODES];

// Default values
export const DEFAULTS = {
  NETWORK: NETWORKS.BASE,
  TRADING_MODE: TRADING_MODES.TEST,
  MIN_PROFIT_THRESHOLD: 0.01, // 1%
  MAX_GAS_PRICE: 50, // gwei
  SLIPPAGE_TOLERANCE: 0.005, // 0.5%
} as const;

// API endpoints
export const API_ENDPOINTS = {
  HEALTH: '/health',
  ARBITRAGE: '/arbitrage',
  FLASH_LOAN: '/flash-loan',
  DEPLOY_BOT: '/deploy-bot',
  ADD_TOKEN: '/add-token',
  AGENT_CHAT: '/agent-chat',
  CONTACT: '/contact',
} as const;

// Local storage keys
export const STORAGE_KEYS = {
  THEME: 'atom-theme',
  BACKEND_URL: 'atom-backend-url',
  USER_PREFERENCES: 'atom-user-preferences',
  WALLET_CONNECTION: 'atom-wallet-connection',
} as const;

// Error messages
export const ERROR_MESSAGES = {
  WALLET_NOT_CONNECTED: 'Please connect your wallet first',
  INSUFFICIENT_BALANCE: 'Insufficient balance for this operation',
  NETWORK_NOT_SUPPORTED: 'This network is not supported',
  TRANSACTION_FAILED: 'Transaction failed. Please try again.',
  API_ERROR: 'API request failed. Please check your connection.',
  INVALID_INPUT: 'Please check your input and try again',
} as const;

// Success messages
export const SUCCESS_MESSAGES = {
  ARBITRAGE_EXECUTED: 'Arbitrage executed successfully!',
  BOT_DEPLOYED: 'Bot deployed successfully!',
  TOKEN_ADDED: 'Token pair added successfully!',
  MESSAGE_SENT: 'Message sent successfully!',
  SETTINGS_SAVED: 'Settings saved successfully!',
} as const;
