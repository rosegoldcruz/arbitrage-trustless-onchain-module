"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Settings, 
  Save, 
  RotateCcw, 
  Moon, 
  Sun, 
  Zap,
  Globe,
  DollarSign,
  Shield,
  Bell
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // General Settings
    theme: "dark",
    notifications: true,
    
    // Trading Settings
    minProfitThreshold: "0.01",
    maxGasPrice: "50",
    slippageTolerance: "0.5",
    defaultNetwork: "ethereum",
    
    // API Settings
    backendUrl: "https://api.aeoninvestmentstechnologies.com",
    apiKey: "",
    
    // Risk Management
    maxTradeSize: "10000",
    dailyLossLimit: "500",
    enableStopLoss: true,
  });

  const handleInputChange = (key: string, value: string | boolean) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveSettings = () => {
    // In a real app, this would save to localStorage or backend
    localStorage.setItem('atom-settings', JSON.stringify(settings));
    toast.success("Settings saved successfully!");
  };

  const resetSettings = () => {
    const defaultSettings = {
      theme: "dark",
      notifications: true,
      minProfitThreshold: "0.01",
      maxGasPrice: "50",
      slippageTolerance: "0.5",
      defaultNetwork: "ethereum",
      backendUrl: "http://localhost:8000",
      apiKey: "",
      maxTradeSize: "10000",
      dailyLossLimit: "500",
      enableStopLoss: true,
    };
    setSettings(defaultSettings);
    toast.info("Settings reset to defaults");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black">
      {/* Header */}
      <div className="border-b border-gray-800 bg-black/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center space-x-2">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-2 rounded-lg">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  ATOM
                </span>
              </Link>
              <div className="h-6 w-px bg-gray-600"></div>
              <h1 className="text-xl font-semibold text-white">Settings</h1>
            </div>
            
            <Link href="/dashboard">
              <Button variant="outline" className="border-gray-600 text-white hover:bg-gray-700">
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Settings Navigation */}
          <div className="lg:col-span-1">
            <Card className="bg-gray-900/50 border-gray-700">
              <CardHeader>
                <CardTitle className="flex items-center text-white">
                  <Settings className="h-5 w-5 mr-2" />
                  Settings
                </CardTitle>
              </CardHeader>
              <CardContent>
                <nav className="space-y-2">
                  {[
                    { id: "general", label: "General", icon: Settings },
                    { id: "trading", label: "Trading", icon: DollarSign },
                    { id: "api", label: "API", icon: Globe },
                    { id: "risk", label: "Risk Management", icon: Shield },
                    { id: "notifications", label: "Notifications", icon: Bell },
                  ].map((item) => (
                    <button
                      key={item.id}
                      className="w-full flex items-center space-x-3 px-3 py-2 text-left text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                    >
                      <item.icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </button>
                  ))}
                </nav>
              </CardContent>
            </Card>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* General Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Card className="bg-gray-900/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">General Settings</CardTitle>
                  <CardDescription className="text-gray-300">
                    Configure your general preferences
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Theme</Label>
                      <p className="text-sm text-gray-400">Choose your preferred theme</p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-gray-600 text-white hover:bg-gray-700"
                    >
                      {settings.theme === "dark" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
                      {settings.theme === "dark" ? "Dark" : "Light"}
                    </Button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Notifications</Label>
                      <p className="text-sm text-gray-400">Receive trade notifications</p>
                    </div>
                    <Button
                      variant={settings.notifications ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleInputChange("notifications", !settings.notifications)}
                      className={settings.notifications ? "bg-green-600 hover:bg-green-700" : "border-gray-600 text-white hover:bg-gray-700"}
                    >
                      {settings.notifications ? "Enabled" : "Disabled"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Trading Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="bg-gray-900/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">Trading Settings</CardTitle>
                  <CardDescription className="text-gray-300">
                    Configure your trading parameters
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="minProfit" className="text-white">Min Profit Threshold (%)</Label>
                      <Input
                        id="minProfit"
                        value={settings.minProfitThreshold}
                        onChange={(e) => handleInputChange("minProfitThreshold", e.target.value)}
                        className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                        placeholder="0.01"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="maxGas" className="text-white">Max Gas Price (gwei)</Label>
                      <Input
                        id="maxGas"
                        value={settings.maxGasPrice}
                        onChange={(e) => handleInputChange("maxGasPrice", e.target.value)}
                        className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                        placeholder="50"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="slippage" className="text-white">Slippage Tolerance (%)</Label>
                      <Input
                        id="slippage"
                        value={settings.slippageTolerance}
                        onChange={(e) => handleInputChange("slippageTolerance", e.target.value)}
                        className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                        placeholder="0.5"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="network" className="text-white">Default Network</Label>
                      <select
                        id="network"
                        value={settings.defaultNetwork}
                        onChange={(e) => handleInputChange("defaultNetwork", e.target.value)}
                        className="w-full bg-gray-800 border border-gray-600 text-white rounded-md px-3 py-2 focus:border-blue-400"
                      >
                        <option value="ethereum">Ethereum</option>
                        <option value="base">Base</option>
                        <option value="arbitrum">Arbitrum</option>
                        <option value="polygon">Polygon</option>
                      </select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* API Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Card className="bg-gray-900/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">API Settings</CardTitle>
                  <CardDescription className="text-gray-300">
                    Configure API endpoints and authentication
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="backendUrl" className="text-white">Backend URL</Label>
                    <Input
                      id="backendUrl"
                      value={settings.backendUrl}
                      onChange={(e) => handleInputChange("backendUrl", e.target.value)}
                      className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                      placeholder="http://localhost:8000"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="apiKey" className="text-white">API Key (Optional)</Label>
                    <Input
                      id="apiKey"
                      type="password"
                      value={settings.apiKey}
                      onChange={(e) => handleInputChange("apiKey", e.target.value)}
                      className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                      placeholder="Enter your API key"
                    />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Risk Management */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Card className="bg-gray-900/50 border-gray-700">
                <CardHeader>
                  <CardTitle className="text-white">Risk Management</CardTitle>
                  <CardDescription className="text-gray-300">
                    Set limits to protect your capital
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="maxTrade" className="text-white">Max Trade Size ($)</Label>
                      <Input
                        id="maxTrade"
                        value={settings.maxTradeSize}
                        onChange={(e) => handleInputChange("maxTradeSize", e.target.value)}
                        className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                        placeholder="10000"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="dailyLimit" className="text-white">Daily Loss Limit ($)</Label>
                      <Input
                        id="dailyLimit"
                        value={settings.dailyLossLimit}
                        onChange={(e) => handleInputChange("dailyLossLimit", e.target.value)}
                        className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
                        placeholder="500"
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Enable Stop Loss</Label>
                      <p className="text-sm text-gray-400">Automatically stop trading on losses</p>
                    </div>
                    <Button
                      variant={settings.enableStopLoss ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleInputChange("enableStopLoss", !settings.enableStopLoss)}
                      className={settings.enableStopLoss ? "bg-green-600 hover:bg-green-700" : "border-gray-600 text-white hover:bg-gray-700"}
                    >
                      {settings.enableStopLoss ? "Enabled" : "Disabled"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Action Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="flex space-x-4"
            >
              <Button
                onClick={saveSettings}
                className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700"
              >
                <Save className="mr-2 h-4 w-4" />
                Save Settings
              </Button>
              
              <Button
                onClick={resetSettings}
                variant="outline"
                className="border-gray-600 text-white hover:bg-gray-700"
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Reset to Defaults
              </Button>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
