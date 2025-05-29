#!/usr/bin/env python3
"""
JAH Agency - Main Application Entry Point
=========================================

This is the main entry point for the JAH Agency autonomous business system.
It initializes all components, starts the primary agent, and coordinates
the entire autonomous operation.

Usage:
    python main.py [options]
    python -m jah_agency [options]

Options:
    --config-file PATH    Configuration file path (default: config/config.yaml)
    --mode MODE          Operation mode: autonomous, interactive, debug (default: autonomous)
    --log-level LEVEL    Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
    --daemon             Run as daemon process
    --version            Show version information
    --help               Show this help message

Example:
    python main.py --config-file config/production.yaml --mode autonomous --daemon

Author: JAHA Development Team
Version: 2.0.0
License: MIT
"""

import sys
import os
import argparse
import logging
import asyncio
import signal
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import JAH Agency components
from jah_agency.primary_agent import PrimaryJAHAgent
from jah_agency.financial_system import FinancialSystem
from jah_agency.revenue_generation import RevenueGenerationSystem
from jah_agency.task_distribution import TaskDistributionEngine
from jah_agency.communication import CommunicationFramework
from jah_agency.quality_assurance import QualityAssuranceSystem
from jah_agency.specialized_agents import AgentManager

# Configure logging
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
    )
    
    # Create main logger
    logger = logging.getLogger('JAHAgency')
    logger.setLevel(getattr(logging, level.upper()))
    
    # File handler for all logs
    file_handler = logging.FileHandler(f'logs/jah_agency_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    # Error file handler for ERROR and CRITICAL
    error_handler = logging.FileHandler(f'logs/jah_agency_errors_{datetime.now().strftime("%Y%m%d")}.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def load_configuration(config_file: str) -> Dict[str, Any]:
    """Load and validate configuration from YAML file"""
    
    config_path = Path(config_file)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required configuration sections
        required_sections = [
            'primary_agent',
            'financial_system', 
            'revenue_generation',
            'specialized_agents',
            'database',
            'security'
        ]
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        return config
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML configuration: {e}")


class JAHAgencySystem:
    """Main JAH Agency System Coordinator"""
    
    def __init__(self, config: Dict[str, Any], mode: str = "autonomous"):
        self.config = config
        self.mode = mode
        self.logger = logging.getLogger('JAHAgency.System')
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Initialize core components
        self.primary_agent: Optional[PrimaryJAHAgent] = None
        self.financial_system: Optional[FinancialSystem] = None
        self.revenue_system: Optional[RevenueGenerationSystem] = None
        self.task_engine: Optional[TaskDistributionEngine] = None
        self.communication: Optional[CommunicationFramework] = None
        self.quality_assurance: Optional[QualityAssuranceSystem] = None
        self.agent_manager: Optional[AgentManager] = None
    
    async def initialize_system(self):
        """Initialize all JAH Agency components"""
        
        self.logger.info("Initializing JAH Agency System...")
        
        try:
            # Initialize Communication Framework first (other components depend on it)
            self.logger.info("Initializing Communication Framework...")
            self.communication = CommunicationFramework(self.config['communication'])
            await self.communication.initialize()
            
            # Initialize Financial System
            self.logger.info("Initializing Financial System...")
            self.financial_system = FinancialSystem(
                config=self.config['financial_system'],
                communication=self.communication
            )
            await self.financial_system.initialize()
            
            # Initialize Task Distribution Engine
            self.logger.info("Initializing Task Distribution Engine...")
            self.task_engine = TaskDistributionEngine(
                config=self.config['task_distribution'],
                communication=self.communication
            )
            await self.task_engine.initialize()
            
            # Initialize Quality Assurance System
            self.logger.info("Initializing Quality Assurance System...")
            self.quality_assurance = QualityAssuranceSystem(
                config=self.config['quality_assurance'],
                communication=self.communication
            )
            await self.quality_assurance.initialize()
            
            # Initialize Agent Manager
            self.logger.info("Initializing Specialized Agent Manager...")
            self.agent_manager = AgentManager(
                config=self.config['specialized_agents'],
                communication=self.communication,
                task_engine=self.task_engine,
                quality_assurance=self.quality_assurance
            )
            await self.agent_manager.initialize()
            
            # Initialize Revenue Generation System
            self.logger.info("Initializing Revenue Generation System...")
            self.revenue_system = RevenueGenerationSystem(
                config=self.config['revenue_generation'],
                communication=self.communication,
                financial_system=self.financial_system,
                agent_manager=self.agent_manager
            )
            await self.revenue_system.initialize()
            
            # Initialize Primary JAH Agent (CEO)
            self.logger.info("Initializing Primary JAH Agent...")
            self.primary_agent = PrimaryJAHAgent(
                config=self.config['primary_agent'],
                financial_system=self.financial_system,
                revenue_system=self.revenue_system,
                task_engine=self.task_engine,
                communication=self.communication,
                quality_assurance=self.quality_assurance,
                agent_manager=self.agent_manager
            )
            await self.primary_agent.initialize()
            
            self.logger.info("✅ JAH Agency System initialization complete!")
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}", exc_info=True)
            raise
    
    async def start_system(self):
        """Start the JAH Agency autonomous operations"""
        
        if self.is_running:
            self.logger.warning("System is already running")
            return
        
        self.logger.info(f"🚀 Starting JAH Agency in {self.mode} mode...")
        
        try:
            # Start all subsystems
            await asyncio.gather(
                self.communication.start(),
                self.financial_system.start(),
                self.task_engine.start(),
                self.quality_assurance.start(),
                self.agent_manager.start(),
                self.revenue_system.start(),
                self.primary_agent.start()
            )
            
            self.is_running = True
            self.logger.info("✅ JAH Agency System is now operational!")
            
            # Print system status
            await self.display_system_status()
            
            if self.mode == "autonomous":
                self.logger.info("🤖 Entering autonomous operation mode...")
                await self.autonomous_operation_loop()
            elif self.mode == "interactive":
                self.logger.info("👤 Entering interactive mode...") 
                await self.interactive_mode()
            elif self.mode == "debug":
                self.logger.info("🔧 Entering debug mode...")
                await self.debug_mode()
            
        except Exception as e:
            self.logger.error(f"❌ System startup failed: {e}", exc_info=True)
            await self.shutdown_system()
            raise
    
    async def autonomous_operation_loop(self):
        """Main autonomous operation loop"""
        
        self.logger.info("Starting autonomous operation loop...")
        
        try:
            while not self.shutdown_event.is_set():
                # Let the Primary Agent handle autonomous decisions
                await self.primary_agent.autonomous_cycle()
                
                # Wait before next cycle (configurable interval)
                cycle_interval = self.config.get('operation_cycle_seconds', 60)
                await asyncio.sleep(cycle_interval)
                
        except asyncio.CancelledError:
            self.logger.info("Autonomous operation loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in autonomous operation: {e}", exc_info=True)
            raise
    
    async def interactive_mode(self):
        """Interactive mode for manual control and monitoring"""
        
        self.logger.info("Entering interactive mode. Type 'help' for commands.")
        
        while not self.shutdown_event.is_set():
            try:
                command = await self.get_user_input("JAH> ")
                await self.process_interactive_command(command)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
    
    async def debug_mode(self):
        """Debug mode for development and troubleshooting"""
        
        self.logger.info("Debug mode activated. Enhanced logging enabled.")
        
        # Enable debug logging for all components
        logging.getLogger().setLevel(logging.DEBUG)
        
        # Run system diagnostics
        await self.run_system_diagnostics()
        
        # Enter interactive mode for debugging
        await self.interactive_mode()
    
    async def display_system_status(self):
        """Display comprehensive system status"""
        
        if not self.primary_agent:
            return
        
        status = await self.primary_agent.get_system_status()
        
        print("\n" + "="*50)
        print("  JAH AGENCY SYSTEM STATUS")
        print("="*50)
        print(f"Active Agents: {status.active_agents}")
        print(f"Daily Revenue: ${status.daily_revenue:,.2f}")
        print(f"Completed Tasks: {status.completed_tasks}")
        print(f"Pending Tasks: {status.pending_tasks}")
        print(f"System Uptime: {status.system_uptime:.2f} hours")
        print(f"Success Rate: {status.success_rate:.1f}%")
        print(f"Error Count: {status.error_count}")
        print("="*50 + "\n")
    
    async def shutdown_system(self):
        """Gracefully shutdown all JAH Agency components"""
        
        if not self.is_running:
            return
        
        self.logger.info("🛑 Initiating graceful system shutdown...")
        
        self.shutdown_event.set()
        self.is_running = False
        
        try:
            # Shutdown components in reverse order
            if self.primary_agent:
                await self.primary_agent.shutdown()
            
            if self.revenue_system:
                await self.revenue_system.shutdown()
            
            if self.agent_manager:
                await self.agent_manager.shutdown()
            
            if self.quality_assurance:
                await self.quality_assurance.shutdown()
            
            if self.task_engine:
                await self.task_engine.shutdown()
            
            if self.financial_system:
                await self.financial_system.shutdown()
            
            if self.communication:
                await self.communication.shutdown()
            
            self.logger.info("✅ JAH Agency System shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
    
    async def get_user_input(self, prompt: str) -> str:
        """Get user input asynchronously"""
        return input(prompt)
    
    async def process_interactive_command(self, command: str):
        """Process interactive commands"""
        
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        if cmd == "help":
            print("""
Available Commands:
  status          - Show system status
  agents          - List active agents  
  tasks           - Show task queue
  revenue         - Show revenue report
  performance     - Show performance metrics
  shutdown        - Shutdown system
  help            - Show this help
            """)
        elif cmd == "status":
            await self.display_system_status()
        elif cmd == "agents":
            await self.show_active_agents()
        elif cmd == "tasks":
            await self.show_task_queue()
        elif cmd == "revenue":
            await self.show_revenue_report()
        elif cmd == "performance":
            await self.show_performance_metrics()
        elif cmd == "shutdown":
            await self.shutdown_system()
            return
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")
    
    async def show_active_agents(self):
        """Display active agents information"""
        if self.agent_manager:
            agents = await self.agent_manager.get_active_agents()
            print(f"\nActive Agents ({len(agents)}):")
            for agent in agents:
                print(f"  - {agent.agent_id} ({agent.agent_type}) - {agent.status}")
    
    async def show_task_queue(self):
        """Display current task queue"""
        if self.task_engine:
            tasks = await self.task_engine.get_pending_tasks()
            print(f"\nPending Tasks ({len(tasks)}):")
            for task in tasks[:10]:  # Show top 10
                print(f"  - {task.task_id}: {task.task_type} (Priority: {task.priority.name})")
    
    async def show_revenue_report(self):
        """Display revenue report"""
        if self.financial_system:
            report = await self.financial_system.generate_daily_report()
            print(f"\nDaily Revenue Report:")
            print(f"  Total Revenue: ${report.total_revenue:,.2f}")
            print(f"  Operating Expenses: ${report.operating_expenses:,.2f}")
            print(f"  Net Profit: ${report.net_profit:,.2f}")
    
    async def show_performance_metrics(self):
        """Display performance metrics"""
        if self.quality_assurance:
            metrics = await self.quality_assurance.get_performance_metrics()
            print(f"\nPerformance Metrics:")
            print(f"  Task Completion Rate: {metrics.completion_rate:.1f}%")
            print(f"  Average Response Time: {metrics.avg_response_time:.2f}s")
            print(f"  Quality Score: {metrics.quality_score:.1f}/100")
    
    async def run_system_diagnostics(self):
        """Run comprehensive system diagnostics"""
        
        self.logger.info("Running system diagnostics...")
        
        # Component health checks
        components = [
            ("Communication", self.communication),
            ("Financial System", self.financial_system),
            ("Task Engine", self.task_engine),
            ("Quality Assurance", self.quality_assurance),
            ("Agent Manager", self.agent_manager),
            ("Revenue System", self.revenue_system),
            ("Primary Agent", self.primary_agent)
        ]
        
        for name, component in components:
            if component:
                try:
                    health = await component.health_check()
                    status = "✅ HEALTHY" if health else "❌ UNHEALTHY"
                    self.logger.info(f"{name}: {status}")
                except Exception as e:
                    self.logger.error(f"{name}: ❌ ERROR - {e}")
            else:
                self.logger.warning(f"{name}: ⚠️ NOT INITIALIZED")


def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(
        description="JAH Agency - Autonomous AI Business Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Start with default config
  python main.py --mode interactive                 # Start in interactive mode  
  python main.py --config-file config/prod.yaml    # Use production config
  python main.py --daemon --log-level WARNING      # Run as daemon with warnings only
        """
    )
    
    parser.add_argument(
        '--config-file',
        default='config/config.yaml',
        help='Configuration file path (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--mode',
        choices=['autonomous', 'interactive', 'debug'],
        default='autonomous',
        help='Operation mode (default: autonomous)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon process'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='JAH Agency v2.0.0'
    )
    
    return parser.parse_args()


async def main():
    """Main application entry point"""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Load configuration
    try:
        config = load_configuration(args.config_file)
        logger.info(f"Configuration loaded from: {args.config_file}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Initialize JAH Agency System
    system = JAHAgencySystem(config, args.mode)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(system.shutdown_system())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize and start the system
        await system.initialize_system()
        await system.start_system()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Critical system error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await system.shutdown_system()


if __name__ == "__main__":
    """Entry point when run as script"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    JAH AGENCY SYSTEM                         ║
    ║              Autonomous AI Business Management               ║
    ║                        Version 2.0.0                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested. Goodbye!")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        sys.exit(1)