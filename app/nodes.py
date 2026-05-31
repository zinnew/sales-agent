#all 4 agent nodes 

import os 
import json 

from dotenv import load_dotenv 
from tavily import TavilyClient #search API built for llms
from pinecone import Pinecone #vector database (stores embeddings)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from app.state import AgentState 

load_dotenv() #load environment variables from .env file
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

#Tavily client for web search 
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#Pincevone client + connect to our index
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX"))

#converts text into a list of numbers 
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def parse_json(text: str) -> dict: 
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match: 
        raise ValueError(f'No JSON found in response: {text}')
    return json.loads(match.group())

def research_node(state: AgentState) -> AgentState:
    company = state['company_name']
    results = [] #collect all research snippets here

    #check Pinecone for any previously stored research on this company 
    query_embedding = embeddings.embed_query(company)
    pinecone_results = index.query(
        vector = query_embedding, 
        top_k = 5, #find the 5 closest stored vectors for this company
        include_metadata = True, 
        filter = {"company": company} #ensures results for this exact company 
    )
    for match in pinecone_results.get("matches", []): 
        if match['score'] > 0.75: #only include if it's a close match to avoid irrelevant info
            results.append(match["metadata"]["text"])

    #web search via Tavily - four targeted queries
    queries = [
        f'{company} company overview founding news 2024',
        f'{company} tech stack engineering blog', 
        f'{company} CEO CTO leadership team', 
        f'{company} challenges problems recent layoffs',
    ]
    for q in queries: 
        response = tavily.search(query=q, max_results=3)
        for r in response.get('results', []): 
            snippet = f'{r['title']}: {r['content']}'
            results.append(snippet)

    #store new results in Pinecone for future runs 
    new_texts = results[len(pinecone_results.get("matches", [])):]
    if new_texts:
        vectors = []
        for i, text in enumerate(new_texts): 
            #convert each snippet into a vector so Pinecone can index it
            vector = embeddings.embed_query(text)
            vectors.append({
                "id": f'{company}-{i}', #unique ID
                "values": vector, #the embedding vector
                "metadata": {"company": company, "text": text} #store the original text for retrieval later
            })
        index.upsert(vectors=vectors)

    return {**state, "raw_research": results}


def summarize_node(state: AgentState) -> AgentState: 
    #join all research snippets into one big block of text for the llm to read
    research_text = "\n\n".join(state["raw_research"])

    prompt = f"""You are a sales intelligence analyst. Based on the research below, extract:
1. A 2-3 sentence company overview
2. A list of 3-5 concrete sales opportunities or pain points 
    
Respond ONLY with valid JSON in this exact format: 
{{
    "summary": "...", 
    "opportunities": ["...", "...", "..."]
}}

Research: 
{research_text[:6000]}
"""
    response = llm.invoke(prompt) #send propt to the llm and get response
    parsed = parse_json(response.content) #parse the JSON out of the llm response

    return {
        **state, 
        "summary": parsed["summary"], 
        "opportunities": parsed["opportunities"]
    }


def identify_node(state: AgentState) -> AgentState: 
    research_text = "\n\n".join(state["raw_research"])
    
    prompt = f"""You are a B2B sales researcher. Extract all named decision makers from the research below. 
Focus on: C-suite, VPs, Directors, Heads of departments. 

Respond ONLY with valid JSON in this exact format: 
{{
    "decision_makers": [
        {{"name": "...", "title": "...", "relevance": "why they matter for a sales conversation"}}
    ]
}}

If no specific names are found, return 2-3 likely roles based on the company type. 

Research: 
{research_text[:6000]}
"""
    response = llm.invoke(prompt)
    parsed = parse_json(response.content)

    return {
        **state, 
        "decision_makers": parsed["decision_makers"]
    }


def outreach_node(state: AgentState) -> AgentState: 
    company = state["company_name"]
    summary = state["summary"]

    #format opportunities as a bullet list for the prompt 
    opportunities = "\n".join(f"- {o}" for o in state["opportunities"])

    #use the first decision makers as the primary contact, if none are found use a generic placeholder 
    top_contact = state["decision_makers"][0] if state["decision_makers"] else {
        "name": "there", 
        "title": "Decision Maker"
    }
    contact_name = top_contact["name"].split()[0] #fist name only
    contact_title = top_contact["title"]

    prompt = f"""You are an expert B2B sales rep. Write outreach for the following prospect. 

Company: {company}
Contact: {contact_name} ({contact_title})
Summary: {summary}
Opportunities: 
{opportunities}

Respond ONLY with valid JSON in this exact format: 
{{
    "email_subject": "...", 
    "email_body": "...", 
    "linkedin_message": "...", 
    "call_talking_points": ["...", "...", "..."]
}}

Rules: 
- Sound human, not salesy or generic 
- Email body max 4 sentences 
- LinkedIn message mx 2 sentences 
- Reference something specific about the company
"""
    response = llm.invoke(prompt)
    parsed = parse_json(response.content)

    return {**state, "outreach": parsed}