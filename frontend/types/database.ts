/**
 * ATOM Arbitrage System - Database Types
 * Auto-generated TypeScript types for Supabase schema
 * Following AEON platform standards and Vercel best practices
 */

export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          wallet_address: string | null
          role: 'admin' | 'user' | 'viewer'
          is_active: boolean
          subscription_tier: 'free' | 'pro' | 'enterprise'
          created_at: string
          updated_at: string
          last_login: string | null
          settings: Json
        }
        Insert: {
          id: string
          email: string
          wallet_address?: string | null
          role?: 'admin' | 'user' | 'viewer'
          is_active?: boolean
          subscription_tier?: 'free' | 'pro' | 'enterprise'
          created_at?: string
          updated_at?: string
          last_login?: string | null
          settings?: Json
        }
        Update: {
          id?: string
          email?: string
          wallet_address?: string | null
          role?: 'admin' | 'user' | 'viewer'
          is_active?: boolean
          subscription_tier?: 'free' | 'pro' | 'enterprise'
          created_at?: string
          updated_at?: string
          last_login?: string | null
          settings?: Json
        }
      }
      arbitrage_config: {
        Row: {
          id: string
          user_id: string
          name: string
          description: string | null
          min_profit_basis_points: number
          max_slippage_basis_points: number
          max_gas_price_gwei: number
          gas_limit: number
          enabled_tokens: string[]
          enabled_dexes: string[]
          flash_loan_enabled: boolean
          preferred_flash_loan_provider: string | null
          max_trade_amount_eth: number
          max_daily_trades: number | null
          max_daily_loss_eth: number | null
          stop_loss_enabled: boolean | null
          is_active: boolean
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          name: string
          description?: string | null
          min_profit_basis_points?: number
          max_slippage_basis_points?: number
          max_gas_price_gwei?: number
          gas_limit?: number
          enabled_tokens?: string[]
          enabled_dexes?: string[]
          flash_loan_enabled?: boolean
          preferred_flash_loan_provider?: string | null
          max_trade_amount_eth?: number
          max_daily_trades?: number | null
          max_daily_loss_eth?: number | null
          stop_loss_enabled?: boolean | null
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          name?: string
          description?: string | null
          min_profit_basis_points?: number
          max_slippage_basis_points?: number
          max_gas_price_gwei?: number
          gas_limit?: number
          enabled_tokens?: string[]
          enabled_dexes?: string[]
          flash_loan_enabled?: boolean
          preferred_flash_loan_provider?: string | null
          max_trade_amount_eth?: number
          max_daily_trades?: number | null
          max_daily_loss_eth?: number | null
          stop_loss_enabled?: boolean | null
          is_active?: boolean
          created_at?: string
          updated_at?: string
        }
      }
      arbitrage_opportunities: {
        Row: {
          id: string
          config_id: string
          token_in: string
          token_out: string
          token_in_symbol: string | null
          token_out_symbol: string | null
          amount_in: number
          dex_buy: string
          dex_sell: string
          price_buy: number
          price_sell: number
          estimated_profit: number
          estimated_gas_cost: number
          profit_basis_points: number
          net_profit: number | null
          status: 'detected' | 'analyzing' | 'executing' | 'completed' | 'failed' | 'expired'
          priority: number | null
          detected_at: string
          analyzed_at: string | null
          executed_at: string | null
          completed_at: string | null
          expires_at: string
          tx_hash: string | null
          block_number: number | null
          actual_profit: number | null
          actual_gas_used: number | null
          error_message: string | null
          retry_count: number
          metadata: Json
        }
        Insert: {
          id?: string
          config_id: string
          token_in: string
          token_out: string
          token_in_symbol?: string | null
          token_out_symbol?: string | null
          amount_in: number
          dex_buy: string
          dex_sell: string
          price_buy: number
          price_sell: number
          estimated_profit: number
          estimated_gas_cost: number
          profit_basis_points: number
          status?: 'detected' | 'analyzing' | 'executing' | 'completed' | 'failed' | 'expired'
          priority?: number | null
          detected_at?: string
          analyzed_at?: string | null
          executed_at?: string | null
          completed_at?: string | null
          expires_at?: string
          tx_hash?: string | null
          block_number?: number | null
          actual_profit?: number | null
          actual_gas_used?: number | null
          error_message?: string | null
          retry_count?: number
          metadata?: Json
        }
        Update: {
          id?: string
          config_id?: string
          token_in?: string
          token_out?: string
          token_in_symbol?: string | null
          token_out_symbol?: string | null
          amount_in?: number
          dex_buy?: string
          dex_sell?: string
          price_buy?: number
          price_sell?: number
          estimated_profit?: number
          estimated_gas_cost?: number
          profit_basis_points?: number
          status?: 'detected' | 'analyzing' | 'executing' | 'completed' | 'failed' | 'expired'
          priority?: number | null
          detected_at?: string
          analyzed_at?: string | null
          executed_at?: string | null
          completed_at?: string | null
          expires_at?: string
          tx_hash?: string | null
          block_number?: number | null
          actual_profit?: number | null
          actual_gas_used?: number | null
          error_message?: string | null
          retry_count?: number
          metadata?: Json
        }
      }
      arbitrage_trades: {
        Row: {
          id: string
          opportunity_id: string | null
          config_id: string
          user_id: string
          token_in: string
          token_out: string
          token_in_symbol: string | null
          token_out_symbol: string | null
          amount_in: number
          amount_out: number | null
          dex_path: string
          route_details: Json
          flash_loan_amount: number | null
          flash_loan_premium: number | null
          flash_loan_provider: string | null
          profit: number
          profit_usd: number | null
          gas_used: number | null
          gas_price_gwei: number | null
          gas_cost_eth: number | null
          tx_hash: string | null
          block_number: number | null
          block_timestamp: string | null
          status: 'pending' | 'success' | 'failed' | 'reverted'
          executed_at: string
          confirmed_at: string | null
          error_message: string | null
          error_code: string | null
          metadata: Json
        }
        Insert: {
          id?: string
          opportunity_id?: string | null
          config_id: string
          user_id: string
          token_in: string
          token_out: string
          token_in_symbol?: string | null
          token_out_symbol?: string | null
          amount_in: number
          amount_out?: number | null
          dex_path: string
          route_details?: Json
          flash_loan_amount?: number | null
          flash_loan_premium?: number | null
          flash_loan_provider?: string | null
          profit?: number
          profit_usd?: number | null
          gas_used?: number | null
          gas_price_gwei?: number | null
          gas_cost_eth?: number | null
          tx_hash?: string | null
          block_number?: number | null
          block_timestamp?: string | null
          status?: 'pending' | 'success' | 'failed' | 'reverted'
          executed_at?: string
          confirmed_at?: string | null
          error_message?: string | null
          error_code?: string | null
          metadata?: Json
        }
        Update: {
          id?: string
          opportunity_id?: string | null
          config_id?: string
          user_id?: string
          token_in?: string
          token_out?: string
          token_in_symbol?: string | null
          token_out_symbol?: string | null
          amount_in?: number
          amount_out?: number | null
          dex_path?: string
          route_details?: Json
          flash_loan_amount?: number | null
          flash_loan_premium?: number | null
          flash_loan_provider?: string | null
          profit?: number
          profit_usd?: number | null
          gas_used?: number | null
          gas_price_gwei?: number | null
          gas_cost_eth?: number | null
          tx_hash?: string | null
          block_number?: number | null
          block_timestamp?: string | null
          status?: 'pending' | 'success' | 'failed' | 'reverted'
          executed_at?: string
          confirmed_at?: string | null
          error_message?: string | null
          error_code?: string | null
          metadata?: Json
        }
      }
      system_logs: {
        Row: {
          id: string
          level: 'debug' | 'info' | 'warn' | 'error' | 'critical'
          component: string
          message: string
          details: Json
          user_id: string | null
          trade_id: string | null
          opportunity_id: string | null
          session_id: string | null
          request_id: string | null
          ip_address: string | null
          user_agent: string | null
          created_at: string
        }
        Insert: {
          id?: string
          level: 'debug' | 'info' | 'warn' | 'error' | 'critical'
          component: string
          message: string
          details?: Json
          user_id?: string | null
          trade_id?: string | null
          opportunity_id?: string | null
          session_id?: string | null
          request_id?: string | null
          ip_address?: string | null
          user_agent?: string | null
          created_at?: string
        }
        Update: {
          id?: string
          level?: 'debug' | 'info' | 'warn' | 'error' | 'critical'
          component?: string
          message?: string
          details?: Json
          user_id?: string | null
          trade_id?: string | null
          opportunity_id?: string | null
          session_id?: string | null
          request_id?: string | null
          ip_address?: string | null
          user_agent?: string | null
          created_at?: string
        }
      }
      price_feeds: {
        Row: {
          id: string
          token_address: string
          token_symbol: string
          dex: string
          pair_address: string | null
          price: number
          price_usd: number | null
          volume_24h: number | null
          liquidity: number | null
          timestamp: string
          block_number: number | null
        }
        Insert: {
          id?: string
          token_address: string
          token_symbol: string
          dex: string
          pair_address?: string | null
          price: number
          price_usd?: number | null
          volume_24h?: number | null
          liquidity?: number | null
          timestamp?: string
          block_number?: number | null
        }
        Update: {
          id?: string
          token_address?: string
          token_symbol?: string
          dex?: string
          pair_address?: string | null
          price?: number
          price_usd?: number | null
          volume_24h?: number | null
          liquidity?: number | null
          timestamp?: string
          block_number?: number | null
        }
      }
      bot_status: {
        Row: {
          id: string
          config_id: string
          status: 'running' | 'stopped' | 'paused' | 'error' | 'maintenance'
          health_score: number | null
          last_scan_at: string | null
          opportunities_found: number
          trades_executed: number
          total_profit: number
          uptime_seconds: number
          error_message: string | null
          error_count: number
          last_error_at: string | null
          metadata: Json
          updated_at: string
        }
        Insert: {
          id?: string
          config_id: string
          status?: 'running' | 'stopped' | 'paused' | 'error' | 'maintenance'
          health_score?: number | null
          last_scan_at?: string | null
          opportunities_found?: number
          trades_executed?: number
          total_profit?: number
          uptime_seconds?: number
          error_message?: string | null
          error_count?: number
          last_error_at?: string | null
          metadata?: Json
          updated_at?: string
        }
        Update: {
          id?: string
          config_id?: string
          status?: 'running' | 'stopped' | 'paused' | 'error' | 'maintenance'
          health_score?: number | null
          last_scan_at?: string | null
          opportunities_found?: number
          trades_executed?: number
          total_profit?: number
          uptime_seconds?: number
          error_message?: string | null
          error_count?: number
          last_error_at?: string | null
          metadata?: Json
          updated_at?: string
        }
      }
      notifications: {
        Row: {
          id: string
          user_id: string
          type: 'trade_success' | 'trade_failed' | 'high_profit' | 'system_error' | 'config_change' | 'maintenance' | 'security_alert'
          priority: 'low' | 'normal' | 'high' | 'critical'
          title: string
          message: string
          data: Json
          read: boolean
          sent_email: boolean
          sent_telegram: boolean
          sent_discord: boolean
          created_at: string
          read_at: string | null
          expires_at: string
        }
        Insert: {
          id?: string
          user_id: string
          type: 'trade_success' | 'trade_failed' | 'high_profit' | 'system_error' | 'config_change' | 'maintenance' | 'security_alert'
          priority?: 'low' | 'normal' | 'high' | 'critical'
          title: string
          message: string
          data?: Json
          read?: boolean
          sent_email?: boolean
          sent_telegram?: boolean
          sent_discord?: boolean
          created_at?: string
          read_at?: string | null
          expires_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          type?: 'trade_success' | 'trade_failed' | 'high_profit' | 'system_error' | 'config_change' | 'maintenance' | 'security_alert'
          priority?: 'low' | 'normal' | 'high' | 'critical'
          title?: string
          message?: string
          data?: Json
          read?: boolean
          sent_email?: boolean
          sent_telegram?: boolean
          sent_discord?: boolean
          created_at?: string
          read_at?: string | null
          expires_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      get_user_stats: {
        Args: {
          user_uuid: string
        }
        Returns: {
          total_trades: number
          successful_trades: number
          total_profit: number
          total_profit_usd: number
          success_rate: number
          avg_profit_per_trade: number
          total_gas_used: number
          avg_gas_per_trade: number
          best_trade_profit: number
          worst_trade_profit: number
        }[]
      }
      get_recent_opportunities: {
        Args: {
          user_uuid: string
          limit_count?: number
        }
        Returns: {
          id: string
          token_in: string
          token_out: string
          token_in_symbol: string | null
          token_out_symbol: string | null
          amount_in: number
          dex_buy: string
          dex_sell: string
          estimated_profit: number
          profit_basis_points: number
          status: string
          detected_at: string
          executed_at: string | null
        }[]
      }
      get_daily_profit_summary: {
        Args: {
          user_uuid: string
          days_back?: number
        }
        Returns: {
          date: string
          total_profit: number
          total_profit_usd: number
          trade_count: number
          success_count: number
          avg_profit: number
          gas_cost: number
        }[]
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}
