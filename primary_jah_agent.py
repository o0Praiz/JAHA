# JAH Agency - Primary JAH Agent (CEO)
# Version 1.0 | Central Command and Coordination Hub

import asyncio
import json
import logging
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Import base agent framework (would be from separate module in production)
from jah_base_agent import (
    BaseAgent, Task, TaskResult, TaskStatus, AgentStatus, 
    CapabilitySet, PerformanceMetrics, CommunicationMessage, MessagePriority
)

class TaskComplexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentType(Enum):
    MARKETING = "marketing"
    SALES = "sales"
    TECHNICAL = "technical"
    RESEARCH = "research"
    CUSTOMER_SERVICE = "customer_service"
    FINANCIAL = "financial"
    CREATIVE = "creative"
    CONSULTING = "consulting"
    GENERAL = "general"

@dataclass
class AgentRegistration:
    agent_id: str
    agent_type: str
    capabilities: List[str]
    status: AgentStatus
    performance_metrics: Dict[str, Any]
    registration_time: datetime
    last_heartbeat: datetime
    current_tasks: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 3

@dataclass
class TaskAssignment:
    task_id: str
    agent_id: str
    assignment_time: datetime
    estimated_completion: datetime
    confidence_score: float
    assignment_reasoning: str

@dataclass
class SystemMetrics:
    total_tasks_processed: int = 0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    active_agents: int = 0
    system_efficiency: float = 0.0
    average_task_completion_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class TaskAnalysisEngine:
    """Analyzes incoming tasks and determines optimal assignment strategies"""
    
    def __init__(self):
        self.complexity_keywords = {
            'low': ['simple', 'basic', 'quick', 'straightforward'],
            'medium': ['moderate', 'standard', 'typical', 'regular'],
            'high': ['complex', 'advanced', 'detailed', 'comprehensive'],
            'critical': ['urgent', 'critical', 'emergency', 'priority']
        }
        
    def analyze_task_complexity(self, task: Task) -> TaskComplexity:
        """Analyze task complexity based on description and requirements"""
        try:
            description_lower = task.description.lower()
            title_lower = task.title.lower()
            
            complexity_scores = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            
            # Analyze description for complexity keywords
            for complexity, keywords in self.complexity_keywords.items():
                for keyword in keywords:
                    if keyword in description_lower or keyword in title_lower:
                        complexity_scores[complexity] += 1
            
            # Consider task requirements
            if task.requirements:
                if task.requirements.get('advanced_skills', False):
                    complexity_scores['high'] += 2
                if task.requirements.get('multiple_agents', False):
                    complexity_scores['high'] += 1
                if task.requirements.get('external_integration', False):
                    complexity_scores['medium'] += 1
            
            # Consider deadline urgency
            if task.deadline:
                time_to_deadline = (task.deadline - datetime.now()).total_seconds() / 3600
                if time_to_deadline < 2:  # Less than 2 hours
                    complexity_scores['critical'] += 2
                elif time_to_deadline < 24:  # Less than 24 hours
                    complexity_scores['high'] += 1
            
            # Determine final complexity
            max_score = max(complexity_scores.values())
            if max_score == 0:
                return TaskComplexity.MEDIUM  # Default
            
            for complexity, score in complexity_scores.items():
                if score == max_score:
                    return TaskComplexity(complexity)
                    
        except Exception as e:
            logging.error(f"Error analyzing task complexity: {str(e)}")
            return TaskComplexity.MEDIUM
    
    def determine_required_capabilities(self, task: Task) -> List[str]:
        """Determine what capabilities are needed for task completion"""
        required_caps = []
        
        task_type_mapping = {
            'content_creation': ['content_creation', 'writing', 'creativity'],
            'data_analysis': ['data_analysis', 'statistics', 'visualization'],
            'software_development': ['programming', 'system_design', 'testing'],
            'market_research': ['research', 'analysis', 'report_generation'],
            'customer_support': ['communication', 'problem_solving', 'empathy'],
            'financial_analysis': ['financial_modeling', 'accounting', 'forecasting'],
            'marketing_campaign': ['marketing', 'creativity', 'analytics'],
            'sales_support': ['sales', 'communication', 'persuasion']
        }
        
        # Map task type to capabilities
        if task.task_type in task_type_mapping:
            required_caps.extend(task_type_mapping[task.task_type])
        
        # Extract from requirements
        if task.requirements and 'required_capabilities' in task.requirements:
            required_caps.extend(task.requirements['required_capabilities'])
        
        return list(set(required_caps))  # Remove duplicates
    
    def calculate_priority_score(self, task: Task, complexity: TaskComplexity) -> int:
        """Calculate dynamic priority score for task"""
        base_score = task.priority_score or 50
        
        # Complexity adjustment
        complexity_multipliers = {
            TaskComplexity.LOW: 0.8,
            TaskComplexity.MEDIUM: 1.0,
            TaskComplexity.HIGH: 1.2,
            TaskComplexity.CRITICAL: 1.5
        }
        
        score = base_score * complexity_multipliers[complexity]
        
        # Revenue potential adjustment
        if task.revenue_potential > 0:
            revenue_factor = min(task.revenue_potential / 1000, 2.0)  # Cap at 2x
            score *= (1 + revenue_factor * 0.5)
        
        # Deadline urgency adjustment
        if task.deadline:
            time_to_deadline = (task.deadline - datetime.now()).total_seconds() / 3600
            if time_to_deadline < 1:
                score *= 2.0
            elif time_to_deadline < 4:
                score *= 1.5
            elif time_to_deadline < 24:
                score *= 1.2
        
        return int(min(score, 100))  # Cap at 100

