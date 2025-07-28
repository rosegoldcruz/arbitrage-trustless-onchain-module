"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Swords, 
  Crown, 
  Trophy, 
  Zap, 
  Target, 
  Shield,
  Flame,
  Star,
  Rocket,
  Bot,
  Brain,
  Eye
} from "lucide-react";
import { api } from "@/lib/api";
import { AgentRippleLoader } from "@/components/ui/RippleLoader";

interface BattleAgent {
  id: string;
  name: string;
  avatar: string;
  level: number;
  xp: number;
  maxXp: number;
  rank: number;
  wins: number;
  losses: number;
  totalProfit: number;
  winStreak: number;
  specialAbility: string;
  status: 'fighting' | 'resting' | 'training' | 'legendary';
  powerLevel: number;
  lastBattle: string;
  achievements: string[];
}

export function AgentBattleArena() {
  const [agents, setAgents] = useState<BattleAgent[]>([
    {
      id: 'atom',
      name: 'ATOM',
      avatar: '🤖',
      level: 47,
      xp: 8750,
      maxXp: 10000,
      rank: 1,
      wins: 847,
      losses: 23,
      totalProfit: 12456.78,
      winStreak: 15,
      specialAbility: 'Lightning Strike',
      status: 'fighting',
      powerLevel: 9500,
      lastBattle: '2 minutes ago',
      achievements: ['Speed Demon', 'Profit Master', 'Streak King']
    },
    {
      id: 'adom',
      name: 'ADOM',
      avatar: '🧠',
      level: 52,
      xp: 3200,
      maxXp: 12000,
      rank: 2,
      wins: 456,
      losses: 12,
      totalProfit: 18934.56,
      winStreak: 8,
      specialAbility: 'Multi-Dimensional Analysis',
      status: 'legendary',
      powerLevel: 9800,
      lastBattle: '5 minutes ago',
      achievements: ['Legendary Trader', 'Master Strategist', 'Profit Overlord']
    },
    {
      id: 'mev_sentinel',
      name: 'MEV Sentinel',
      avatar: '🛡️',
      level: 38,
      xp: 6800,
      maxXp: 8500,
      rank: 3,
      wins: 234,
      losses: 8,
      totalProfit: 7823.45,
      winStreak: 12,
      specialAbility: 'MEV Shield',
      status: 'training',
      powerLevel: 8200,
      lastBattle: '1 hour ago',
      achievements: ['Guardian', 'MEV Destroyer', 'Shield Master']
    }
  ]);

  const [battleInProgress, setBattleInProgress] = useState(false);
  const [battleLog, setBattleLog] = useState<string[]>([]);
  const [champion, setChampion] = useState<BattleAgent | null>(null);

  useEffect(() => {
    // Find current champion (highest rank)
    const currentChampion = agents.find(agent => agent.rank === 1);
    setChampion(currentChampion || null);
  }, [agents]);

  // Simulate real-time battles
  useEffect(() => {
    const interval = setInterval(() => {
      if (!battleInProgress && Math.random() > 0.7) {
        startRandomBattle();
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [battleInProgress]);

  const startRandomBattle = async () => {
    setBattleInProgress(true);
    
    const fightingAgents = agents.filter(a => a.status === 'fighting');
    if (fightingAgents.length < 2) return;

    const agent1 = fightingAgents[Math.floor(Math.random() * fightingAgents.length)];
    const agent2 = fightingAgents.filter(a => a.id !== agent1.id)[0];

    setBattleLog([
      `⚔️ BATTLE INITIATED: ${agent1.name} vs ${agent2.name}`,
      `${agent1.name} uses ${agent1.specialAbility}!`,
      `${agent2.name} counters with ${agent2.specialAbility}!`,
    ]);

    // Simulate battle duration
    await new Promise(resolve => setTimeout(resolve, 3000));

    // Determine winner based on power level + randomness
    const agent1Power = agent1.powerLevel + Math.random() * 1000;
    const agent2Power = agent2.powerLevel + Math.random() * 1000;
    const winner = agent1Power > agent2Power ? agent1 : agent2;
    const loser = winner === agent1 ? agent2 : agent1;

    // Update stats
    setAgents(prev => prev.map(agent => {
      if (agent.id === winner.id) {
        const newXp = agent.xp + 250;
        const levelUp = newXp >= agent.maxXp;
        return {
          ...agent,
          wins: agent.wins + 1,
          winStreak: agent.winStreak + 1,
          totalProfit: agent.totalProfit + Math.random() * 100 + 50,
          xp: levelUp ? newXp - agent.maxXp : newXp,
          level: levelUp ? agent.level + 1 : agent.level,
          maxXp: levelUp ? agent.maxXp + 1000 : agent.maxXp,
          powerLevel: agent.powerLevel + (levelUp ? 200 : 50),
          lastBattle: 'Just now'
        };
      } else if (agent.id === loser.id) {
        return {
          ...agent,
          losses: agent.losses + 1,
          winStreak: 0,
          lastBattle: 'Just now'
        };
      }
      return agent;
    }));

    setBattleLog(prev => [
      ...prev,
      `🏆 ${winner.name} WINS!`,
      `+250 XP, +$${(Math.random() * 100 + 50).toFixed(2)} profit`,
      `Win streak: ${winner.winStreak + 1}`
    ]);

    setBattleInProgress(false);
  };

  const getStatusColor = (status: BattleAgent['status']) => {
    switch (status) {
      case 'fighting': return 'text-red-400 bg-red-500/20';
      case 'legendary': return 'text-yellow-400 bg-yellow-500/20';
      case 'training': return 'text-blue-400 bg-blue-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Crown className="h-5 w-5 text-yellow-400" />;
      case 2: return <Trophy className="h-5 w-5 text-gray-300" />;
      case 3: return <Star className="h-5 w-5 text-orange-400" />;
      default: return <Target className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Arena Header */}
      <Card className="bg-gradient-to-r from-red-900/20 to-purple-900/20 border-red-500/30">
        <CardHeader>
          <CardTitle className="flex items-center justify-between text-white">
            <div className="flex items-center space-x-2">
              <Swords className="h-6 w-6 text-red-400" />
              <span>Agent Battle Arena</span>
              {battleInProgress && (
                <Badge className="bg-red-500/20 text-red-400 animate-pulse">
                  BATTLE IN PROGRESS
                </Badge>
              )}
            </div>
            
            {champion && (
              <div className="flex items-center space-x-2">
                <Crown className="h-5 w-5 text-yellow-400" />
                <span className="text-yellow-400">Champion: {champion.name}</span>
              </div>
            )}
          </CardTitle>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Rankings */}
        <Card className="bg-gray-900/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Leaderboard</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {agents
                .sort((a, b) => a.rank - b.rank)
                .map((agent, index) => (
                  <motion.div
                    key={agent.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-4 rounded-lg border ${
                      agent.rank === 1 
                        ? 'bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border-yellow-500/30' 
                        : 'bg-gray-800/50 border-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2">
                          {getRankIcon(agent.rank)}
                          <span className="text-2xl">{agent.avatar}</span>
                        </div>
                        <div>
                          <div className="font-semibold text-white">{agent.name}</div>
                          <div className="text-sm text-gray-400">Level {agent.level}</div>
                        </div>
                      </div>
                      
                      <Badge className={getStatusColor(agent.status)}>
                        {agent.status.toUpperCase()}
                      </Badge>
                    </div>

                    {/* XP Progress */}
                    <div className="mb-3">
                      <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>XP: {agent.xp.toLocaleString()}</span>
                        <span>{agent.maxXp.toLocaleString()}</span>
                      </div>
                      <Progress 
                        value={(agent.xp / agent.maxXp) * 100} 
                        className="h-2"
                      />
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="text-green-400 font-semibold">
                          ${agent.totalProfit.toLocaleString()}
                        </div>
                        <div className="text-gray-400 text-xs">Total Profit</div>
                      </div>
                      <div>
                        <div className="text-blue-400 font-semibold">
                          {agent.wins}-{agent.losses}
                        </div>
                        <div className="text-gray-400 text-xs">W-L Record</div>
                      </div>
                      <div>
                        <div className="text-orange-400 font-semibold">
                          {agent.winStreak}
                        </div>
                        <div className="text-gray-400 text-xs">Win Streak</div>
                      </div>
                    </div>

                    {/* Special Ability */}
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <div className="flex items-center space-x-2">
                        <Zap className="h-4 w-4 text-purple-400" />
                        <span className="text-sm text-purple-400">{agent.specialAbility}</span>
                      </div>
                    </div>

                    {/* Achievements */}
                    {agent.achievements.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {agent.achievements.slice(0, 2).map((achievement, i) => (
                          <Badge 
                            key={i} 
                            variant="outline" 
                            className="text-xs text-yellow-400 border-yellow-400/30"
                          >
                            {achievement}
                          </Badge>
                        ))}
                        {agent.achievements.length > 2 && (
                          <Badge variant="outline" className="text-xs text-gray-400">
                            +{agent.achievements.length - 2} more
                          </Badge>
                        )}
                      </div>
                    )}
                  </motion.div>
                ))}
            </div>
          </CardContent>
        </Card>

        {/* Battle Log */}
        <Card className="bg-gray-900/50 border-gray-700">
          <CardHeader>
            <CardTitle className="flex items-center text-white">
              <Eye className="h-5 w-5 mr-2 text-green-400" />
              Live Battle Feed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              <AnimatePresence mode="popLayout">
                {battleLog.map((log, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className={`p-2 rounded text-sm ${
                      log.includes('WINS') 
                        ? 'bg-green-500/20 text-green-400' 
                        : log.includes('BATTLE INITIATED')
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-gray-800/50 text-gray-300'
                    }`}
                  >
                    {log}
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {battleLog.length === 0 && !battleInProgress && (
                <div className="flex justify-center py-8">
                  <AgentRippleLoader
                    size="medium"
                    speed={0.7}
                    message="Arena Ready"
                    subMessage="Waiting for epic AI battles to begin..."
                  />
                </div>
              )}

              {battleInProgress && battleLog.length > 0 && (
                <div className="flex justify-center py-4">
                  <AgentRippleLoader
                    size="small"
                    speed={2.0}
                    message="BATTLE IN PROGRESS!"
                    subMessage="AI agents are fighting for supremacy"
                    showMessage={false}
                  />
                </div>
              )}
            </div>

            {/* Manual Battle Button */}
            <div className="mt-4 pt-4 border-t border-gray-700">
              <Button
                onClick={startRandomBattle}
                disabled={battleInProgress}
                className="w-full bg-gradient-to-r from-red-600 to-purple-600 hover:from-red-700 hover:to-purple-700"
              >
                {battleInProgress ? (
                  <>
                    <Swords className="h-4 w-4 mr-2 animate-spin" />
                    Battle in Progress...
                  </>
                ) : (
                  <>
                    <Swords className="h-4 w-4 mr-2" />
                    Start Epic Battle
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
