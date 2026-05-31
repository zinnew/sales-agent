#shared state dict - the data container that flows through every node in the graph 

from typing import TypedDict

class AgentState(TypedDict): 
    company_name: str #the input to the agent
    raw_research: list[str] #list of raw text snippets from research node
    summary: str #output from summarize node 
    opportunities: list[str] #list of opportunities 
    decision_makers: list[dict] #list of people to contact
    outreach: dict #final output 