#!/usr/bin/env python3
"""
Example of how bots should implement communication with the orchestrator
This shows the file-based communication protocol
"""

import json
import time
import os
from pathlib import Path

class BotCommunicationInterface:
    """
    Interface for bot communication with orchestrator
    Bots should implement this pattern for coordination
    """
    
    def __init__(self, bot_name: str):
        self.bot_name = bot_name.upper()
        self.comm_dir = Path("comm")
        self.commands_dir = self.comm_dir / "commands"
        self.results_dir = self.comm_dir / "results"
        self.heartbeats_dir = self.comm_dir / "heartbeats"
        
        # Ensure directories exist
        for directory in [self.commands_dir, self.results_dir, self.heartbeats_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.command_file = self.commands_dir / f"{bot_name.lower()}_command.json"
        self.result_file = self.results_dir / f"{bot_name.lower()}_result.json"
        self.heartbeat_file = self.heartbeats_dir / f"{bot_name.lower()}_heartbeat.json"
        
        print(f"🔗 {self.bot_name} communication interface initialized")

    def send_heartbeat(self, status: str = "running", metrics: dict = None):
        """Send heartbeat to orchestrator"""
        if metrics is None:
            metrics = {}
        
        heartbeat_data = {
            "bot_name": self.bot_name,
            "status": status,
            "timestamp": time.time(),
            "pid": os.getpid(),
            "metrics": metrics
        }
        
        try:
            with open(self.heartbeat_file, 'w') as f:
                json.dump(heartbeat_data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to send heartbeat: {e}")

    def check_for_commands(self) -> dict:
        """Check for commands from orchestrator"""
        if not self.command_file.exists():
            return None
        
        try:
            with open(self.command_file, 'r') as f:
                command_data = json.load(f)
            
            # Remove command file after reading
            os.remove(self.command_file)
            
            print(f"📨 Received command: {command_data.get('command', 'unknown')}")
            return command_data
            
        except Exception as e:
            print(f"❌ Failed to read command: {e}")
            return None

    def send_result(self, success: bool, data: dict = None, error: str = None):
        """Send execution result to orchestrator"""
        if data is None:
            data = {}
        
        result_data = {
            "bot_name": self.bot_name,
            "success": success,
            "timestamp": time.time(),
            "data": data,
            "error": error
        }
        
        try:
            with open(self.result_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            print(f"📤 Result sent: {'✅ Success' if success else '❌ Failed'}")
            
        except Exception as e:
            print(f"❌ Failed to send result: {e}")

    def execute_arbitrage_command(self, command_data: dict):
        """
        Example implementation of arbitrage execution
        Bots should implement their own version of this
        """
        try:
            opportunity = command_data.get('opportunity', {})
            
            print(f"🎯 Executing arbitrage:")
            print(f"   Tokens: {opportunity.get('token_a')} → {opportunity.get('token_b')} → {opportunity.get('token_c')}")
            print(f"   Expected profit: ${opportunity.get('net_profit_usd', 0):.2f}")
            print(f"   Spread: {opportunity.get('spread_bps', 0)} bps")
            
            # Simulate execution (replace with real bot logic)
            execution_time = 2.0  # seconds
            time.sleep(execution_time)
            
            # Simulate success/failure (replace with real execution result)
            import random
            success = random.random() > 0.2  # 80% success rate
            
            if success:
                actual_profit = opportunity.get('net_profit_usd', 0) * random.uniform(0.8, 1.2)
                self.send_result(
                    success=True,
                    data={
                        "profit": actual_profit,
                        "execution_time": execution_time,
                        "tx_hash": f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
                    }
                )
            else:
                self.send_result(
                    success=False,
                    error="Slippage too high"
                )
                
        except Exception as e:
            self.send_result(
                success=False,
                error=str(e)
            )

def example_bot_main_loop():
    """
    Example main loop for a bot
    Shows how to integrate with orchestrator communication
    """
    bot_name = "EXAMPLE"
    comm = BotCommunicationInterface(bot_name)
    
    print(f"🚀 Starting {bot_name} bot with orchestrator communication")
    
    try:
        while True:
            # Send heartbeat
            comm.send_heartbeat(
                status="running",
                metrics={
                    "uptime": time.time(),
                    "memory_usage": "50MB",
                    "opportunities_processed": 42
                }
            )
            
            # Check for commands
            command = comm.check_for_commands()
            if command:
                command_type = command.get('command')
                
                if command_type == "execute_arbitrage":
                    comm.execute_arbitrage_command(command)
                elif command_type == "status_request":
                    # Send status update
                    comm.send_result(
                        success=True,
                        data={
                            "status": "healthy",
                            "last_execution": time.time() - 300,
                            "success_rate": 0.85
                        }
                    )
                else:
                    print(f"⚠️ Unknown command: {command_type}")
            
            # Bot's main work (scanning, analysis, etc.)
            time.sleep(5)  # Check for commands every 5 seconds
            
    except KeyboardInterrupt:
        print(f"🛑 {bot_name} bot stopping...")
        comm.send_heartbeat(status="stopping")

if __name__ == "__main__":
    example_bot_main_loop()
