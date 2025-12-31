"""
Conversation Memory Manager
Maintains conversation history, context, and enables topic switching
Ensures traceability and prevents hallucination
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class ConversationTurn:
    """Single turn in conversation"""
    turn_id: int
    timestamp: datetime
    user_question: str
    ai_answer: str
    data_sources: List[str] = field(default_factory=list)
    detected_intent: str = ""
    detected_category: Optional[str] = None
    detected_region: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'turn_id': self.turn_id,
            'timestamp': self.timestamp.isoformat(),
            'user_question': self.user_question,
            'ai_answer': self.ai_answer,
            'data_sources': self.data_sources,
            'detected_intent': self.detected_intent,
            'detected_category': self.detected_category,
            'detected_region': self.detected_region,
            'metadata': self.metadata
        }


class ConversationMemory:
    """
    Manages conversation history and context
    Enables:
    - Full conversation recall
    - Topic switching and returning
    - Context-aware responses
    - Traceability of all answers
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize conversation memory
        
        Args:
            max_history: Maximum number of turns to keep in memory
        """
        self.conversation_history: List[ConversationTurn] = []
        self.max_history = max_history
        self.current_turn_id = 0
        self.session_start = datetime.now()
        
        # Context tracking
        self.current_context = {
            'active_category': None,
            'active_region': None,
            'active_supplier': None,
            'active_topic': None
        }
        
        # Topic history for easy switching
        self.topic_history: List[str] = []
    
    def add_turn(
        self,
        user_question: str,
        ai_answer: str,
        data_sources: List[str],
        detected_intent: str = "",
        detected_category: Optional[str] = None,
        detected_region: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationTurn:
        """
        Add a new conversation turn
        
        Args:
            user_question: User's question
            ai_answer: AI's answer
            data_sources: List of data sources used (for traceability)
            detected_intent: Detected intent (spend, risk, supplier, etc.)
            detected_category: Detected category if any
            detected_region: Detected region if any
            metadata: Additional metadata
            
        Returns:
            The created ConversationTurn
        """
        self.current_turn_id += 1
        
        turn = ConversationTurn(
            turn_id=self.current_turn_id,
            timestamp=datetime.now(),
            user_question=user_question,
            ai_answer=ai_answer,
            data_sources=data_sources,
            detected_intent=detected_intent,
            detected_category=detected_category,
            detected_region=detected_region,
            metadata=metadata or {}
        )
        
        self.conversation_history.append(turn)
        
        # Update context
        if detected_category:
            self.current_context['active_category'] = detected_category
        if detected_region:
            self.current_context['active_region'] = detected_region
        if detected_intent:
            self.current_context['active_topic'] = detected_intent
            if detected_intent not in self.topic_history:
                self.topic_history.append(detected_intent)
        
        # Trim history if needed
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        return turn
    
    def get_recent_context(self, n_turns: int = 5) -> str:
        """
        Get recent conversation context for context-aware responses
        
        Args:
            n_turns: Number of recent turns to include
            
        Returns:
            Formatted context string
        """
        if not self.conversation_history:
            return "No previous conversation."
        
        recent_turns = self.conversation_history[-n_turns:]
        
        context = "Recent Conversation:\n"
        for turn in recent_turns:
            context += f"\nTurn {turn.turn_id}:\n"
            context += f"  User: {turn.user_question}\n"
            context += f"  Intent: {turn.detected_intent}\n"
            if turn.detected_category:
                context += f"  Category: {turn.detected_category}\n"
            if turn.detected_region:
                context += f"  Region: {turn.detected_region}\n"
        
        return context
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current conversation context"""
        return {
            **self.current_context,
            'turn_count': self.current_turn_id,
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'topics_discussed': self.topic_history
        }
    
    def find_similar_questions(self, question: str, threshold: float = 0.7) -> List[ConversationTurn]:
        """
        Find similar questions asked before
        Helps with topic switching and returning to previous topics
        
        Args:
            question: Current question
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar conversation turns
        """
        q_lower = question.lower()
        similar_turns = []
        
        for turn in self.conversation_history:
            # Simple keyword-based similarity
            turn_q_lower = turn.user_question.lower()
            
            # Extract keywords
            q_words = set(q_lower.split())
            turn_words = set(turn_q_lower.split())
            
            # Calculate Jaccard similarity
            if q_words and turn_words:
                intersection = len(q_words & turn_words)
                union = len(q_words | turn_words)
                similarity = intersection / union
                
                if similarity >= threshold:
                    similar_turns.append(turn)
        
        return similar_turns
    
    def get_turn_by_id(self, turn_id: int) -> Optional[ConversationTurn]:
        """Get a specific conversation turn by ID"""
        for turn in self.conversation_history:
            if turn.turn_id == turn_id:
                return turn
        return None
    
    def get_turns_by_category(self, category: str) -> List[ConversationTurn]:
        """Get all turns related to a specific category"""
        return [
            turn for turn in self.conversation_history
            if turn.detected_category and turn.detected_category.lower() == category.lower()
        ]
    
    def get_turns_by_intent(self, intent: str) -> List[ConversationTurn]:
        """Get all turns with a specific intent"""
        return [
            turn for turn in self.conversation_history
            if turn.detected_intent and intent.lower() in turn.detected_intent.lower()
        ]
    
    def clear_context(self):
        """Clear current context (useful for explicit topic switches)"""
        self.current_context = {
            'active_category': None,
            'active_region': None,
            'active_supplier': None,
            'active_topic': None
        }
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the entire conversation"""
        if not self.conversation_history:
            return "No conversation history."
        
        summary = f"📊 **CONVERSATION SUMMARY**\n\n"
        summary += f"Session Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Total Turns: {self.current_turn_id}\n"
        summary += f"Topics Discussed: {', '.join(self.topic_history) if self.topic_history else 'None'}\n\n"
        
        # Category breakdown
        categories = {}
        for turn in self.conversation_history:
            if turn.detected_category:
                categories[turn.detected_category] = categories.get(turn.detected_category, 0) + 1
        
        if categories:
            summary += "**Categories Explored:**\n"
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                summary += f"- {cat}: {count} questions\n"
        
        return summary
    
    def export_conversation(self, filepath: str):
        """Export conversation to JSON file"""
        export_data = {
            'session_start': self.session_start.isoformat(),
            'total_turns': self.current_turn_id,
            'topics': self.topic_history,
            'conversation': [turn.to_dict() for turn in self.conversation_history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def get_traceability_report(self, turn_id: Optional[int] = None) -> str:
        """
        Get full traceability report for a specific turn or all turns
        Shows exactly what data sources were used
        
        Args:
            turn_id: Specific turn ID, or None for all turns
            
        Returns:
            Formatted traceability report
        """
        if turn_id:
            turn = self.get_turn_by_id(turn_id)
            if not turn:
                return f"Turn {turn_id} not found."
            turns_to_report = [turn]
        else:
            turns_to_report = self.conversation_history
        
        report = "🔍 **TRACEABILITY REPORT**\n\n"
        
        for turn in turns_to_report:
            report += f"**Turn {turn.turn_id}** ({turn.timestamp.strftime('%H:%M:%S')})\n"
            report += f"Question: {turn.user_question}\n"
            report += f"Intent: {turn.detected_intent}\n"
            
            if turn.data_sources:
                report += "Data Sources Used:\n"
                for source in turn.data_sources:
                    report += f"  ✓ {source}\n"
            else:
                report += "Data Sources: None (General response)\n"
            
            if turn.detected_category:
                report += f"Category Context: {turn.detected_category}\n"
            if turn.detected_region:
                report += f"Region Context: {turn.detected_region}\n"
            
            report += "\n" + "-" * 60 + "\n\n"
        
        return report


# Example usage
if __name__ == "__main__":
    # Create memory instance
    memory = ConversationMemory()
    
    # Simulate conversation
    memory.add_turn(
        user_question="What's our total spend?",
        ai_answer="Total spend is $147M",
        data_sources=["spend_data.csv", "regional_summary"],
        detected_intent="spend_analysis"
    )
    
    memory.add_turn(
        user_question="How much did we spend on Rice Bran Oil?",
        ai_answer="Rice Bran Oil spend is $2.05M",
        data_sources=["spend_data.csv (filtered by category)"],
        detected_intent="spend_analysis",
        detected_category="Rice Bran Oil"
    )
    
    memory.add_turn(
        user_question="What are the risks?",
        ai_answer="3 risks detected...",
        data_sources=["rule_results", "risk_register.csv"],
        detected_intent="risk_analysis"
    )
    
    # Now switch back to previous topic
    memory.add_turn(
        user_question="Back to Rice Bran Oil - who are the suppliers?",
        ai_answer="Top suppliers: Malaya Agri Oils, Borneo Nutrients",
        data_sources=["spend_data.csv (filtered by category)", "supplier_master.csv"],
        detected_intent="supplier_analysis",
        detected_category="Rice Bran Oil"
    )
    
    # Print summary
    print(memory.get_conversation_summary())
    print("\n")
    print(memory.get_traceability_report())
