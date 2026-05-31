#LangGraph wiring - wireles all the nodes together into a LangGraph pipeline 

from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.nodes import research_node, summarize_node, identify_node, outreach_node


def check_research_quality(state: AgentState) -> str: 
    #simple check to see if research node found enough information to move on 
    if len(state["raw_research"]) < 3: 
        #if less than 3 research snippets, go back and try to find more
        return "retry"
    #enough data collected, move on to summarization
    return "sufficient"


def build_graph(): 
    #create a new graph that uses AgentState as its shared data container 
    graph = StateGraph(AgentState)

    #add all the nodes to the graph
    graph.add_node("research", research_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("identify", identify_node)
    graph.add_node("outreach", outreach_node)

    #define where the graph starts 
    graph.set_entry_point("research")

    #add conditional edges from research node based on the quality of the research
    graph.add_conditional_edges("research", check_research_quality, {
        "sufficient": "summarize", 
        "retry": "research"
    })

    #add edges to wire the rest of the nodes together in a linear fashion
    graph.add_edge("summarize", "identify")
    graph.add_edge("identify", "outreach")
    graph.add_edge("outreach", END) #signals the pipline is complete

    return graph.compile() #locks the graph structure and returns a runnable object 

agent = build_graph()