"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2, ArrowUpDown, Zap, TrendingUp, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { zeroXAPI, SwapQuote, TokenInfo } from "@/lib/0x-api";

interface ZeroXSwapPanelProps {
  className?: string;
}

export function ZeroXSwapPanel({ className }: ZeroXSwapPanelProps) {
  const [sellToken, setSellToken] = useState<string>('ETH');
  const [buyToken, setBuyToken] = useState<string>('USDC');
  const [sellAmount, setSellAmount] = useState<string>('');
  const [quote, setQuote] = useState<SwapQuote | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [tokens, setTokens] = useState<TokenInfo[]>([]);
  const [apiKeyValid, setApiKeyValid] = useState<boolean>(false);

  // Load supported tokens on component mount
  useEffect(() => {
    const loadTokens = async () => {
      try {
        const supportedTokens = await zeroXAPI.getSupportedTokens(1); // Ethereum mainnet
        setTokens(supportedTokens.slice(0, 20)); // Limit to first 20 tokens
        
        // Validate API key
        const isValid = await zeroXAPI.validateApiKey();
        setApiKeyValid(isValid);
        
        if (!isValid) {
          toast.error('0x.org API key not configured or invalid');
        }
      } catch (error) {
        console.error('Error loading tokens:', error);
        toast.error('Failed to load supported tokens');
      }
    };

    loadTokens();
  }, []);

  const handleGetQuote = async () => {
    if (!sellAmount || parseFloat(sellAmount) <= 0) {
      toast.error('Please enter a valid sell amount');
      return;
    }

    if (!apiKeyValid) {
      toast.error('0x.org API key not configured');
      return;
    }

    setLoading(true);
    setQuote(null);

    try {
      // Convert amount to wei (assuming 18 decimals for simplicity)
      const sellAmountWei = (parseFloat(sellAmount) * Math.pow(10, 18)).toString();

      const quoteData = await zeroXAPI.getSwapQuote({
        sellToken,
        buyToken,
        sellAmount: sellAmountWei,
        slippagePercentage: 0.01, // 1% slippage
        skipValidation: true,
      });

      if (quoteData) {
        setQuote(quoteData);
        toast.success('Quote retrieved successfully!');
      } else {
        toast.error('Failed to get quote');
      }
    } catch (error) {
      console.error('Error getting quote:', error);
      toast.error('Failed to get swap quote');
    } finally {
      setLoading(false);
    }
  };

  const handleSwapTokens = () => {
    const temp = sellToken;
    setSellToken(buyToken);
    setBuyToken(temp);
    setQuote(null);
  };

  const formatAmount = (amount: string, decimals: number = 18): string => {
    const num = parseFloat(amount) / Math.pow(10, decimals);
    return num.toFixed(6);
  };

  const calculatePriceImpact = (): string => {
    if (!quote) return '0.00';
    
    const price = parseFloat(quote.price);
    const guaranteedPrice = parseFloat(quote.guaranteedPrice);
    const impact = ((price - guaranteedPrice) / price) * 100;
    
    return Math.abs(impact).toFixed(2);
  };

  return (
    <Card className={`bg-gray-900/50 border-gray-800 ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-blue-400" />
          0x.org Swap Integration
        </CardTitle>
        <CardDescription>
          Get quotes and execute swaps using 0x.org protocol
        </CardDescription>
        {!apiKeyValid && (
          <Badge variant="destructive" className="w-fit">
            <AlertCircle className="h-3 w-3 mr-1" />
            API Key Required
          </Badge>
        )}
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Swap Interface */}
        <div className="space-y-4">
          {/* Sell Token */}
          <div className="space-y-2">
            <Label htmlFor="sellToken">Sell</Label>
            <div className="flex gap-2">
              <Select value={sellToken} onValueChange={setSellToken}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ETH">ETH</SelectItem>
                  <SelectItem value="USDC">USDC</SelectItem>
                  <SelectItem value="USDT">USDT</SelectItem>
                  <SelectItem value="WBTC">WBTC</SelectItem>
                  <SelectItem value="DAI">DAI</SelectItem>
                  {tokens.map((token) => (
                    <SelectItem key={token.address} value={token.symbol}>
                      {token.symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                id="sellAmount"
                type="number"
                placeholder="0.0"
                value={sellAmount}
                onChange={(e) => setSellAmount(e.target.value)}
                className="flex-1"
              />
            </div>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSwapTokens}
              className="rounded-full p-2"
            >
              <ArrowUpDown className="h-4 w-4" />
            </Button>
          </div>

          {/* Buy Token */}
          <div className="space-y-2">
            <Label htmlFor="buyToken">Buy</Label>
            <div className="flex gap-2">
              <Select value={buyToken} onValueChange={setBuyToken}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ETH">ETH</SelectItem>
                  <SelectItem value="USDC">USDC</SelectItem>
                  <SelectItem value="USDT">USDT</SelectItem>
                  <SelectItem value="WBTC">WBTC</SelectItem>
                  <SelectItem value="DAI">DAI</SelectItem>
                  {tokens.map((token) => (
                    <SelectItem key={token.address} value={token.symbol}>
                      {token.symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                readOnly
                placeholder="0.0"
                value={quote ? formatAmount(quote.buyAmount) : ''}
                className="flex-1 bg-gray-800"
              />
            </div>
          </div>

          {/* Get Quote Button */}
          <Button
            onClick={handleGetQuote}
            disabled={loading || !apiKeyValid}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Getting Quote...
              </>
            ) : (
              'Get Quote'
            )}
          </Button>
        </div>

        {/* Quote Details */}
        {quote && (
          <div className="space-y-4 p-4 bg-gray-800/50 rounded-lg">
            <h4 className="font-semibold flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-400" />
              Quote Details
            </h4>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Price:</span>
                <div className="font-mono">{parseFloat(quote.price).toFixed(6)}</div>
              </div>
              
              <div>
                <span className="text-gray-400">Guaranteed Price:</span>
                <div className="font-mono">{parseFloat(quote.guaranteedPrice).toFixed(6)}</div>
              </div>
              
              <div>
                <span className="text-gray-400">Price Impact:</span>
                <div className="font-mono text-yellow-400">{calculatePriceImpact()}%</div>
              </div>
              
              <div>
                <span className="text-gray-400">Gas Estimate:</span>
                <div className="font-mono">{parseInt(quote.gas).toLocaleString()}</div>
              </div>
              
              <div>
                <span className="text-gray-400">Protocol Fee:</span>
                <div className="font-mono">{formatAmount(quote.protocolFee)} ETH</div>
              </div>
              
              <div>
                <span className="text-gray-400">Sources:</span>
                <div className="text-xs">
                  {quote.sources.slice(0, 3).map((source, index) => (
                    <Badge key={index} variant="secondary" className="mr-1 text-xs">
                      {source.name}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>

            {/* Execute Swap Button (Placeholder) */}
            <Button
              variant="outline"
              className="w-full"
              disabled
            >
              Execute Swap (Coming Soon)
            </Button>
          </div>
        )}

        {/* API Status */}
        <div className="text-xs text-gray-500 text-center">
          API Status: {apiKeyValid ? (
            <span className="text-green-400">Connected</span>
          ) : (
            <span className="text-red-400">Not Connected</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
