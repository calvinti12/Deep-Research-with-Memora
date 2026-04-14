"""
Research tools and utilities for deep research with Memora memory.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import anthropic
from memora import MemoryStore, MemorySearchConfig

@dataclass
class ResearchPlan:
    """Data class for research plan"""
    topic: str
    steps: List[str]
    status: Dict[str, bool]
    findings: Dict[str, str]
    
    def to_markdown(self) -> str:
        """Convert plan to markdown"""
        md = f"# Research Plan: {self.topic}\n\n"
        md += "## Steps:\n"
        for i, step in enumerate(self.steps, 1):
            status = "✅" if self.status.get(step, False) else "⏳"
            md += f"- {status} Step {i}: {step}\n"
        
        if self.findings:
            md += "\n## Findings:\n"
            for step, finding in self.findings.items():
                md += f"### {step}\n{finding}\n\n"
        
        return md


class MemoraMemoryManager:
    """Manages memory operations using Memora."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize Memora memory manager."""
        if db_path:
            db_path = os.path.expanduser(db_path)
        
        self.store = MemoryStore(db_path=db_path)
        self.research_plans: Dict[str, ResearchPlan] = {}
    
    def create_research_plan(self, topic: str, steps: List[str]) -> ResearchPlan:
        """Create and store a research plan."""
        plan = ResearchPlan(
            topic=topic,
            steps=steps,
            status={step: False for step in steps},
            findings={}
        )
        
        # Save to Memora with semantic indexing
        plan_content = plan.to_markdown()
        self.store.create_memory(
            content=plan_content,
            tags=[f"research-plan", f"topic:{topic.lower()}"],
            section="research_plans"
        )
        
        self.research_plans[topic] = plan
        return plan
    
    def update_research_progress(
        self,
        topic: str,
        step: str,
        finding: str,
        completed: bool = True
    ) -> None:
        """Update research progress in memory."""
        if topic in self.research_plans:
            plan = self.research_plans[topic]
            plan.status[step] = completed
            plan.findings[step] = finding
            
            # Update in Memora
            updated_content = plan.to_markdown()
            memories = self.store.search(
                query=f"Research Plan: {topic}",
                tags=[f"research-plan", f"topic:{topic.lower()}"]
            )
            
            if memories:
                self.store.update_memory(
                    memory_id=memories[0].id,
                    content=updated_content
                )
    
    def save_research_report(self, content: str, topic: str) -> str:
        """Save research report to Memora."""
        memory_id = self.store.create_memory(
            content=f"# Research Report: {topic}\n\n{content}",
            tags=["research-report", f"topic:{topic.lower()}"],
            section="research_reports"
        )
        return memory_id
    
    def search_related_research(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for related research in memory."""
        results = self.store.search(query=query, limit=limit)
        return [
            {
                "id": r.id,
                "content": r.content,
                "tags": r.tags,
                "score": r.similarity_score
            }
            for r in results
        ]
    
    def get_research_context(self, topic: str) -> str:
        """Get accumulated knowledge on a topic from memory."""
        results = self.search_related_research(topic, limit=3)
        
        if not results:
            return ""
        
        context = "## Previously Research Information:\n\n"
        for result in results:
            context += f"### From {result['tags']}\n{result['content']}\n\n"
        
        return context


def setup_web_search_tools() -> List[Dict[str, Any]]:
    """Set up web search tools (Exa or similar)."""
    tools = [
        {
            "name": "web_search",
            "description": "Search the web for information on a topic",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "web_crawl",
            "description": "Crawl and extract content from a specific URL",
            "input_schema": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to crawl"
                    }
                },
                "required": ["url"]
            }
        }
    ]
    return tools


def format_memory_context(memories: List[Dict]) -> str:
    """Format memory search results as context."""
    if not memories:
        return ""
    
    context = "## Relevant Prior Research:\n\n"
    for memory in memories:
        context += f"- **{memory.get('tags', 'unknown')}**: {memory['content'][:200]}...\n"
    
    return context


class ResearchOrchestrator:
    """Orchestrates the research process."""
    
    def __init__(self, client: anthropic.Anthropic, memory_manager: MemoraMemoryManager, web_tools: List[Dict]):
        """Initialize research orchestrator."""
        self.client = client
        self.memory = memory_manager
        self.web_tools = web_tools
        self.model = "claude-3-5-sonnet-20241022"
    
    def conduct_research(self, task: str) -> str:
        """Conduct comprehensive research on a topic."""
        
        # Extract topic from task
        topic = self._extract_topic(task)
        
        # Get prior research context from Memora
        prior_context = self.memory.get_research_context(topic)
        
        # Create system prompt with research instructions
        system_prompt = self._create_system_prompt(prior_context)
        
        # Initialize messages
        messages = [
            {
                "role": "user",
                "content": task
            }
        ]
        
        # Conduct research through agentic loop
        final_report = self._agentic_research_loop(
            system_prompt=system_prompt,
            messages=messages,
            task=task,
            topic=topic
        )
        
        return final_report
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        words = text.lower().split()
        # Return first capitalized phrase or common topic
        if len(words) > 1:
            return " ".join(words[:3])
        return words[0]
    
    def _create_system_prompt(self, prior_context: str) -> str:
        """Create comprehensive system prompt for research."""
        return f"""You are Deep Thought, an advanced research agent specializing in comprehensive, 
in-depth analysis. Your role is to conduct thorough research by:

1. **Creating Research Plans**: Break down complex topics into logical research steps
2. **Web Research**: Use web search and crawling tools to gather information
3. **Memory Integration**: Build on previous research and cross-reference findings
4. **Analysis**: Synthesize information into coherent, well-cited reports
5. **Quality**: Ensure accuracy, completeness, and proper attribution

{prior_context if prior_context else ""}

Your Research Methodology:
- Start by creating a detailed research plan with specific steps
- Execute each step systematically, searching for relevant information
- Cross-validate findings from multiple sources
- Build a knowledge graph of related concepts
- Synthesize into a comprehensive final report
- Include proper citations and source attribution

Research Report Format:
- Use clear markdown formatting
- Include executive summary
- Organize by key themes or topics
- Provide detailed analysis with citations
- Include key insights and conclusions
- Note any limitations or uncertainties
- Suggest areas for further research

Be thorough, systematic, and comprehensive in your research."""
    
    def _agentic_research_loop(self, system_prompt: str, messages: List[Dict], task: str, topic: str) -> str:
        """Run agentic loop for research."""
        
        max_iterations = 10
        iteration = 0
        plan = None
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=self.web_tools + [
                    {
                        "name": "create_plan",
                        "description": "Create a research plan",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "steps": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of research steps"
                                }
                            },
                            "required": ["steps"]
                        }
                    },
                    {
                        "name": "finalize_report",
                        "description": "Finalize and submit the research report",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "report": {
                                    "type": "string",
                                    "description": "Final research report in markdown"
                                }
                            },
                            "required": ["report"]
                        }
                    }
                ],
                messages=messages
            )
            
            # Process response
            if response.stop_reason == "end_turn":
                # Extract final text if no tool was used
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                
                if final_text:
                    return final_text
            
            elif response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        
                        # Handle different tools
                        if tool_name == "create_plan":
                            steps = tool_input.get("steps", [])
                            plan = self.memory.create_research_plan(topic, steps)
                            result = f"Plan created with {len(steps)} steps"
                        
                        elif tool_name == "web_search":
                            # Simulated web search
                            result = f"Search results for: {tool_input.get('query')}\n[Search results would be retrieved here]"
                        
                        elif tool_name == "web_crawl":
                            # Simulated web crawl
                            result = f"Content from {tool_input.get('url')}:\n[Crawled content would appear here]"
                        
                        elif tool_name == "finalize_report":
                            return tool_input.get("report", "")
                        
                        else:
                            result = f"Tool {tool_name} executed"
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                # Add assistant response and tool results to messages
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
        
        # Fallback if loop exits without finalization
        return "Research completed. Final report generation in progress."
