from app.graph import agent

result = agent.invoke({
    "company_name": "Stripe",
    "raw_research": [],
    "summary": "",
    "opportunities": [],
    "decision_makers": [],
    "outreach": {}
})

print("SUMMARY:", result["summary"])
print("\nOPPORTUNITIES:")
for o in result["opportunities"]: 
    print("-", o)

print("\nDECISION MAKERS:")
for dm in result["decision_makers"]: 
    print(f" - {dm['name']} ({dm['title']})")
    
print("\nEMAIL SUBJECT:", result["outreach"]["email_subject"])
print("\nEMAIL BODY:", result["outreach"]["email_body"])
