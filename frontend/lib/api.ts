const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || 'https://api.smart4technology.com';

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  success: boolean;
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    console.log(`API Request: ${config.method || 'GET'} ${url}`);
    
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new ApiError(response.status, `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      data,
      success: true,
    };
  } catch (error) {
    console.error('API Error:', error);
    
    if (error instanceof ApiError) {
      return {
        error: error.message,
        success: false,
      };
    }
    
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      success: false,
    };
  }
}

// API endpoints
export const api = {
  // Health check
  health: () => apiRequest('/health'),

  // Arbitrage operations
  arbitrage: {
    execute: (data: { assetPair: string; network: string; amount?: number; minProfitThreshold?: number }) =>
      apiRequest('/arbitrage', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    trigger: (data: { token_triple: string[]; amount: string; force_execute?: boolean }) =>
      apiRequest('/arbitrage/trigger', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    opportunities: (params?: { network?: string; min_profit?: number; limit?: number }) => {
      const queryParams = new URLSearchParams();
      if (params?.network) queryParams.append('network', params.network);
      if (params?.min_profit) queryParams.append('min_profit', params.min_profit.toString());
      if (params?.limit) queryParams.append('limit', params.limit.toString());

      return apiRequest(`/arbitrage/opportunities${queryParams.toString() ? '?' + queryParams.toString() : ''}`);
    },
    stats: () => apiRequest('/arbitrage/stats'),
  },

  // Flash loan operations
  flashLoan: {
    execute: (data: { asset: string; amount: string; network: string; strategy?: string }) =>
      apiRequest('/flash-loan', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    providers: () => apiRequest('/flash-loan/providers'),
    simulate: (data: { asset: string; amount: string; network: string; strategy?: string }) =>
      apiRequest('/flash-loan/simulate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Bot deployment
  bot: {
    deploy: (data: { network: string; strategy?: string; token_pairs?: string[] }) =>
      apiRequest('/deploy-bot', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Token management
  tokens: {
    addPair: (data: { tokenA: string; tokenB: string; network: string; auto_trade?: boolean }) =>
      apiRequest('/tokens/add-pair', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    pairs: (params?: { network?: string; status?: string; limit?: number }) => {
      const queryParams = new URLSearchParams();
      if (params?.network) queryParams.append('network', params.network);
      if (params?.status) queryParams.append('status', params.status);
      if (params?.limit) queryParams.append('limit', params.limit.toString());

      return apiRequest(`/tokens/pairs${queryParams.toString() ? '?' + queryParams.toString() : ''}`);
    },
    supported: () => apiRequest('/tokens/supported'),
    prices: (params?: { symbols?: string; network?: string }) => {
      const queryParams = new URLSearchParams();
      if (params?.symbols) queryParams.append('symbols', params.symbols);
      if (params?.network) queryParams.append('network', params.network);

      return apiRequest(`/tokens/prices${queryParams.toString() ? '?' + queryParams.toString() : ''}`);
    },
    search: (query: string, network?: string, limit?: number) => {
      const queryParams = new URLSearchParams({ query });
      if (network) queryParams.append('network', network);
      if (limit) queryParams.append('limit', limit.toString());

      return apiRequest(`/tokens/search?${queryParams.toString()}`);
    },
  },

  // AI Agents
  agents: {
    getAll: () => apiRequest('/agents'),
    chat: (data: { message: string; agent?: string; context?: string }) =>
      apiRequest('/agents', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    start: (agentId: string) =>
      apiRequest(`/agents/${agentId}/start`, {
        method: 'POST',
      }),
    stop: (agentId: string) =>
      apiRequest(`/agents/${agentId}/stop`, {
        method: 'POST',
      }),
    performance: (agentId: string, days?: number) => {
      const queryParams = days ? `?days=${days}` : '';
      return apiRequest(`/agents/${agentId}/performance${queryParams}`);
    },
    configure: (agentId: string, config: any) =>
      apiRequest(`/agents/${agentId}/configure`, {
        method: 'POST',
        body: JSON.stringify(config),
      }),
  },

  // Statistics
  stats: {
    overview: () => apiRequest('/stats/overview'),
    daily: (days?: number) => {
      const queryParams = days ? `?days=${days}` : '';
      return apiRequest(`/stats/daily${queryParams}`);
    },
    tokens: () => apiRequest('/stats/tokens'),
    networks: () => apiRequest('/stats/networks'),
    chartProfit: (period?: string) => {
      const queryParams = period ? `?period=${period}` : '';
      return apiRequest(`/stats/chart/profit${queryParams}`);
    },
    chartVolume: (period?: string) => {
      const queryParams = period ? `?period=${period}` : '';
      return apiRequest(`/stats/chart/volume${queryParams}`);
    },
    performance: () => apiRequest('/stats/performance'),
  },

  // Trade History
  trades: {
    history: (params?: {
      limit?: number;
      offset?: number;
      status?: string;
      agent?: string;
      network?: string;
      pair?: string;
    }) => {
      const queryParams = new URLSearchParams();
      if (params?.limit) queryParams.append('limit', params.limit.toString());
      if (params?.offset) queryParams.append('offset', params.offset.toString());
      if (params?.status) queryParams.append('status', params.status);
      if (params?.agent) queryParams.append('agent', params.agent);
      if (params?.network) queryParams.append('network', params.network);
      if (params?.pair) queryParams.append('pair', params.pair);

      return apiRequest(`/trades/history${queryParams.toString() ? '?' + queryParams.toString() : ''}`);
    },
    stats: (params?: { days?: number; agent?: string; network?: string }) => {
      const queryParams = new URLSearchParams();
      if (params?.days) queryParams.append('days', params.days.toString());
      if (params?.agent) queryParams.append('agent', params.agent);
      if (params?.network) queryParams.append('network', params.network);

      return apiRequest(`/trades/stats${queryParams.toString() ? '?' + queryParams.toString() : ''}`);
    },
    recent: (limit?: number) => {
      const queryParams = limit ? `?limit=${limit}` : '';
      return apiRequest(`/trades/recent${queryParams}`);
    },
    details: (tradeId: string) => apiRequest(`/trades/${tradeId}`),
    popularPairs: () => apiRequest('/trades/pairs/popular'),
    simulate: (data: { pair: string; amount: number; network?: string; agent?: string }) =>
      apiRequest('/trades/simulate', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Contact form
  contact: {
    send: (data: { name: string; email: string; message: string }) =>
      apiRequest('/contact', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
};

export { ApiError };
export type { ApiResponse };
