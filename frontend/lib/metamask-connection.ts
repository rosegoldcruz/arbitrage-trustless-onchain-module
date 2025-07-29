/**
 * MetaMask Connection Utility
 * Handles wallet connection, network switching, and state management
 * Following AEON platform standards and Vercel best practices
 */

interface MetaMaskState {
  isConnected: boolean;
  account: string | null;
  chainId: string | null;
  balance: string | null;
  isLoading: boolean;
  error: string | null;
}

type StateListener = (state: MetaMaskState) => void;

class MetaMaskConnection {
  private state: MetaMaskState = {
    isConnected: false,
    account: null,
    chainId: null,
    balance: null,
    isLoading: false,
    error: null,
  };

  private listeners: Set<StateListener> = new Set();

  // Base Sepolia network configuration
  private readonly BASE_SEPOLIA_CONFIG = {
    chainId: '0x14A34', // 84532 in hex
    chainName: 'Base Sepolia',
    nativeCurrency: {
      name: 'ETH',
      symbol: 'ETH',
      decimals: 18,
    },
    rpcUrls: ['https://sepolia.base.org'],
    blockExplorerUrls: ['https://sepolia-explorer.base.org'],
  };

  constructor() {
    if (typeof window !== 'undefined') {
      this.initializeEventListeners();
      this.checkConnection();
    }
  }

  private initializeEventListeners() {
    if (!window.ethereum) return;

    window.ethereum.on('accountsChanged', this.handleAccountsChanged);
    window.ethereum.on('chainChanged', this.handleChainChanged);
    window.ethereum.on('disconnect', this.handleDisconnect);
  }

  private handleAccountsChanged = (accounts: string[]) => {
    if (accounts.length === 0) {
      this.updateState({
        isConnected: false,
        account: null,
        balance: null,
        error: null,
      });
    } else {
      this.updateState({
        account: accounts[0],
        isConnected: true,
        error: null,
      });
      this.updateBalance();
    }
  };

  private handleChainChanged = (chainId: string) => {
    this.updateState({ chainId, error: null });
  };

  private handleDisconnect = () => {
    this.updateState({
      isConnected: false,
      account: null,
      chainId: null,
      balance: null,
      error: null,
    });
  };

  private updateState(updates: Partial<MetaMaskState>) {
    this.state = { ...this.state, ...updates };
    this.notifyListeners();
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.state));
  }

  private async updateBalance() {
    if (!this.state.account || !window.ethereum) return;

    try {
      const balance = await window.ethereum.request({
        method: 'eth_getBalance',
        params: [this.state.account, 'latest'],
      });

      // Convert from wei to ETH
      const balanceInEth = (parseInt(balance, 16) / Math.pow(10, 18)).toFixed(4);
      this.updateState({ balance: balanceInEth });
    } catch (error) {
      console.error('Failed to fetch balance:', error);
    }
  }

  public isMetaMaskInstalled(): boolean {
    return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined';
  }

  public async checkConnection(): Promise<void> {
    if (!this.isMetaMaskInstalled() || !window.ethereum) return;

    try {
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      const chainId = await window.ethereum.request({ method: 'eth_chainId' });

      if (accounts.length > 0) {
        this.updateState({
          isConnected: true,
          account: accounts[0],
          chainId,
        });
        this.updateBalance();
      }
    } catch (error) {
      console.error('Failed to check connection:', error);
      this.updateState({ error: 'Failed to check wallet connection' });
    }
  }

  public async connect(): Promise<boolean> {
    if (!this.isMetaMaskInstalled() || !window.ethereum) {
      this.updateState({ error: 'MetaMask is not installed' });
      return false;
    }

    this.updateState({ isLoading: true, error: null });

    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });

      if (accounts.length > 0) {
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        
        this.updateState({
          isConnected: true,
          account: accounts[0],
          chainId,
          isLoading: false,
        });

        this.updateBalance();
        return true;
      }
    } catch (error: any) {
      console.error('Connection failed:', error);
      this.updateState({
        error: error.message || 'Failed to connect to MetaMask',
        isLoading: false,
      });
    }

    return false;
  }

  public async switchToBaseSepolia(): Promise<boolean> {
    if (!this.isMetaMaskInstalled() || !window.ethereum) return false;

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: this.BASE_SEPOLIA_CONFIG.chainId }],
      });
      return true;
    } catch (switchError: any) {
      // Chain not added to MetaMask
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [this.BASE_SEPOLIA_CONFIG],
          });
          return true;
        } catch (addError) {
          console.error('Failed to add Base Sepolia network:', addError);
          this.updateState({ error: 'Failed to add Base Sepolia network' });
        }
      } else {
        console.error('Failed to switch to Base Sepolia:', switchError);
        this.updateState({ error: 'Failed to switch to Base Sepolia network' });
      }
    }

    return false;
  }

  public disconnect(): void {
    this.updateState({
      isConnected: false,
      account: null,
      chainId: null,
      balance: null,
      error: null,
    });
  }

  public getState(): MetaMaskState {
    return { ...this.state };
  }

  public subscribe(listener: StateListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public isCorrectNetwork(): boolean {
    return this.state.chainId === this.BASE_SEPOLIA_CONFIG.chainId;
  }
}

// Global instance
export const metamaskConnection = new MetaMaskConnection();

// Type declarations moved to global.d.ts to avoid conflicts
