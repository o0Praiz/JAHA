# JAH Agency - Task Distribution Engine
# Version 1.0 | Intelligent Work Allocation System

import heapq
import logging
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import math
import statistics
import uuid

# Import base components (would be from separate modules in production)
from jah_base_agent import Task, TaskStatus, AgentStatus

class PriorityCategory(Enum):
    CRITICAL = "critical"
    HIGH = "high"  
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class TaskPriorityScore:
    composite_score: float
    urgency_score: float
    business_impact_score: float
    resource_efficiency_score: float
    revenue_impact_score: float
    dependency_score: float
    calculation_timestamp: datetime
    recalculation_triggers: List[str] = field(default_factory=list)

@dataclass
class AgentCapabilityProfile:
    agent_id: str
    capabilities: List[str]
    proficiency_levels: Dict[str, float]
    specializations: List[str]
    experience_history: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    current_workload: int
    max_capacity: int
    availability_schedule: Dict[str, Any]
    learning_efficiency: float = 0.8
    
@dataclass
class TaskAgentCompatibility:
    agent_id: str
    task_id: str
    compatibility_score: float
    skill_match_score: float
    experience_relevance_score: float
    performance_prediction_score: float
    availability_score: float
    confidence_level: float
    assignment_reasoning: str
    improvement_recommendations: List[str] = field(default_factory=list)

@dataclass
class WorkloadDistribution:
    agent_id: str
    current_tasks: List[str]
    utilization_percentage: float
    efficiency_rating: float
    projected_completion_times: Dict[str, datetime]
    capacity_remaining: int
    overload_risk: float
    optimization_suggestions: List[str] = field(default_factory=list)

