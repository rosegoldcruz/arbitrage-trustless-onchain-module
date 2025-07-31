/**
 * REAL-TIME API CLIENT
 * Connects frontend to REAL DEX data from backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface DashboardStatus {
  system_status: string;
  agents: Record<string, {
    status: string;
    profit: number;
    trades: number;
    type: string;
  }>;
  total_profit: number;
  active_agents: number;
  last_update: string;
  dex_connections: Record<string, string>;
  real_time_data: {
    gas_price: number;
    eth_price: number;
    spread_opportunities: number;
    profitable_paths: number;
  };
}

export interface ArbitrageOpportunity {
  id: string;
  path: string;
  spread_bps: number;
  profit_usd: number;
  dex_route: string;
  confidence: number;
  detected_at: string;
}

export interface ExecutionResult {
  opportunity_id: string;
  status: string;
  profit_realized: number;
  gas_used: number;
  tx_hash: string;
  executed_at: string;
}

export interface BotLog {
  timestamp: string;
  bot: string;
  level: string;
  message: string;
}

class RealTimeApi {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Get REAL dashboard status with live DEX data
   */
  async getDashboardStatus(): Promise<DashboardStatus> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/status`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch dashboard status');
    }
    
    return result.data;
  }

  /**
   * Get REAL arbitrage opportunities from DEX aggregator
   */
  async getOpportunities(): Promise<{
    opportunities: ArbitrageOpportunity[];
    total_opportunities: number;
    profitable_count: number;
    last_update: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/opportunities`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch opportunities');
    }
    
    return result.data;
  }

  /**
   * Get REAL DEX connection status
   */
  async getDexStatus(): Promise<{
    connections: Record<string, string>;
    healthy_connections: number;
    total_connections: number;
    last_check: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/dex-status`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch DEX status');
    }
    
    return result.data;
  }

  /**
   * Execute a REAL arbitrage opportunity
   */
  async executeOpportunity(opportunityId: string): Promise<ExecutionResult> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/execute-opportunity`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ opportunity_id: opportunityId }),
    });
    
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error(result.detail || 'Failed to execute opportunity');
    }
    
    return result.data;
  }

  /**
   * Get REAL bot logs and activity
   */
  async getBotLogs(): Promise<{
    logs: BotLog[];
    total_logs: number;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/bot-logs`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch bot logs');
    }
    
    return result.data;
  }

  /**
   * Start a specific bot
   */
  async startBot(botName: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/start-bot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bot_name: botName }),
    });
    
    const result = await response.json();
    return result;
  }

  /**
   * Stop a specific bot
   */
  async stopBot(botName: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/stop-bot`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bot_name: botName }),
    });
    
    const result = await response.json();
    return result;
  }

  /**
   * Get REAL market data
   */
  async getMarketData(): Promise<{
    gas_price: number;
    eth_price: number;
    base_fee: number;
    network_congestion: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/market-data`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch market data');
    }
    
    return result.data;
  }

  /**
   * Get REAL trading history
   */
  async getTradingHistory(limit: number = 50): Promise<{
    trades: Array<{
      id: string;
      timestamp: string;
      bot: string;
      type: string;
      profit: number;
      gas_used: number;
      tx_hash: string;
      status: string;
    }>;
    total_trades: number;
    total_profit: number;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/trading-history?limit=${limit}`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch trading history');
    }
    
    return result.data;
  }

  /**
   * Test DEX connections manually
   */
  async testDexConnections(): Promise<{
    test_results: Record<string, {
      status: string;
      response_time: number;
      error?: string;
    }>;
    overall_health: string;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/test-dex-connections`, {
      method: 'POST',
    });
    
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to test DEX connections');
    }
    
    return result.data;
  }

  /**
   * Get system health check
   */
  async getSystemHealth(): Promise<{
    overall_status: string;
    components: Record<string, {
      status: string;
      last_check: string;
      details?: string;
    }>;
    uptime: number;
  }> {
    const response = await fetch(`${this.baseUrl}/api/dashboard/system-health`);
    const result = await response.json();
    
    if (result.status !== 'success') {
      throw new Error('Failed to fetch system health');
    }
    
    return result.data;
  }
}

// Export singleton instance
export const realTimeApi = new RealTimeApi();

// All types are already exported above as interfaces
