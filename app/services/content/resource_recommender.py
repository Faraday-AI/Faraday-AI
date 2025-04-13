from typing import List, Dict, Optional, Set
import networkx as nx
from datetime import datetime
from pydantic import BaseModel
import numpy as np

class Resource(BaseModel):
    id: str
    title: str
    description: str
    url: Optional[str] = None
    type: str  # video, article, exercise, etc.
    topics: List[str]
    difficulty: float
    prerequisites: List[str] = []
    completion_time: int  # estimated minutes to complete
    created_at: datetime = datetime.now()
    engagement_score: float = 0.0
    completion_rate: float = 0.0
    user_ratings: Dict[str, float] = {}  # user_id -> rating

class ResourceRecommender:
    def __init__(self):
        self.knowledge_graph = nx.DiGraph()
        self.resources: Dict[str, Resource] = {}
        self.topic_resources: Dict[str, Set[str]] = {}  # topic -> set of resource_ids
        self.user_history: Dict[str, List[str]] = {}  # user_id -> list of resource_ids
        
    def add_resource(self, resource: Resource) -> None:
        """Add a new resource to the recommender system"""
        self.resources[resource.id] = resource
        
        # Add to topic index
        for topic in resource.topics:
            if topic not in self.topic_resources:
                self.topic_resources[topic] = set()
            self.topic_resources[topic].add(resource.id)
        
        # Update knowledge graph
        self.knowledge_graph.add_node(resource.id, 
                                    type='resource',
                                    difficulty=resource.difficulty)
        
        # Add prerequisite relationships
        for prereq in resource.prerequisites:
            if prereq in self.resources:
                self.knowledge_graph.add_edge(prereq, resource.id, 
                                           type='prerequisite')
    
    def update_user_history(self, user_id: str, resource_id: str) -> None:
        """Update a user's learning history"""
        if user_id not in self.user_history:
            self.user_history[user_id] = []
        if resource_id not in self.user_history[user_id]:
            self.user_history[user_id].append(resource_id)
    
    def add_user_rating(self, user_id: str, resource_id: str, rating: float) -> None:
        """Add or update a user's rating for a resource"""
        if resource_id in self.resources:
            self.resources[resource_id].user_ratings[user_id] = rating
            self._update_resource_scores(resource_id)
    
    def _update_resource_scores(self, resource_id: str) -> None:
        """Update engagement and completion scores for a resource"""
        resource = self.resources[resource_id]
        ratings = list(resource.user_ratings.values())
        
        if ratings:
            resource.engagement_score = sum(ratings) / len(ratings)
            resource.completion_rate = sum(1 for r in ratings if r >= 4.0) / len(ratings)
    
    def get_prerequisites(self, resource_id: str) -> List[Resource]:
        """Get all prerequisites for a resource"""
        if resource_id not in self.knowledge_graph:
            return []
            
        prereq_ids = [n for n in self.knowledge_graph.predecessors(resource_id)
                     if self.knowledge_graph[n][resource_id]['type'] == 'prerequisite']
        return [self.resources[pid] for pid in prereq_ids if pid in self.resources]
    
    def recommend_resources(self, 
                          user_id: str,
                          topics: List[str],
                          difficulty_range: tuple[float, float] = (0.0, 1.0),
                          max_resources: int = 5) -> List[Resource]:
        """Recommend resources based on user history and topics"""
        candidate_resources = set()
        
        # Collect resources for requested topics
        for topic in topics:
            if topic in self.topic_resources:
                candidate_resources.update(self.topic_resources[topic])
        
        if not candidate_resources:
            return []
        
        # Filter by difficulty
        min_diff, max_diff = difficulty_range
        candidates = [
            rid for rid in candidate_resources
            if min_diff <= self.resources[rid].difficulty <= max_diff
        ]
        
        if not candidates:
            return []
        
        # Score candidates
        scores = []
        user_history = set(self.user_history.get(user_id, []))
        
        for rid in candidates:
            resource = self.resources[rid]
            
            # Skip if already completed
            if rid in user_history:
                continue
                
            # Calculate score based on multiple factors
            prereq_completion = self._calculate_prereq_completion(user_id, rid)
            topic_relevance = len(set(resource.topics) & set(topics)) / len(topics)
            difficulty_score = 1.0 - abs(resource.difficulty - 0.5)  # Prefer moderate difficulty
            
            score = (
                0.3 * resource.engagement_score +
                0.2 * resource.completion_rate +
                0.2 * prereq_completion +
                0.2 * topic_relevance +
                0.1 * difficulty_score
            )
            
            scores.append((score, rid))
        
        # Sort by score and return top resources
        scores.sort(reverse=True)
        return [
            self.resources[rid]
            for _, rid in scores[:max_resources]
        ]
    
    def _calculate_prereq_completion(self, user_id: str, resource_id: str) -> float:
        """Calculate what fraction of prerequisites the user has completed"""
        prereqs = self.get_prerequisites(resource_id)
        if not prereqs:
            return 1.0
            
        user_history = set(self.user_history.get(user_id, []))
        completed_prereqs = sum(1 for p in prereqs if p.id in user_history)
        return completed_prereqs / len(prereqs)
    
    def get_learning_path(self, 
                         start_resources: List[str],
                         target_resources: List[str],
                         max_length: int = 10) -> List[Resource]:
        """Find a learning path from start resources to target resources"""
        if not (all(rid in self.knowledge_graph for rid in start_resources) and
                all(rid in self.knowledge_graph for rid in target_resources)):
            return []
        
        # Try to find shortest path between any start and target
        all_paths = []
        for start in start_resources:
            for target in target_resources:
                try:
                    path = nx.shortest_path(self.knowledge_graph, start, target)
                    if len(path) <= max_length:
                        all_paths.append(path)
                except nx.NetworkXNoPath:
                    continue
        
        if not all_paths:
            return []
        
        # Select shortest valid path
        best_path = min(all_paths, key=len)
        return [self.resources[rid] for rid in best_path if rid in self.resources] 