class TaskPriorityEngine:
    """Advanced priority calculation engine with multi-factor analysis"""
    
    def __init__(self):
        self.priority_weights = {
            'urgency': 0.25,
            'business_impact': 0.30,
            'resource_efficiency': 0.20,
            'revenue_impact': 0.15,
            'dependency_impact': 0.10
        }
        
        self.urgency_thresholds = {
            'critical': 2.0,    # hours
            'high': 24.0,       # hours
            'medium': 168.0,    # hours (1 week)
            'low': float('inf')
        }
        
        self.business_impact_factors = {
            'client_tier': {'enterprise': 1.5, 'premium': 1.2, 'standard': 1.0, 'basic': 0.8},
            'strategic_importance': {'critical': 2.0, 'high': 1.5, 'medium': 1.0, 'low': 0.5},
            'stakeholder_priority': {'ceo': 2.0, 'executive': 1.5, 'manager': 1.0, 'team': 0.8}
        }
        
        self.revenue_impact_multipliers = {
            'direct_revenue': 2.0,
            'pipeline_impact': 1.5,
            'retention_impact': 1.3,
            'cost_savings': 1.0
        }
    
    def calculate_comprehensive_priority(self, task: Task, system_context: Dict[str, Any]) -> TaskPriorityScore:
        """Calculate comprehensive priority score with multiple factors"""
        try:
            current_time = datetime.now()
            
            # Calculate urgency score
            urgency_score = self._calculate_urgency_score(task, current_time)
            
            # Calculate business impact score
            business_impact_score = self._calculate_business_impact_score(task, system_context)
            
            # Calculate resource efficiency score
            resource_efficiency_score = self._calculate_resource_efficiency_score(task, system_context)
            
            # Calculate revenue impact score
            revenue_impact_score = self._calculate_revenue_impact_score(task)
            
            # Calculate dependency impact score
            dependency_score = self._calculate_dependency_impact_score(task, system_context)
            
            # Calculate weighted composite score
            composite_score = (
                urgency_score * self.priority_weights['urgency'] +
                business_impact_score * self.priority_weights['business_impact'] +
                resource_efficiency_score * self.priority_weights['resource_efficiency'] +
                revenue_impact_score * self.priority_weights['revenue_impact'] +
                dependency_score * self.priority_weights['dependency_impact']
            )
            
            # Normalize to 0-100 scale
            composite_score = min(100.0, max(0.0, composite_score))
            
            return TaskPriorityScore(
                composite_score=composite_score,
                urgency_score=urgency_score,
                business_impact_score=business_impact_score,
                resource_efficiency_score=resource_efficiency_score,
                revenue_impact_score=revenue_impact_score,
                dependency_score=dependency_score,
                calculation_timestamp=current_time,
                recalculation_triggers=self._determine_recalculation_triggers(task)
            )
            
        except Exception as e:
            logging.error(f"Error calculating task priority: {str(e)}")
            return TaskPriorityScore(
                composite_score=50.0,  # Default medium priority
                urgency_score=50.0,
                business_impact_score=50.0,
                resource_efficiency_score=50.0,
                revenue_impact_score=50.0,
                dependency_score=50.0,
                calculation_timestamp=current_time
            )
    
    def _calculate_urgency_score(self, task: Task, current_time: datetime) -> float:
        """Calculate urgency score based on deadline and creation time"""
        if not task.deadline:
            return 30.0  # Low urgency for tasks without deadline
        
        time_to_deadline = (task.deadline - current_time).total_seconds() / 3600.0  # hours
        time_since_creation = (current_time - task.creation_date).total_seconds() / 3600.0
        
        # Base urgency from deadline
        if time_to_deadline <= self.urgency_thresholds['critical']:
            base_urgency = 95.0
        elif time_to_deadline <= self.urgency_thresholds['high']:
            base_urgency = 80.0
        elif time_to_deadline <= self.urgency_thresholds['medium']:
            base_urgency = 50.0
        else:
            base_urgency = 20.0
        
        # Increase urgency based on how long task has been waiting
        aging_factor = min(1.5, 1.0 + (time_since_creation / 24.0) * 0.1)  # 10% increase per day
        
        # Adjust for estimated completion time
        estimated_hours = task.estimated_hours or 2.0
        if time_to_deadline < estimated_hours * 1.5:  # Less than 1.5x estimated time remaining
            urgency_multiplier = 1.3
        else:
            urgency_multiplier = 1.0
        
        return min(100.0, base_urgency * aging_factor * urgency_multiplier)
    
    def _calculate_business_impact_score(self, task: Task, system_context: Dict[str, Any]) -> float:
        """Calculate business impact score"""
        base_score = 50.0
        
        # Client tier impact
        client_tier = task.requirements.get('client_tier', 'standard')
        client_multiplier = self.business_impact_factors['client_tier'].get(client_tier, 1.0)
        
        # Strategic importance
        strategic_importance = task.requirements.get('strategic_importance', 'medium')
        strategic_multiplier = self.business_impact_factors['strategic_importance'].get(strategic_importance, 1.0)
        
        # Stakeholder priority
        stakeholder_level = task.requirements.get('stakeholder_level', 'team')
        stakeholder_multiplier = self.business_impact_factors['stakeholder_priority'].get(stakeholder_level, 1.0)
        
        # Task type specific impact
        high_impact_types = ['client_deliverable', 'revenue_generation', 'compliance_requirement']
        type_multiplier = 1.3 if task.task_type in high_impact_types else 1.0
        
        impact_score = base_score * client_multiplier * strategic_multiplier * stakeholder_multiplier * type_multiplier
        
        return min(100.0, impact_score)
    
    def _calculate_resource_efficiency_score(self, task: Task, system_context: Dict[str, Any]) -> float:
        """Calculate resource efficiency score"""
        base_score = 50.0
        
        # Consider current system load
        system_load = system_context.get('system_load', 0.5)
        if system_load < 0.3:  # Low load - prioritize resource utilization
            efficiency_multiplier = 1.2
        elif system_load > 0.8:  # High load - prioritize quick tasks
            estimated_hours = task.estimated_hours or 2.0
            efficiency_multiplier = 1.5 if estimated_hours < 1.0 else 0.8
        else:
            efficiency_multiplier = 1.0
        
        # Consider task complexity vs available expertise
        required_skills = task.requirements.get('required_capabilities', [])
        available_expertise = system_context.get('available_expertise', {})
        
        expertise_match = 0.0
        if required_skills:
            matched_skills = sum(1 for skill in required_skills if skill in available_expertise)
            expertise_match = matched_skills / len(required_skills)
        
        expertise_multiplier = 1.0 + (expertise_match * 0.3)  # Up to 30% bonus for good expertise match
        
        efficiency_score = base_score * efficiency_multiplier * expertise_multiplier
        
        return min(100.0, efficiency_score)
    
    def _calculate_revenue_impact_score(self, task: Task) -> float:
        """Calculate revenue impact score"""
        base_score = 20.0  # Low base for tasks without revenue impact
        
        revenue_potential = task.revenue_potential or 0.0
        
        if revenue_potential > 0:
            # Logarithmic scale for revenue impact
            revenue_score = 30.0 + (20.0 * math.log10(max(1, revenue_potential / 100)))
            revenue_score = min(90.0, max(30.0, revenue_score))
        else:
            revenue_score = base_score
        
        # Consider revenue type
        revenue_type = task.requirements.get('revenue_type', 'none')
        multiplier = self.revenue_impact_multipliers.get(revenue_type, 1.0)
        
        return min(100.0, revenue_score * multiplier)
    
    def _calculate_dependency_impact_score(self, task: Task, system_context: Dict[str, Any]) -> float:
        """Calculate dependency impact score"""
        base_score = 50.0
        
        # Check if task is blocking other tasks
        blocked_tasks = task.requirements.get('blocks_tasks', [])
        blocking_multiplier = 1.0 + (len(blocked_tasks) * 0.2)  # 20% increase per blocked task
        
        # Check if task has dependencies
        dependencies = task.requirements.get('depends_on', [])
        dependency_penalty = len(dependencies) * 0.1  # 10% penalty per dependency
        
        # Check dependency status
        dependency_graph = system_context.get('dependency_graph', {})
        ready_dependencies = 0
        if dependencies:
            for dep in dependencies:
                if dependency_graph.get(dep, {}).get('status') == 'completed':
                    ready_dependencies += 1
        
        dependency_readiness = ready_dependencies / len(dependencies) if dependencies else 1.0
        
        dependency_score = base_score * blocking_multiplier * (1 - dependency_penalty) * dependency_readiness
        
        return min(100.0, max(10.0, dependency_score))
    
    def _determine_recalculation_triggers(self, task: Task) -> List[str]:
        """Determine conditions that should trigger priority recalculation"""
        triggers = ['system_load_change', 'agent_availability_change']
        
        if task.deadline:
            time_to_deadline = (task.deadline - datetime.now()).total_seconds() / 3600.0
            if time_to_deadline < 48:  # Less than 48 hours
                triggers.append('hourly_deadline_check')
            else:
                triggers.append('daily_deadline_check')
        
        if task.requirements.get('depends_on'):
            triggers.append('dependency_status_change')
        
        if task.revenue_potential and task.revenue_potential > 1000:
            triggers.append('high_value_task_monitoring')
        
        return triggers

