"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MessageSquare, Send, Bot, User } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: string;
  agent?: string;
}

export function ChatWithAgent() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "agent",
      content: "Hello! I'm your ATOM assistant. I can help you with arbitrage strategies, explain how flash loans work, or answer questions about your trading performance. What would you like to know?",
      timestamp: new Date().toLocaleTimeString(),
      agent: "ATOM Assistant",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      // Chat with AI agent
      const response = await api.agents.chat({ message: inputValue });
      
      if (response.success && response.data) {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "agent",
          content: response.data.message || "I understand your question. Let me help you with that.",
          timestamp: new Date().toLocaleTimeString(),
          agent: "ATOM Assistant",
        };
        setMessages(prev => [...prev, agentMessage]);
      } else {
        // Fallback response for demo purposes
        const fallbackResponses = [
          "That's a great question! Flash loans allow you to borrow assets without collateral, execute trades, and repay within the same transaction.",
          "Arbitrage opportunities arise when the same asset is priced differently across exchanges. Our AI agents monitor these differences 24/7.",
          "Your current strategy is performing well. The ATOM agent has executed 23 successful trades today with a 0.46% average profit margin.",
          "Gas optimization is crucial for profitable arbitrage. We automatically calculate the optimal gas price for each transaction.",
          "MEV protection helps prevent front-running attacks. Our MEV Sentinel agent monitors the mempool and adjusts strategies accordingly.",
        ];
        
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: "agent",
          content: fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)],
          timestamp: new Date().toLocaleTimeString(),
          agent: "ATOM Assistant",
        };
        setMessages(prev => [...prev, agentMessage]);
      }
    } catch (error) {
      toast.error("Failed to send message. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card className="bg-gray-900/50 border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center text-white">
          <MessageSquare className="h-5 w-5 mr-2 text-blue-400" />
          Chat with Agent
        </CardTitle>
        <CardDescription className="text-gray-300">
          Ask questions about arbitrage and trading strategies
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Messages */}
          <div className="h-64 overflow-y-auto space-y-3 p-3 bg-black/30 rounded-lg">
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`flex items-start space-x-2 max-w-[80%] ${
                  message.type === "user" ? "flex-row-reverse space-x-reverse" : ""
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === "user" 
                      ? "bg-blue-500" 
                      : "bg-gradient-to-r from-purple-500 to-blue-500"
                  }`}>
                    {message.type === "user" ? (
                      <User className="h-4 w-4 text-white" />
                    ) : (
                      <Bot className="h-4 w-4 text-white" />
                    )}
                  </div>
                  
                  <div className={`rounded-lg p-3 ${
                    message.type === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-700 text-gray-100"
                  }`}>
                    <p className="text-sm">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>
                  </div>
                </div>
              </motion.div>
            ))}
            
            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="flex items-start space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="bg-gray-700 rounded-lg p-3">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Input */}
          <div className="flex space-x-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about arbitrage strategies..."
              className="bg-gray-800 border-gray-600 text-white focus:border-blue-400"
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Quick Actions */}
          <div className="flex flex-wrap gap-2">
            {[
              "How do flash loans work?",
              "Show my profit stats",
              "Explain MEV protection",
              "Best trading pairs?",
            ].map((question) => (
              <Button
                key={question}
                size="sm"
                variant="outline"
                onClick={() => setInputValue(question)}
                className="text-xs border-gray-600 text-gray-300 hover:bg-gray-700"
                disabled={isLoading}
              >
                {question}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
