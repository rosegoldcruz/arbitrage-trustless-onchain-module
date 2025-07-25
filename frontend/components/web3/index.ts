/**
 * Web3 Components Export
 * Centralized exports for all Web3-related components
 * Following AEON platform standards and Vercel best practices
 */

// Legacy MetaMask provider (keeping for compatibility)
export { Web3Provider, useWeb3, useMetaMaskInstalled } from './web3-provider';
export { default as MetaMaskConnector } from './metamask-connector';
export { default as WalletButton } from './wallet-button';

// Web3Auth integration (primary)
export { default as Web3AuthButton } from './Web3AuthButton';
export { default as WalletConnectButton } from './WalletConnectButton';
