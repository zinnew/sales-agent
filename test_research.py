from app.nodes import research_node, summarize_node, identify_node, outreach_node

state = {
    "company_name": "Stripe",
    "raw_research": [],
    "summary": "",
    "opportunities": [],
    "decision_makers": [],
    "outreach": {}
}

print("Reaserching...")
state = research_node(state)

print("Summarizing...")
state = summarize_node(state)

print("Identifying...")
state = identify_node(state)

print("Generating outreach...")
state = outreach_node(state)

print("\n" + "="*50)
print("SUMMARY:", state["summary"])

print("\nOPPORTUNITIES:")
for o in state["opportunities"]: 
    print("-", o)

print("\nDECISION MAKERS:")
for dm in state["decision_makers"]: 
    print(f"- {dm['name']} ({dm['title']})")

print("\nEMAIL SUBJECT:", state["outreach"]["email_subject"])
print("\nEMAIL BODY:", state["outreach"]["email_body"])
print("\nLINKEDIN:", state["outreach"]["linkedin_message"])
print("\nTALKING POINTS:")
for tp in state["outreach"]["call_talking_points"]: 
    print("-", tp)

