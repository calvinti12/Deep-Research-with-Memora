#!/usr/bin/env python3
"""
Deep Research Agent using Memora for persistent memory management.
Conducts comprehensive research by integrating web search with semantic memory.
"""

import os
import json
import sys
from dotenv import load_dotenv
from typing import Optional
import anthropic
from rich import print as rprint
from rich.markdown import Markdown
from research_tools import (
    MemoraMemoryManager,
    setup_web_search_tools,
    ResearchOrchestrator,
)

# Load environment variables
load_dotenv()

def main():
    """Main entry point for the deep research agent."""
    
    # Initialize clients
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Initialize memory manager with Memora
    db_path = os.getenv("MEMORA_DB_PATH", "~/.local/share/memora/memories.db")
    memory_manager = MemoraMemoryManager(db_path=db_path)
    
    # Initialize web search tools
    web_tools = setup_web_search_tools()
    
    # Initialize research orchestrator
    orchestrator = ResearchOrchestrator(
        client=client,
        memory_manager=memory_manager,
        web_tools=web_tools
    )
    
    # Research task
    TASK = """
    Please write a comprehensive research report on PostgreSQL and its ecosystem.
    Include information about:
    1. PostgreSQL architecture and core features
    2. Popular extensions and tools in the ecosystem
    3. Performance optimization strategies
    4. Security best practices
    5. Use cases and industry adoption
    
    Provide a detailed, well-cited report with references to sources.
    """
    
    print("[bold cyan]🔍 Starting Deep Research Agent[/bold cyan]")
    print(f"[yellow]Task:[/yellow] {TASK}\n")
    
    # Execute research
    report = orchestrator.conduct_research(task=TASK)
    
    # Display and save report
    print("\n[bold green]📊 Research Report[/bold green]\n")
    md = Markdown(report)
    rprint(md)
    
    # Save report to memory
    memory_manager.save_research_report(report, "PostgreSQL Research")
    
    print("\n[bold green]✅ Research complete![/bold green]")
    print(f"[cyan]Report saved to Memora with semantic indexing[/cyan]")

if __name__ == "__main__":
    main()
