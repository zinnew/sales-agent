# AI Sales Research Agent 

An agentic AI pipeline that takes a company name and automatically researches it, identifies sales opportunities, finds decision makers, and generates personalized outreach, all exposed as a FastAPI endpoint. 

## How it works

The agent runs through 4 steps in sequence, powered by LangGraph: 
- Research node (Tavily web search + Pinecone vector store)
- Summarize node (LLM extracts overview + opportunities)
- Identify node (LLM finds decision makers)
- Outreach node (LLM writes, email, LinkedIn message, talking points)

If the research step gathers fewer than 3 results, the graph automatically retries before moving on. 

## Tech stack
| Tool | Purpose |
|------|---------|
| LangGraph | Orchestrates the agent pipeline |
| OpenAI gpt-4o-mini | LLM for summarizing, identifying, and writing outreach |
| OpenAI text-embedding-3-small | Converts text to vectors for Pinecone |
| Tavily | Web search API built for LLMs |
| Pinecone | Vector database for cachin research |
| FastAPI | Serves the agennt as an HTTP API |