class IntelligentTaskQueue:
    """Advanced task queue with dynamic prioritization and optimization"""
    
    def __init__(self, rebalancing_interval: int = 300):  # 5 minutes
        self._priority_queue = []  # Min heap (we'll use negative priorities)
        self._task_registry = {}  # task_id -> task mapping
        self._priority_cache = {}  # task_id -> priority_score mapping
        self._queue_lock = threading.Lock()
        self._last_rebalance = datetime.now()
        self._rebalancing_interval = rebalancing_interval
        self.priority_engine = TaskPriorityEngine()
        self.performance_metrics = {
            'total_enqueued': 0,
            'total_dequeued': 0,
            'average_wait_time': 0.0,
            'priority_distribution': defaultdict(int)
        }
    
    def enqueue_task(self, task: Task, system_context: Dict[str, Any]) -> bool:
        """Enqueue task with dynamic priority calculation"""
        try:
            with self._queue_lock:
                # Calculate priority score
                priority_score = self.priority_engine.calculate_comprehensive_priority(task, system_context)
                
                # Create queue entry (negative priority for max-heap behavior)
                queue_entry = (
                    -priority_score.composite_score,  # Negative for max-heap
                    task.creation_date.timestamp(),    # Tie-breaker (FIFO for same priority)
                    task.task_id,                      # Unique identifier
                    task                               # Task object
                )
                
                # Add to priority queue
                heapq.heappush(self._priority_queue, queue_entry)
                
                # Update registries
                self._task_registry[task.task_id] = task
                self._priority_cache[task.task_id] = priority_score
                
                # Update metrics
                self.performance_metrics['total_enqueued'] += 1
                priority_category = self._get_priority_category(priority_score.composite_score)
                self.performance_metrics['priority_distribution'][priority_category] += 1
                
                logging.info(f"Task {task.task_id} enqueued with priority {priority_score.composite_score:.2f}")
                return True
                
        except Exception as e:
            logging.error(f"Error enqueuing task: {str(e)}")
            return False
    
    def dequeue_optimal_task(self, agent_profile: AgentCapabilityProfile, 
                           system_context: Dict[str, Any]) -> Optional[Task]:
        """Dequeue the optimal task for the specified agent"""
        try:
            with self._queue_lock:
                if not self._priority_queue:
                    return None
                
                # Check if rebalancing is needed
                if self._should_rebalance():
                    self._rebalance_queue(system_context)
                
                # Find compatible tasks in priority order
                compatible_tasks = []
                temp_queue = []
                
                # Extract tasks and check compatibility
                while self._priority_queue:
                    priority, timestamp, task_id, task = heapq.heappop(self._priority_queue)
                    
                    if self._is_task_compatible(task, agent_profile):
                        compatible_tasks.append((priority, timestamp, task_id, task))
                    else:
                        temp_queue.append((priority, timestamp, task_id, task))
                
                # Restore non-compatible tasks to queue
                for item in temp_queue:
                    heapq.heappush(self._priority_queue, item)
                
                # Select best compatible task
                if compatible_tasks:
                    # Sort by priority (already negative, so normal sort gives us highest priority first)
                    compatible_tasks.sort()
                    _, _, selected_task_id, selected_task = compatible_tasks[0]
                    
                    # Put other compatible tasks back
                    for item in compatible_tasks[1:]:
                        heapq.heappush(self._priority_queue, item)
                    
                    # Clean up registries
                    del self._task_registry[selected_task_id]
                    del self._priority_cache[selected_task_id]
                    
                    # Update metrics
                    self.performance_metrics['total_dequeued'] += 1
                    self._update_wait_time_metrics(selected_task)
                    
                    logging.info(f"Task {selected_task_id} dequeued for agent {agent_profile.agent_id}")
                    return selected_task
                
                return None
                
        except Exception as e:
            logging.error(f"Error dequeuing task: {str(e)}")
            return None
    
    def _is_task_compatible(self, task: Task, agent_profile: AgentCapabilityProfile) -> bool:
        """Check if task is compatible with agent capabilities"""
        required_capabilities = task.requirements.get('required_capabilities', [])
        
        if not required_capabilities:
            return True  # No specific requirements
        
        agent_capabilities = set(agent_profile.capabilities)
        required_capabilities_set = set(required_capabilities)
        
        # Check if agent has required capabilities
        capability_overlap = agent_capabilities.intersection(required_capabilities_set)
        coverage_ratio = len(capability_overlap) / len(required_capabilities_set)
        
        # Require at least 70% capability coverage
        return coverage_ratio >= 0.7
    
    def _should_rebalance(self) -> bool:
        """Determine if queue should be rebalanced"""
        time_since_rebalance = (datetime.now() - self._last_rebalance).total_seconds()
        return time_since_rebalance >= self._rebalancing_interval
    
    def _rebalance_queue(self, system_context: Dict[str, Any]) -> None:
        """Rebalance queue priorities based on current system state"""
        try:
            logging.info("Rebalancing task queue priorities")
            
            # Extract all tasks
            all_tasks = []
            while self._priority_queue:
                _, _, task_id, task = heapq.heappop(self._priority_queue)
                all_tasks.append(task)
            
            # Recalculate priorities and re-enqueue
            for task in all_tasks:
                priority_score = self.priority_engine.calculate_comprehensive_priority(task, system_context)
                self._priority_cache[task.task_id] = priority_score
                
                queue_entry = (
                    -priority_score.composite_score,
                    task.creation_date.timestamp(),
                    task.task_id,
                    task
                )
                heapq.heappush(self._priority_queue, queue_entry)
            
            self._last_rebalance = datetime.now()
            logging.info(f"Queue rebalanced with {len(all_tasks)} tasks")
            
        except Exception as e:
            logging.error(f"Error rebalancing queue: {str(e)}")
    
    def _get_priority_category(self, priority_score: float) -> str:
        """Get priority category from score"""
        if priority_score >= 80:
            return 'critical'
        elif priority_score >= 60:
            return 'high'
        elif priority_score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _update_wait_time_metrics(self, task: Task) -> None:
        """Update average wait time metrics"""
        wait_time = (datetime.now() - task.creation_date).total_seconds() / 3600.0  # hours
        
        current_avg = self.performance_metrics['average_wait_time']
        total_dequeued = self.performance_metrics['total_dequeued']
        
        # Calculate new average
        new_avg = ((current_avg * (total_dequeued - 1)) + wait_time) / total_dequeued
        self.performance_metrics['average_wait_time'] = new_avg
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status and metrics"""
        with self._queue_lock:
            return {
                'queue_size': len(self._priority_queue),
                'performance_metrics': dict(self.performance_metrics),
                'priority_distribution': dict(self.performance_metrics['priority_distribution']),
                'last_rebalance': self._last_rebalance.isoformat(),
                'next_rebalance': (self._last_rebalance + timedelta(seconds=self._rebalancing_interval)).isoformat()
            }
    
    def get_pending_tasks_summary(self) -> List[Dict[str, Any]]:
        """Get summary of pending tasks"""
        with self._queue_lock:
            summary = []
            for priority, timestamp, task_id, task in self._priority_queue:
                priority_score = self._priority_cache.get(task_id)
                summary.append({
                    'task_id': task_id,
                    'title': task.title,
                    'priority_score': -priority,  # Convert back to positive
                    'created': datetime.fromtimestamp(timestamp).isoformat(),
                    'wait_time_hours': (datetime.now() - task.creation_date).total_seconds() / 3600.0,
                    'task_type': task.task_type,
                    'complexity': task.complexity_level
                })
            
            # Sort by priority (highest first)
            summary.sort(key=lambda x: x['priority_score'], reverse=True)
            return summary

class CapabilityMatchingEngine:
    """Advanced agent-task compatibility assessment system"""
    
    def __init__(self):
        self.skill_weights = {
            'exact_match': 1.0,
            'related_skill': 0.7,
            'transferable_skill': 0.4,
            'learning_potential': 0.2
        }
        
        self.experience_factors = {
            'domain_experience': 0.4,
            'task_type_experience': 0.3,
            'complexity_experience': 0.2,
            'recent_performance': 0.1
        }
        
        # Define skill relationships for transferability
        self.skill_relationships = {
            'content_creation': ['writing', 'creativity', 'marketing'],
            'data_analysis': ['statistics', 'research', 'visualization'],
            'programming': ['system_design', 'debugging', 'technical_writing'],
            'marketing': ['content_creation', 'analytics', 'communication'],
            'sales': ['communication', 'persuasion', 'relationship_management']
        }
    
    def evaluate_agent_task_compatibility(self, agent_profile: AgentCapabilityProfile, 
                                        task: Task) -> TaskAgentCompatibility:
        """Evaluate comprehensive compatibility between agent and task"""
        try:
            # Analyze skill alignment
            skill_match = self._analyze_skill_alignment(agent_profile, task)
            
            # Evaluate experience relevance
            experience_relevance = self._evaluate_experience_relevance(agent_profile, task)
            
            # Predict performance likelihood
            performance_prediction = self._predict_task_performance(agent_profile, task)
            
            # Assess availability and capacity
            availability_score = self._assess_agent_availability(agent_profile, task)
            
            # Calculate composite compatibility score
            compatibility_score = self._calculate_composite_compatibility(
                skill_match, experience_relevance, performance_prediction, availability_score
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_assignment_confidence(
                compatibility_score, skill_match, experience_relevance
            )
            
            # Generate assignment reasoning
            reasoning = self._generate_assignment_reasoning(
                skill_match, experience_relevance, performance_prediction, availability_score
            )
            
            # Generate improvement recommendations
            improvements = self._generate_improvement_recommendations(
                agent_profile, task, skill_match
            )
            
            return TaskAgentCompatibility(
                agent_id=agent_profile.agent_id,
                task_id=task.task_id,
                compatibility_score=compatibility_score,
                skill_match_score=skill_match['overall_score'],
                experience_relevance_score=experience_relevance['overall_score'],
                performance_prediction_score=performance_prediction,
                availability_score=availability_score,
                confidence_level=confidence_level,
                assignment_reasoning=reasoning,
                improvement_recommendations=improvements
            )
            
        except Exception as e:
            logging.error(f"Error evaluating agent-task compatibility: {str(e)}")
            return TaskAgentCompatibility(
                agent_id=agent_profile.agent_id,
                task_id=task.task_id,
                compatibility_score=0.5,
                skill_match_score=0.5,
                experience_relevance_score=0.5,
                performance_prediction_score=0.5,
                availability_score=0.5,
                confidence_level=0.3,
                assignment_reasoning="Error in compatibility evaluation"
            )
    
    def _analyze_skill_alignment(self, agent_profile: AgentCapabilityProfile, task: Task) -> Dict[str, Any]:
        """Analyze how well agent skills align with task requirements"""
        required_skills = task.requirements.get('required_capabilities', [])
        agent_skills = set(agent_profile.capabilities)
        
        if not required_skills:
            return {
                'overall_score': 0.7,  # Neutral score for tasks without specific requirements
                'exact_matches': [],
                'related_matches': [],
                'gaps': [],
                'coverage_ratio': 1.0
            }
        
        exact_matches = []
        related_matches = []
        gaps = []
        
        for required_skill in required_skills:
            if required_skill in agent_skills:
                exact_matches.append(required_skill)
            else:
                # Check for related skills
                related_found = False
                for agent_skill in agent_skills:
                    if self._are_skills_related(required_skill, agent_skill):
                        related_matches.append((required_skill, agent_skill))
                        related_found = True
                        break
                
                if not related_found:
                    gaps.append(required_skill)
        
        # Calculate coverage ratios
        exact_coverage = len(exact_matches) / len(required_skills)
        related_coverage = len(related_matches) / len(required_skills)
        gap_ratio = len(gaps) / len(required_skills)
        
        # Calculate overall skill match score
        overall_score = (
            exact_coverage * self.skill_weights['exact_match'] +
            related_coverage * self.skill_weights['related_skill'] +
            (1 - gap_ratio) * self.skill_weights['transferable_skill']
        )
        
        return {
            'overall_score': min(1.0, overall_score),
            'exact_matches': exact_matches,
            'related_matches': related_matches,
            'gaps': gaps,
            'coverage_ratio': exact_coverage + (related_coverage * 0.7)
        }
    
    def _are_skills_related(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are related"""
        for primary_skill, related_skills in self.skill_relationships.items():
            if skill1 == primary_skill and skill2 in related_skills:
                return True
            if skill2 == primary_skill and skill1 in related_skills:
                return True
            if skill1 in related_skills and skill2 in related_skills:
                return True
        return False
    
    def _evaluate_experience_relevance(self, agent_profile: AgentCapabilityProfile, task: Task) -> Dict[str, Any]:
        """Evaluate how relevant agent's experience is for the task"""
        experience_scores = {
            'domain_experience': 0.5,
            'task_type_experience': 0.5,
            'complexity_experience': 0.5,
            'recent_performance': 0.5
        }
        
        # Analyze experience history
        if agent_profile.experience_history:
            # Domain experience
            domain_tasks = [exp for exp in agent_profile.experience_history 
                          if exp.get('domain') == task.requirements.get('domain')]
            if domain_tasks:
                avg_success = statistics.mean([exp.get('success_rate', 0.5) for exp in domain_tasks])
                experience_scores['domain_experience'] = avg_success
            
            # Task type experience
            type_tasks = [exp for exp in agent_profile.experience_history 
                         if exp.get('task_type') == task.task_type]
            if type_tasks:
                avg_success = statistics.mean([exp.get('success_rate', 0.5) for exp in type_tasks])
                experience_scores['task_type_experience'] = avg_success
            
            # Complexity experience
            complexity_tasks = [exp for exp in agent_profile.experience_history 
                              if exp.get('complexity') == task.complexity_level]
            if complexity_tasks:
                avg_success = statistics.mean([exp.get('success_rate', 0.5) for exp in complexity_tasks])
                experience_scores['complexity_experience'] = avg_success
            
            # Recent performance (last 30 days)
            recent_cutoff = datetime.now() - timedelta(days=30)
            recent_tasks = [exp for exp in agent_profile.experience_history 
                          if exp.get('completion_date', datetime.min) >= recent_cutoff]
            if recent_tasks:
                avg_recent = statistics.mean([exp.get('success_rate', 0.5) for exp in recent_tasks])
                experience_scores['recent_performance'] = avg_recent
        
        # Calculate weighted overall score
        overall_score = sum(
            score * self.experience_factors[factor] 
            for factor, score in experience_scores.items()
        )
        
        return {
            'overall_score': overall_score,
            'experience_breakdown': experience_scores,
            'relevant_experience_count': len([exp for exp in agent_profile.experience_history 
                                            if exp.get('task_type') == task.task_type])
        }
    
    def _predict_task_performance(self, agent_profile: AgentCapabilityProfile, task: Task) -> float:
        """Predict likely performance outcome for agent on task"""
        base_performance = agent_profile.performance_metrics.get('average_success_rate', 0.7)
        
        # Adjust based on skill proficiency
        required_skills = task.requirements.get('required_capabilities', [])
        if required_skills:
            proficiency_scores = []
            for skill in required_skills:
                if skill in agent_profile.proficiency_levels:
                    proficiency_scores.append(agent_profile.proficiency_levels[skill])
                else:
                    proficiency_scores.append(0.3)  # Low proficiency for missing skills
            
            avg_proficiency = statistics.mean(proficiency_scores)
            proficiency_factor = 0.5 + (avg_proficiency * 0.5)  # Scale to 0.5-1.0
        else:
            proficiency_factor = 1.0
        
        # Adjust based on workload
        workload_ratio = agent_profile.current_workload / max(agent_profile.max_capacity, 1)
        workload_factor = 1.0 - (workload_ratio * 0.3)  # Up to 30% penalty for high workload
        
        # Adjust based on learning efficiency for unfamiliar tasks
        familiarity = len([skill for skill in required_skills 
                          if skill in agent_profile.capabilities]) / max(len(required_skills), 1)
        learning_factor = familiarity + ((1 - familiarity) * agent_profile.learning_efficiency)
        
        predicted_performance = base_performance * proficiency_factor * workload_factor * learning_factor
        
        return min(1.0, max(0.1, predicted_performance))
    
    def _assess_agent_availability(self, agent_profile: AgentCapabilityProfile, task: Task) -> float:
        """Assess agent availability for task execution"""
        # Current capacity availability
        capacity_available = (agent_profile.max_capacity - agent_profile.current_workload) / agent_profile.max_capacity
        
        # Time availability (simplified - would check actual schedule in production)
        time_availability = 1.0  # Assume full availability for now
        
        # Urgency consideration
        if task.deadline:
            time_to_deadline = (task.deadline - datetime.now()).total_seconds() / 3600.0
            if time_to_deadline < 4:  # Less than 4 hours
                urgency_factor = 0.8 if capacity_available < 0.3 else 1.0
            else:
                urgency_factor = 1.0
        else:
            urgency_factor = 1.0
        
        availability_score = capacity_available * time_availability * urgency_factor
        
        return min(1.0, max(0.0, availability_score))
    
    def _calculate_composite_compatibility(self, skill_match: Dict, experience_relevance: Dict, 
                                         performance_prediction: float, availability_score: float) -> float:
        """Calculate composite compatibility score"""
        weights = {
            'skill_match': 0.4,
            'experience': 0.25,
            'performance_prediction': 0.2,
            'availability': 0.15
        }
        
        composite_score = (
            skill_match['overall_score'] * weights['skill_match'] +
            experience_relevance['overall_score'] * weights['experience'] +
            performance_prediction * weights['performance_prediction'] +
            availability_score * weights['availability']
        )
        
        return min(1.0, max(0.0, composite_score))
    
    def _calculate_assignment_confidence(self, compatibility_score: float, 
                                       skill_match: Dict, experience_relevance: Dict) -> float:
        """Calculate confidence level for assignment recommendation"""
        base_confidence = compatibility_score
        
        # Increase confidence for exact skill matches
        exact_match_bonus = len(skill_match.get('exact_matches', [])) * 0.1
        
        # Increase confidence for relevant experience
        experience_bonus = min(0.2, experience_relevance.get('relevant_experience_count', 0) * 0.05)
        
        # Decrease confidence for skill gaps
        gap_penalty = len(skill_match.get('gaps', [])) * 0.15
        
        confidence = base_confidence + exact_match_bonus + experience_bonus - gap_penalty
        
        return min(1.0, max(0.2, confidence))
    
    def _generate_assignment_reasoning(self, skill_match: Dict, experience_relevance: Dict,
                                     performance_prediction: float, availability_score: float) -> str:
        """Generate human-readable reasoning for assignment recommendation"""
        reasons = []
        
        # Skill match reasoning
        exact_matches = skill_match.get('exact_matches', [])
        if exact_matches:
            reasons.append(f"Strong skill match with {len(exact_matches)} exact capability matches")
        
        gaps = skill_match.get('gaps', [])
        if gaps:
            reasons.append(f"Missing {len(gaps)} required capabilities: {', '.join(gaps[:3])}")
        
        # Experience reasoning
        experience_score = experience_relevance.get('overall_score', 0.5)
        if experience_score > 0.8:
            reasons.append("Excellent relevant experience")
        elif experience_score < 0.4:
            reasons.append("Limited relevant experience")
        
        # Performance reasoning
        if performance_prediction > 0.8:
            reasons.append("High performance prediction")
        elif performance_prediction < 0.5:
            reasons.append("Lower performance prediction due to workload/unfamiliarity")
        
        # Availability reasoning
        if availability_score < 0.3:
            reasons.append("Limited availability due to current workload")
        elif availability_score > 0.8:
            reasons.append("Good availability for immediate assignment")
        
        return "; ".join(reasons) if reasons else "Standard assignment based on general capabilities"
    
    def _generate_improvement_recommendations(self, agent_profile: AgentCapabilityProfile,
                                           task: Task, skill_match: Dict) -> List[str]:
        """Generate recommendations for improving agent capabilities"""
        recommendations = []
        
        gaps = skill_match.get('gaps', [])
        if gaps:
            recommendations.append(f"Consider training in: {', '.join(gaps[:3])}")
        
        # Check for underutilized capabilities
        agent_skills = set(agent_profile.capabilities)
        required_skills = set(task.requirements.get('required_capabilities', []))
        unused_skills = agent_skills - required_skills
        
        if len(unused_skills) > 3:
            recommendations.append("Agent has additional capabilities that could be leveraged")
        
        # Performance-based recommendations
        if agent_profile.performance_metrics.get('average_success_rate', 0.7) < 0.6:
            recommendations.append("Consider additional training or mentoring to improve success rate")
        
        return recommendations