class AgentManagementSystem:
    """Manages the lifecycle and coordination of all sub-agents"""
    
    def __init__(self):
        self.registered_agents: Dict[str, AgentRegistration] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.agent_performance_history: Dict[str, List[Dict]] = defaultdict(list)
        self.lock = threading.Lock()
        
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]) -> bool:
        """Register a new agent with the system"""
        try:
            with self.lock:
                registration = AgentRegistration(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    capabilities=capabilities,
                    status=AgentStatus.IDLE,
                    performance_metrics={},
                    registration_time=datetime.now(),
                    last_heartbeat=datetime.now()
                )
                
                self.registered_agents[agent_id] = registration
                self.agent_capabilities[agent_id] = capabilities
                
                logging.info(f"Agent {agent_id} registered successfully")
                return True
                
        except Exception as e:
            logging.error(f"Error registering agent {agent_id}: {str(e)}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the system"""
        try:
            with self.lock:
                if agent_id in self.registered_agents:
                    del self.registered_agents[agent_id]
                    if agent_id in self.agent_capabilities:
                        del self.agent_capabilities[agent_id]
                    logging.info(f"Agent {agent_id} unregistered")
                    return True
                return False
        except Exception as e:
            logging.error(f"Error unregistering agent {agent_id}: {str(e)}")
            return False
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, 
                          performance_metrics: Optional[Dict] = None) -> None:
        """Update agent status and performance metrics"""
        try:
            with self.lock:
                if agent_id in self.registered_agents:
                    self.registered_agents[agent_id].status = status
                    self.registered_agents[agent_id].last_heartbeat = datetime.now()
                    
                    if performance_metrics:
                        self.registered_agents[agent_id].performance_metrics = performance_metrics
                        # Store performance history
                        self.agent_performance_history[agent_id].append({
                            'timestamp': datetime.now(),
                            'metrics': performance_metrics.copy()
                        })
                        
                        # Keep only last 100 entries
                        if len(self.agent_performance_history[agent_id]) > 100:
                            self.agent_performance_history[agent_id] = \
                                self.agent_performance_history[agent_id][-100:]
                                
        except Exception as e:
            logging.error(f"Error updating agent status: {str(e)}")
    
    def find_best_agent_for_task(self, task: Task, required_capabilities: List[str]) -> Optional[str]:
        """Find the best available agent for a specific task"""
        try:
            with self.lock:
                available_agents = [
                    (agent_id, reg) for agent_id, reg in self.registered_agents.items()
                    if reg.status in [AgentStatus.IDLE, AgentStatus.BUSY] and 
                    len(reg.current_tasks) < reg.max_concurrent_tasks
                ]
                
                if not available_agents:
                    return None
                
                # Score agents based on capability match and performance
                agent_scores = []
                
                for agent_id, registration in available_agents:
                    score = self._calculate_agent_task_score(
                        agent_id, registration, required_capabilities, task
                    )
                    agent_scores.append((agent_id, score))
                
                # Sort by score (descending) and return best agent
                agent_scores.sort(key=lambda x: x[1], reverse=True)
                
                if agent_scores and agent_scores[0][1] > 0:
                    return agent_scores[0][0]
                
                return None
                
        except Exception as e:
            logging.error(f"Error finding best agent: {str(e)}")
            return None
    
    def _calculate_agent_task_score(self, agent_id: str, registration: AgentRegistration,
                                  required_capabilities: List[str], task: Task) -> float:
        """Calculate how well an agent matches a task"""
        score = 0.0
        
        # Capability match score
        agent_caps = set(registration.capabilities)
        required_caps = set(required_capabilities)
        
        if required_caps:
            capability_match = len(agent_caps.intersection(required_caps)) / len(required_caps)
            score += capability_match * 40  # 40% weight for capability match
        else:
            score += 20  # Base score if no specific capabilities required
        
        # Performance score
        perf_metrics = registration.performance_metrics
        if perf_metrics:
            # Efficiency score (0-20 points)
            efficiency = perf_metrics.get('efficiency_rating', 0.5)
            score += efficiency * 20
            
            # Quality score (0-20 points)
            quality = perf_metrics.get('average_quality_score', 0.5)
            score += quality * 20
            
            # Reliability score based on error rate (0-10 points)
            error_rate = perf_metrics.get('error_rate', 0.5)
            reliability = max(0, 1 - error_rate)
            score += reliability * 10
        else:
            score += 25  # Default score for new agents
        
        # Availability penalty (reduce score based on current load)
        load_factor = len(registration.current_tasks) / max(registration.max_concurrent_tasks, 1)
        score *= (1 - load_factor * 0.3)  # Up to 30% penalty for high load
        
        return score
    
    def assign_task_to_agent(self, task_id: str, agent_id: str) -> None:
        """Record task assignment to agent"""
        try:
            with self.lock:
                if agent_id in self.registered_agents:
                    self.registered_agents[agent_id].current_tasks.append(task_id)
        except Exception as e:
            logging.error(f"Error assigning task to agent: {str(e)}")
    
    def complete_task_for_agent(self, task_id: str, agent_id: str) -> None:
        """Record task completion for agent"""
        try:
            with self.lock:
                if agent_id in self.registered_agents:
                    if task_id in self.registered_agents[agent_id].current_tasks:
                        self.registered_agents[agent_id].current_tasks.remove(task_id)
        except Exception as e:
            logging.error(f"Error completing task for agent: {str(e)}")
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get overview of all agents and their status"""
        with self.lock:
            overview = {
                'total_agents': len(self.registered_agents),
                'active_agents': len([r for r in self.registered_agents.values() 
                                    if r.status == AgentStatus.BUSY]),
                'idle_agents': len([r for r in self.registered_agents.values() 
                                  if r.status == AgentStatus.IDLE]),
                'agent_details': []
            }
            
            for agent_id, registration in self.registered_agents.items():
                overview['agent_details'].append({
                    'agent_id': agent_id,
                    'type': registration.agent_type,
                    'status': registration.status.value,
                    'capabilities': registration.capabilities,
                    'current_tasks': len(registration.current_tasks),
                    'max_tasks': registration.max_concurrent_tasks,
                    'last_heartbeat': registration.last_heartbeat.isoformat()
                })
            
            return overview

class PrimaryJAHAgent(BaseAgent):
    """Primary JAH Agent - Central command and coordination hub"""
    
    def __init__(self, agent_id: str = "primary_jah_agent", agent_config: Dict[str, Any] = None):
        if agent_config is None:
            agent_config = {
                'max_concurrent_tasks': 50,
                'task_assignment_timeout': 300,  # 5 minutes
                'agent_heartbeat_timeout': 600,  # 10 minutes
                'performance_monitoring_interval': 60,  # 1 minute
                'system_optimization_interval': 3600  # 1 hour
            }
        
        super().__init__(agent_id, agent_config)
        
        # Initialize specialized components
        self.task_analysis_engine = TaskAnalysisEngine()
        self.agent_management_system = AgentManagementSystem()
        self.active_tasks: Dict[str, Task] = {}
        self.task_assignments: Dict[str, TaskAssignment] = {}
        self.system_metrics = SystemMetrics()
        
        # Communication queues
        self.stakeholder_communication_queue = []
        self.pending_task_assignments = []
        
        # Performance tracking
        self.performance_history = []
        self.optimization_recommendations = []
        
        self.logger.info("Primary JAH Agent initialized successfully")
    
    def initialize_capabilities(self) -> CapabilitySet:
        """Initialize Primary JAH Agent capabilities"""
        return CapabilitySet([
            'task_analysis',
            'agent_coordination',
            'resource_allocation',
            'performance_optimization',
            'strategic_planning',
            'system_monitoring',
            'stakeholder_communication',
            'decision_making',
            'workflow_orchestration',
            'quality_assurance'
        ])
    
    def process_task(self, task: Task) -> TaskResult:
        """Process tasks specific to Primary JAH Agent (meta-tasks)"""
        try:
            if task.task_type == 'system_optimization':
                return self._perform_system_optimization()
            elif task.task_type == 'performance_analysis':
                return self._generate_performance_analysis()
            elif task.task_type == 'agent_management':
                return self._handle_agent_management_task(task)
            elif task.task_type == 'stakeholder_reporting':
                return self._generate_stakeholder_report()
            else:
                # For regular business tasks, coordinate with sub-agents
                return self._coordinate_task_execution(task)
                
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                status='failed',
                error_message=f"Primary agent task processing error: {str(e)}"
            )
    
    def validate_task_compatibility(self, task: Task) -> Dict[str, Any]:
        """Primary JAH Agent can handle coordination of any task"""
        return {
            'is_valid': True,
            'confidence_level': 1.0,
            'can_coordinate': True,
            'requires_sub_agents': task.task_type not in [
                'system_optimization', 'performance_analysis', 
                'agent_management', 'stakeholder_reporting'
            ]
        }
    
    def receive_stakeholder_task(self, task_description: str, requirements: Dict[str, Any] = None,
                               deadline: Optional[datetime] = None, priority: int = 50) -> str:
        """Receive task from human stakeholder and begin processing"""
        try:
            # Create task object
            task = Task(
                task_id=str(uuid.uuid4()),
                title=f"Stakeholder Task: {task_description[:50]}...",
                description=task_description,
                task_type=requirements.get('task_type', 'general') if requirements else 'general',
                complexity_level='medium',  # Will be analyzed
                priority_score=priority,
                requirements=requirements or {},
                deliverables={},
                creation_date=datetime.now(),
                deadline=deadline
            )
            
            # Analyze task
            self._analyze_and_process_stakeholder_task(task)
            
            # Send confirmation to stakeholder
            self._send_stakeholder_confirmation(task)
            
            return task.task_id
            
        except Exception as e:
            self.logger.error(f"Error receiving stakeholder task: {str(e)}")
            return ""
    
    def _analyze_and_process_stakeholder_task(self, task: Task) -> None:
        """Analyze stakeholder task and begin processing workflow"""
        try:
            # Analyze task complexity
            complexity = self.task_analysis_engine.analyze_task_complexity(task)
            task.complexity_level = complexity.value
            
            # Determine required capabilities
            required_capabilities = self.task_analysis_engine.determine_required_capabilities(task)
            
            # Calculate dynamic priority
            task.priority_score = self.task_analysis_engine.calculate_priority_score(task, complexity)
            
            # Store task
            self.active_tasks[task.task_id] = task
            self.system_metrics.active_tasks += 1
            
            # Find appropriate agent
            best_agent = self.agent_management_system.find_best_agent_for_task(
                task, required_capabilities
            )
            
            if best_agent:
                self._assign_task_to_agent(task, best_agent, required_capabilities)
            else:
                # No suitable agent available - queue for later or create new agent
                self._handle_no_available_agent(task, required_capabilities)
                
        except Exception as e:
            self.logger.error(f"Error analyzing stakeholder task: {str(e)}")
    
    def _assign_task_to_agent(self, task: Task, agent_id: str, required_capabilities: List[str]) -> None:
        """Assign task to specific agent"""
        try:
            # Create assignment record
            assignment = TaskAssignment(
                task_id=task.task_id,
                agent_id=agent_id,
                assignment_time=datetime.now(),
                estimated_completion=datetime.now() + timedelta(hours=2),  # Default estimate
                confidence_score=0.8,  # Will be calculated more precisely
                assignment_reasoning=f"Best match for capabilities: {', '.join(required_capabilities)}"
            )
            
            self.task_assignments[task.task_id] = assignment
            self.agent_management_system.assign_task_to_agent(task.task_id, agent_id)
            
            # Send task to agent
            self._send_task_to_agent(task, agent_id)
            
            self.logger.info(f"Task {task.task_id} assigned to agent {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Error assigning task to agent: {str(e)}")
    
    def _send_task_to_agent(self, task: Task, agent_id: str) -> None:
        """Send task assignment message to agent"""
        assignment_message = CommunicationMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.agent_id,
            recipient_id=agent_id,
            message_type="task_assignment",
            content={
                "task": {
                    "task_id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type,
                    "complexity_level": task.complexity_level,
                    "priority_score": task.priority_score,
                    "requirements": task.requirements,
                    "deliverables": task.deliverables,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "estimated_hours": task.estimated_hours
                }
            },
            timestamp=datetime.now(),
            priority=MessagePriority.HIGH,
            delivery_confirmation_required=True
        )
        
        self.communication_handler.send_message(assignment_message)
    
    def _handle_no_available_agent(self, task: Task, required_capabilities: List[str]) -> None:
        """Handle case when no suitable agent is available"""
        self.logger.warning(f"No available agent for task {task.task_id} with capabilities {required_capabilities}")
        
        # Add to pending assignments
        self.pending_task_assignments.append({
            'task': task,
            'required_capabilities': required_capabilities,
            'queued_time': datetime.now()
        })
        
        # Consider creating new agent or notifying stakeholder
        self._consider_agent_scaling(required_capabilities)
    
    def _consider_agent_scaling(self, required_capabilities: List[str]) -> None:
        """Consider whether to create new agents or scale existing ones"""
        # Simplified logic - in production would be more sophisticated
        self.logger.info(f"Considering scaling for capabilities: {required_capabilities}")
        
        # Could implement:
        # - Dynamic agent creation
        # - Load balancing adjustments
        # - Resource optimization
        # - Stakeholder notification for manual scaling decisions
    
    def _coordinate_task_execution(self, task: Task) -> TaskResult:
        """Coordinate execution of complex tasks requiring multiple agents"""
        try:
            self.logger.info(f"Coordinating execution of task {task.task_id}")
            
            # This would implement complex workflow orchestration
            # For now, return a coordination result
            return TaskResult(
                task_id=task.task_id,
                status='completed',
                deliverables={
                    'coordination_result': 'Task coordination completed',
                    'sub_tasks_created': 0,
                    'agents_involved': []
                },
                quality_metrics={'coordination_efficiency': 0.85},
                performance_indicators={'coordination_time': 0.5}
            )
            
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                status='failed',
                error_message=f"Coordination error: {str(e)}"
            )
    
    def _perform_system_optimization(self) -> TaskResult:
        """Perform system-wide optimization"""
        try:
            self.logger.info("Performing system optimization")
            
            # Analyze current system performance
            system_overview = self.agent_management_system.get_system_overview()
            
            # Identify optimization opportunities
            optimizations = []
            
            # Check for idle agents
            idle_agents = [agent for agent in system_overview['agent_details'] 
                          if agent['status'] == 'idle']
            if len(idle_agents) > 3:
                optimizations.append("Consider consolidating idle agents")
            
            # Check for overloaded agents
            overloaded_agents = [agent for agent in system_overview['agent_details']
                               if agent['current_tasks'] >= agent['max_tasks']]
            if overloaded_agents:
                optimizations.append(f"Scale up capacity for {len(overloaded_agents)} overloaded agents")
            
            # Check pending tasks
            if len(self.pending_task_assignments) > 5:
                optimizations.append("High number of pending tasks - consider adding agents")
            
            return TaskResult(
                task_id="system_optimization",
                status='completed',
                deliverables={
                    'system_overview': system_overview,
                    'optimization_recommendations': optimizations,
                    'performance_metrics': self.system_metrics.__dict__
                },
                quality_metrics={'optimization_effectiveness': 0.8}
            )
            
        except Exception as e:
            return TaskResult(
                task_id="system_optimization",
                status='failed',
                error_message=f"Optimization error: {str(e)}"
            )
    
    def _generate_performance_analysis(self) -> TaskResult:
        """Generate comprehensive performance analysis"""
        try:
            self.logger.info("Generating performance analysis")
            
            # Calculate system-wide metrics
            total_tasks = self.system_metrics.completed_tasks + self.system_metrics.failed_tasks
            success_rate = (self.system_metrics.completed_tasks / total_tasks * 100 
                          if total_tasks > 0 else 0)
            
            # Agent performance summary
            agent_performance = []
            system_overview = self.agent_management_system.get_system_overview()
            
            for agent_detail in system_overview['agent_details']:
                agent_id = agent_detail['agent_id']
                if agent_id in self.agent_management_system.registered_agents:
                    reg = self.agent_management_system.registered_agents[agent_id]
                    agent_performance.append({
                        'agent_id': agent_id,
                        'type': agent_detail['type'],
                        'performance_metrics': reg.performance_metrics,
                        'current_load': len(reg.current_tasks),
                        'efficiency': reg.performance_metrics.get('efficiency_rating', 0)
                    })
            
            return TaskResult(
                task_id="performance_analysis",
                status='completed',
                deliverables={
                    'system_success_rate': success_rate,
                    'total_tasks_processed': total_tasks,
                    'active_tasks': self.system_metrics.active_tasks,
                    'agent_performance': agent_performance,
                    'system_efficiency': self.system_metrics.system_efficiency,
                    'recommendations': self._generate_performance_recommendations()
                },
                quality_metrics={'analysis_completeness': 0.9}
            )
            
        except Exception as e:
            return TaskResult(
                task_id="performance_analysis",
                status='failed',
                error_message=f"Performance analysis error: {str(e)}"
            )
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Check success rate
        total_tasks = self.system_metrics.completed_tasks + self.system_metrics.failed_tasks
        if total_tasks > 0:
            success_rate = self.system_metrics.completed_tasks / total_tasks
            if success_rate < 0.9:
                recommendations.append("Investigate and address task failure causes")
        
        # Check system efficiency
        if self.system_metrics.system_efficiency < 0.75:
            recommendations.append("Optimize task distribution and agent utilization")
        
        # Check average completion time
        if self.system_metrics.average_task_completion_time > 4.0:  # hours
            recommendations.append("Review task complexity estimation and agent training")
        
        return recommendations
    
    def _generate_stakeholder_report(self) -> TaskResult:
        """Generate stakeholder-focused system report"""
        try:
            # Get current system state
            system_overview = self.agent_management_system.get_system_overview()
            
            # Calculate key metrics
            total_tasks = self.system_metrics.completed_tasks + self.system_metrics.failed_tasks
            success_rate = (self.system_metrics.completed_tasks / total_tasks * 100 
                          if total_tasks > 0 else 0)
            
            # Recent performance trend (simplified)
            performance_trend = "stable"  # Would calculate from historical data
            
            stakeholder_report = {
                'executive_summary': {
                    'total_agents': system_overview['total_agents'],
                    'active_tasks': self.system_metrics.active_tasks,
                    'success_rate': round(success_rate, 1),
                    'system_status': 'operational',
                    'performance_trend': performance_trend
                },
                'operational_metrics': {
                    'completed_tasks': self.system_metrics.completed_tasks,
                    'failed_tasks': self.system_metrics.failed_tasks,
                    'average_completion_time': round(self.system_metrics.average_task_completion_time, 2),
                    'system_efficiency': round(self.system_metrics.system_efficiency, 2)
                },
                'agent_utilization': {
                    'active_agents': system_overview['active_agents'],
                    'idle_agents': system_overview['idle_agents'],
                    'utilization_rate': round(
                        system_overview['active_agents'] / max(system_overview['total_agents'], 1) * 100, 1
                    )
                },
                'recommendations': self._generate_stakeholder_recommendations(),
                'report_timestamp': datetime.now().isoformat()
            }
            
            return TaskResult(
                task_id="stakeholder_report",
                status='completed',
                deliverables={'stakeholder_report': stakeholder_report},
                quality_metrics={'report_completeness': 0.95}
            )
            
        except Exception as e:
            return TaskResult(
                task_id="stakeholder_report",
                status='failed',
                error_message=f"Stakeholder report error: {str(e)}"
            )
    
    def _generate_stakeholder_recommendations(self) -> List[str]:
        """Generate high-level recommendations for stakeholders"""
        recommendations = []
        
        system_overview = self.agent_management_system.get_system_overview()
        
        # Agent capacity recommendations
        if system_overview['idle_agents'] > system_overview['active_agents']:
            recommendations.append("Consider optimizing agent allocation - high idle capacity detected")
        elif len(self.pending_task_assignments) > 0:
            recommendations.append("Consider expanding agent capacity to handle pending tasks")
        
        # Performance recommendations
        if self.system_metrics.system_efficiency < 0.8:
            recommendations.append("System efficiency could be improved through optimization")
        
        # Revenue opportunity recommendations
        if self.system_metrics.completed_tasks > 50:
            recommendations.append("System showing strong task completion - consider expanding operations")
        
        return recommendations
    
    def handle_agent_registration(self, agent_id: str, agent_type: str, capabilities: List[str]) -> bool:
        """Handle new agent registration"""
        success = self.agent_management_system.register_agent(agent_id, agent_type, capabilities)
        if success:
            self.system_metrics.active_agents += 1
            # Check if any pending tasks can now be assigned
            self._process_pending_assignments()
        return success
    
    def handle_agent_status_update(self, agent_id: str, status: AgentStatus, 
                                 performance_metrics: Optional[Dict] = None) -> None:
        """Handle agent status updates"""
        self.agent_management_system.update_agent_status(agent_id, status, performance_metrics)
    
    def handle_task_completion(self, task_id: str, agent_id: str, result: TaskResult) -> None:
        """Handle task completion from sub-agent"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                
                # Update system metrics
                if result.status == 'completed':
                    self.system_metrics.completed_tasks += 1
                else:
                    self.system_metrics.failed_tasks += 1
                
                self.system_metrics.active_tasks -= 1
                
                # Update agent task list
                self.agent_management_system.complete_task_for_agent(task_id, agent_id)
                
                # Notify stakeholder if this was a stakeholder task
                self._notify_stakeholder_of_completion(task, result)
                
                # Clean up
                del self.active_tasks[task_id]
                if task_id in self.task_assignments:
                    del self.task_assignments[task_id]
                
                self.logger.info(f"Task {task_id} completed by agent {agent_id} with status {result.status}")
                
        except Exception as e:
            self.logger.error(f"Error handling task completion: {str(e)}")
    
    def _notify_stakeholder_of_completion(self, task: Task, result: TaskResult) -> None:
        """Notify stakeholder of task completion"""
        notification = {
            'task_id': task.task_id,
            'task_title': task.title,
            'completion_status': result.status,
            'completion_time': result.completion_time.isoformat() if result.completion_time else None,
            'deliverables': result.deliverables,
            'quality_metrics': result.quality_metrics
        }
        
        # Add to stakeholder communication queue
        self.stakeholder_communication_queue.append({
            'type': 'task_completion',
            'content': notification,
            'timestamp': datetime.now()
        })
        
        self.logger.info(f"Stakeholder notified of task {task.task_id} completion")
    
    def _process_pending_assignments(self) -> None:
        """Process any pending task assignments"""
        if not self.pending_task_assignments:
            return
        
        assignments_to_remove = []
        
        for i, pending in enumerate(self.pending_task_assignments):
            task = pending['task']
            required_capabilities = pending['required_capabilities']
            
            # Try to find an agent now
            best_agent = self.agent_management_system.find_best_agent_for_task(
                task, required_capabilities
            )
            
            if best_agent:
                self._assign_task_to_agent(task, best_agent, required_capabilities)
                assignments_to_remove.append(i)
        
        # Remove processed assignments
        for i in reversed(assignments_to_remove):
            del self.pending_task_assignments[i]
    
    def _send_stakeholder_confirmation(self, task: Task) -> None:
        """Send confirmation to stakeholder that task was received"""
        confirmation = {
            'task_id': task.task_id,
            'message': f'Task "{task.title}" received and processing has begun',
            'estimated_completion': (datetime.now() + timedelta(hours=4)).isoformat(),
            'priority_level': task.priority_score,
            'complexity': task.complexity_level
        }
        
        self.stakeholder_communication_queue.append({
            'type': 'task_confirmation',
            'content': confirmation,
            'timestamp': datetime.now()
        })
    
    def get_stakeholder_communications(self) -> List[Dict]:
        """Get and clear pending stakeholder communications"""
        communications = self.stakeholder_communication_queue.copy()
        self.stakeholder_communication_queue.clear()
        return communications
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for monitoring"""
        system_overview = self.agent_management_system.get_system_overview()
        
        return {
            'primary_agent_status': self.status.value,
            'system_metrics': self.system_metrics.__dict__,
            'agent_overview': system_overview,
            'active_tasks_count': len(self.active_tasks),
            'pending_assignments': len(self.pending_task_assignments),
            'task_assignments': len(self.task_assignments),
            'stakeholder_communications_pending': len(self.stakeholder_communication_queue),
            'timestamp': datetime.now().isoformat()
        }

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create Primary JAH Agent
    primary_agent = PrimaryJAHAgent()
    primary_agent.start_agent()
    
    # Simulate agent registrations
    primary_agent.handle_agent_registration("marketing_agent_001", "marketing", 
                                           ["content_creation", "social_media", "analytics"])
    primary_agent.handle_agent_registration("technical_agent_001", "technical", 
                                           ["programming", "system_design", "debugging"])
    primary_agent.handle_agent_registration("research_agent_001", "research", 
                                           ["data_analysis", "market_research", "reporting"])
    
    # Simulate stakeholder task
    task_id = primary_agent.receive_stakeholder_task(
        task_description="Create a comprehensive marketing campaign for our new product launch",
        requirements={
            'task_type': 'marketing_campaign',
            'required_capabilities': ['content_creation', 'social_media', 'analytics'],
            'budget': 5000,
            'target_audience': 'tech professionals'
        },
        deadline=datetime.now() + timedelta(days=3),
        priority=80
    )
    
    print(f"Task submitted with ID: {task_id}")
    
    # Check system status
    time.sleep(2)
    status = primary_agent.get_system_status()
    print(f"System Status: {json.dumps(status, indent=2, default=str)}")
    
    # Check stakeholder communications
    communications = primary_agent.get_stakeholder_communications()
    print(f"Stakeholder Communications: {json.dumps(communications, indent=2, default=str)}")
    
    # Stop the agent
    time.sleep(5)
    primary_agent.stop_agent()
