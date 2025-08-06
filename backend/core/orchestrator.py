# backend/core/orchestrator.py

class MasterOrchestrator:
    def __init__(self):
        self.agents = [{"id": 1}]
    
    def initialize_agents(self):
        return

    def get_system_status(self):
        return {
            "global_metrics": {
                "active_agents": 1,
                "total_operations": 10,
                "system_uptime": 99.9,
                "total_profit": 0.0
            }
        }

# Singleton instance
master_orchestrator = MasterOrchestrator()