class TaskDistributionEngine:
    """Main task distribution engine coordinating all components"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'queue_rebalancing_interval': 300,  # 5 minutes
            'max_assignment_attempts': 3,
            'assignment_timeout': 60,  # seconds
            'performance_monitoring_interval': 60
        }
        
        self.task_queue = IntelligentTaskQueue(self.config['queue_rebalancing_interval'])
        self.capability_matching = CapabilityMatchingEngine()
        self.agent_profiles: Dict[str, AgentCapabilityProfile] = {}
        self.workload_monitor = WorkloadMonitor()
        
        self.assignment_history = deque(maxlen=1000)  # Keep last 1000 assignments
        self.system_metrics = {
            'total_assignments': 0,
            'successful_assignments': 0,
            'failed_assignments': 0,
            'average_assignment_time': 0.0,
            'average_compatibility_score': 0.0
        }
        
        self.logger = logging.getLogger("TaskDistributionEngine")
    
    def register_agent(self, agent_profile: AgentCapabilityProfile) -> bool:
        """Register an agent profile with the distribution engine"""
        try:
            self.agent_profiles[agent_profile.agent_id] = agent_profile
            self.workload_monitor.add_agent(agent_profile)
            self.logger.info(f"Agent {agent_profile.agent_id} registered with distribution engine")
            return True
        except Exception as e:
            self.logger.error(f"Error registering agent: {str(e)}")
            return False
    
    def submit_task(self, task: Task, system_context: Dict[str, Any] = None) -> bool:
        """Submit task to distribution queue"""
        if system_context is None:
            system_context = self._get_current_system_context()
        
        return self.task_queue.enqueue_task(task, system_context)
    
    def find_optimal_assignment(self, max_candidates: int = 5) -> Optional[Tuple[Task, str, TaskAgentCompatibility]]:
        """Find optimal task-agent assignment"""
        try:
            # Get available agents
            available_agents = self._get_available_agents()
            if not available_agents:
                return None
            
            # Get current system context
            system_context = self._get_current_system_context()
            
            # Try to find assignment for each available agent
            best_assignments = []
            
            for agent_profile in available_agents[:max_candidates]:
                # Try to get optimal task for this agent
                optimal_task = self.task_queue.dequeue_optimal_task(agent_profile, system_context)
                
                if optimal_task:
                    # Evaluate compatibility
                    compatibility = self.capability_matching.evaluate_agent_task_compatibility(
                        agent_profile, optimal_task
                    )
                    
                    best_assignments.append((optimal_task, agent_profile.agent_id, compatibility))
                    
                    # Put task back if this isn't the final selection
                    # (In production, would implement more sophisticated selection)
            
            if best_assignments:
                # Select best assignment based on compatibility score
                best_assignment = max(best_assignments, key=lambda x: x[2].compatibility_score)
                
                # Update assignment history and metrics
                self._record_assignment(best_assignment)
                
                return best_assignment
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding optimal assignment: {str(e)}")
            return None
    
    def _get_available_agents(self) -> List[AgentCapabilityProfile]:
        """Get list of available agents for assignment"""
        available = []
        for agent_profile in self.agent_profiles.values():
            if agent_profile.current_workload < agent_profile.max_capacity:
                available.append(agent_profile)
        
        # Sort by availability score (most available first)
        available.sort(key=lambda x: (x.max_capacity - x.current_workload) / x.max_capacity, reverse=True)
        
        return available
    
    def _get_current_system_context(self) -> Dict[str, Any]:
        """Get current system context for decision making"""
        total_agents = len(self.agent_profiles)
        busy_agents = sum(1 for profile in self.agent_profiles.values() 
                         if profile.current_workload >= profile.max_capacity * 0.8)
        
        system_load = busy_agents / max(total_agents, 1)
        
        # Get available expertise
        available_expertise = {}
        for profile in self.agent_profiles.values():
            if profile.current_workload < profile.max_capacity:
                for capability in profile.capabilities:
                    available_expertise[capability] = available_expertise.get(capability, 0) + 1
        
        return {
            'system_load': system_load,
            'total_agents': total_agents,
            'available_agents': total_agents - busy_agents,
            'available_expertise': available_expertise,
            'queue_size': len(self.task_queue._priority_queue),
            'average_wait_time': self.task_queue.performance_metrics['average_wait_time']
        }
    
    def _record_assignment(self, assignment: Tuple[Task, str, TaskAgentCompatibility]) -> None:
        """Record assignment for metrics and learning"""
        task, agent_id, compatibility = assignment
        
        assignment_record = {
            'timestamp': datetime.now(),
            'task_id': task.task_id,
            'agent_id': agent_id,
            'compatibility_score': compatibility.compatibility_score,
            'assignment_reasoning': compatibility.assignment_reasoning
        }
        
        self.assignment_history.append(assignment_record)
        
        # Update metrics
        self.system_metrics['total_assignments'] += 1
        
        # Update average compatibility score
        total = self.system_metrics['total_assignments']
        current_avg = self.system_metrics['average_compatibility_score']
        new_avg = ((current_avg * (total - 1)) + compatibility.compatibility_score) / total
        self.system_metrics['average_compatibility_score'] = new_avg
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            'queue_status': self.task_queue.get_queue_status(),
            'agent_count': len(self.agent_profiles),
            'available_agents': len(self._get_available_agents()),
            'system_metrics': self.system_metrics,
            'workload_distribution': self.workload_monitor.get_workload_distribution(),
            'recent_assignments': list(self.assignment_history)[-10:],  # Last 10 assignments
            'system_context': self._get_current_system_context()
        }

class WorkloadMonitor:
    """Monitor and analyze agent workload distribution"""
    
    def __init__(self):
        self.agent_workloads: Dict[str, WorkloadDistribution] = {}
        self.historical_data = deque(maxlen=1000)
    
    def add_agent(self, agent_profile: AgentCapabilityProfile) -> None:
        """Add agent to workload monitoring"""
        workload = WorkloadDistribution(
            agent_id=agent_profile.agent_id,
            current_tasks=[],
            utilization_percentage=0.0,
            efficiency_rating=agent_profile.performance_metrics.get('efficiency_rating', 0.8),
            projected_completion_times={},
            capacity_remaining=agent_profile.max_capacity,
            overload_risk=0.0
        )
        self.agent_workloads[agent_profile.agent_id] = workload
    
    def update_agent_workload(self, agent_id: str, current_tasks: List[str], 
                            projected_completions: Dict[str, datetime] = None) -> None:
        """Update agent workload information"""
        if agent_id in self.agent_workloads:
            workload = self.agent_workloads[agent_id]
            workload.current_tasks = current_tasks
            workload.utilization_percentage = len(current_tasks) / max(workload.capacity_remaining + len(current_tasks), 1) * 100
            
            if projected_completions:
                workload.projected_completion_times = projected_completions
            
            # Calculate overload risk
            if len(current_tasks) > workload.capacity_remaining:
                workload.overload_risk = min(1.0, (len(current_tasks) - workload.capacity_remaining) / workload.capacity_remaining)
            else:
                workload.overload_risk = 0.0
    
    def get_workload_distribution(self) -> Dict[str, Any]:
        """Get workload distribution across all agents"""
        if not self.agent_workloads:
            return {'message': 'No agents registered'}
        
        utilizations = [w.utilization_percentage for w in self.agent_workloads.values()]
        overload_risks = [w.overload_risk for w in self.agent_workloads.values()]
        
        return {
            'total_agents': len(self.agent_workloads),
            'average_utilization': statistics.mean(utilizations) if utilizations else 0,
            'utilization_std_dev': statistics.stdev(utilizations) if len(utilizations) > 1 else 0,
            'overloaded_agents': sum(1 for risk in overload_risks if risk > 0.5),
            'agent_details': [
                {
                    'agent_id': agent_id,
                    'utilization': workload.utilization_percentage,
                    'current_tasks': len(workload.current_tasks),
                    'efficiency': workload.efficiency_rating,
                    'overload_risk': workload.overload_risk
                }
                for agent_id, workload in self.agent_workloads.items()
            ]
        }

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create task distribution engine
    distribution_engine = TaskDistributionEngine()
    
    # Create sample agent profiles
    marketing_profile = AgentCapabilityProfile(
        agent_id="marketing_001",
        capabilities=["content_creation", "social_media", "analytics", "creativity"],
        proficiency_levels={
            "content_creation": 0.9,
            "social_media": 0.8,
            "analytics": 0.7,
            "creativity": 0.85
        },
        specializations=["digital_marketing", "brand_development"],
        experience_history=[
            {"task_type": "marketing_campaign", "success_rate": 0.9, "completion_date": datetime.now() - timedelta(days=5)},
            {"task_type": "content_creation", "success_rate": 0.95, "completion_date": datetime.now() - timedelta(days=10)}
        ],
        performance_metrics={"average_success_rate": 0.88, "efficiency_rating": 0.82},
        current_workload=1,
        max_capacity=3,
        availability_schedule={}
    )
    
    technical_profile = AgentCapabilityProfile(
        agent_id="technical_001",
        capabilities=["programming", "system_design", "debugging", "testing"],
        proficiency_levels={
            "programming": 0.95,
            "system_design": 0.85,
            "debugging": 0.9,
            "testing": 0.8
        },
        specializations=["web_development", "api_design"],
        experience_history=[
            {"task_type": "software_development", "success_rate": 0.92, "completion_date": datetime.now() - timedelta(days=3)},
            {"task_type": "system_integration", "success_rate": 0.87, "completion_date": datetime.now() - timedelta(days=7)}
        ],
        performance_metrics={"average_success_rate": 0.91, "efficiency_rating": 0.89},
        current_workload=2,
        max_capacity=4,
        availability_schedule={}
    )
    
    # Register agents
    distribution_engine.register_agent(marketing_profile)
    distribution_engine.register_agent(technical_profile)
    
    # Create sample tasks
    marketing_task = Task(
        task_id="task_marketing_001",
        title="Create social media campaign",
        description="Develop comprehensive social media campaign for product launch",
        task_type="marketing_campaign",
        complexity_level="medium",
        priority_score=75,
        requirements={
            "required_capabilities": ["content_creation", "social_media", "analytics"],
            "client_tier": "premium",
            "strategic_importance": "high"
        },
        deliverables={},
        creation_date=datetime.now(),
        deadline=datetime.now() + timedelta(days=2),
        revenue_potential=2500
    )
    
    technical_task = Task(
        task_id="task_technical_001",
        title="Develop API integration",
        description="Create API integration for customer data synchronization",
        task_type="software_development",
        complexity_level="high",
        priority_score=85,
        requirements={
            "required_capabilities": ["programming", "system_design", "testing"],
            "client_tier": "enterprise",
            "strategic_importance": "critical"
        },
        deliverables={},
        creation_date=datetime.now(),
        deadline=datetime.now() + timedelta(hours=8),
        revenue_potential=5000
    )
    
    # Submit tasks
    print("Submitting tasks to distribution engine...")
    distribution_engine.submit_task(marketing_task)
    distribution_engine.submit_task(technical_task)
    
    # Find optimal assignments
    print("\nFinding optimal assignments...")
    assignment1 = distribution_engine.find_optimal_assignment()
    if assignment1:
        task, agent_id, compatibility = assignment1
        print(f"Assignment 1: Task {task.task_id} -> Agent {agent_id}")
        print(f"Compatibility Score: {compatibility.compatibility_score:.3f}")
        print(f"Reasoning: {compatibility.assignment_reasoning}")
    
    assignment2 = distribution_engine.find_optimal_assignment()
    if assignment2:
        task, agent_id, compatibility = assignment2
        print(f"\nAssignment 2: Task {task.task_id} -> Agent {agent_id}")
        print(f"Compatibility Score: {compatibility.compatibility_score:.3f}")
        print(f"Reasoning: {compatibility.assignment_reasoning}")
    
    # Get system status
    print("\nSystem Status:")
    status = distribution_engine.get_system_status()
    print(f"Queue Size: {status['queue_status']['queue_size']}")
    print(f"Available Agents: {status['available_agents']}")
    print(f"Average Compatibility Score: {status['system_metrics']['average_compatibility_score']:.3f}")
    print(f"Total Assignments: {status['system_metrics']['total_assignments']}")
