#FastAPI app - exposes the agent as an HTTP API

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel #define the shape of requests and response data 
from app.graph import agent 

app = FastAPI(title="Sales Research Agent")

class ResearchRequest(BaseModel): #defines what the celler must send in the request body 
    company_name: str

class ResearchResponse(BaseModel): #defines the shape of teh JSON we send back 
    company_name: str
    summary: str
    opportunities: list[str]
    decision_makers: list[dict]
    outreach: dict


#endpoints 
@app.get("/")
def root(): 
    return {"status": "ok", "message": "Sales Research Agent is running"}

@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest):
    if not request.company_name.strip(): #basic input validation
        raise HTTPException(status_code=400, detail="company_name cannot be empty")
    
    #all fields start empty and get filled in as the agent runs through the graph
    result = agent.invoke({
        "company_name": request.company_name.strip(), 
        "raw_research": [],
        "summary": "",
        "opportunities": [],
        "decision_makers": [],
        "outreach": {}
    })

    return ResearchResponse(
        company_name=request.company_name, 
        summary=result["summary"], 
        opportunities=result["opportunities"],
        decision_makers=result["decision_makers"],
        outreach=result["outreach"]
    )