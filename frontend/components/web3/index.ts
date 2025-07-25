/**
 * Web3 Components Export
 * Centralized exports for all Web3-related components
 * Following AEON platform standards and Vercel best practices
 */

// Legacy MetaMask provider (keeping for compatibility)
export { Web3Provider, useWeb3, useMetaMaskInstalled } from './web3-provider';
export { default as MetaMaskConnector } from './metamask-connector';
export { default as WalletButton } from './wallet-button';

// New Web3Auth provider (recommended)
export { Web3AuthProvider, useWeb3Auth } from './web3auth-provider';
export { Web3AuthButton, Web3AuthButtonCompact, Web3AuthStatus } from './web3auth-button';
export { Web3AuthProfile } from './web3auth-profile';
