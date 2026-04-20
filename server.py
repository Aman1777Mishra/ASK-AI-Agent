from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import os
import io
import pandas as pd
import Create_Agent
import uuid
import Tool_Creation
from langchain_openai import ChatOpenAI
from langchain_classic.prompts import PromptTemplate
import API_keys
# --- FastAPI app ---
app = FastAPI()

# Allow requests from the HTML file opened locally (file://) or any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

os.environ["OPENAI_API_KEY"] = API_keys.open_ai_key

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_file(file: UploadFile, content: bytes):
    filename = file.filename.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content))
        print(df.head())  # Just to verify we read it correctly
        return {
            "type": "csv",
            "rows": df.shape[0],
            "columns": list(df.columns)
        }

    # 👇 fallback (VERY IMPORTANT)
    return {
        "type": "unknown",
        "filename": file.filename,
        "size": len(content)
    }

agents = {}
MAX_Sessions = 5

llm = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0.7,
        max_completion_tokens=200
        )
    
prompt = PromptTemplate.from_template(
        """You are a helpful price assistant.
         Decide on whether to use Help_Assist, NPC, or VPM tool based on the user's question.
         Rules for tool usage:
         -If the question is related to how to do pricing or any steps involved in pricing, use the Help_Assist tool to provide guidance based on user guide.
         -If the question is related to simulating or comparing FUTURE price changes impact on revenue, use the NPC tool.
         -If the question is related to analyzing the impact of HISTORICAL price changes on revenue, use the VPM tool.
         - If user suggests a Tool in the question, use that tool.
         
        IMPORTANT Things to note:
        -If a tool exists for a task, you MUST use the tool.
        -Do not answer from your own knowledge if tools exist for the task.
        -If a tool is used, its returned output is the final answer. Do not continue reasoning.
        -DO NOT Loop over one tool more than once. Whatever, result the tool give in the first try, take it as final and do not try to use the same tool again for the same question.
        -DO NOT call more than one tool for a question. Always choose the most relevant tool based on the question and use only that tool.
         Incase of using the tools, make sure to provide the necessary input in the correct format as expected by the tool.
         If you are not able to get the time period from the user query, just pass 12 to the NPC and VPM tools as default.
        Provide time period input to NPC and VPM tools as an string representing number of months.
        For example, if the user query has:
        6 months, provide input as 6.
        year, provide input as 12.
        two years, provide input as 24.
        quarter, provide input as 3.

        {chat_history}
         
         Question: {question}
         
         Helpful Answer:
         
         {agent_scratchpad}"""
    )



@app.post("/ask")
async def ask(
    query: str = Form(...),
    session_id: str = Form(None),
    files: list[UploadFile] = File(default=[])
):
    
    if len(agents) > MAX_Sessions:
        agents.clear()  
        print(agents)

    if not session_id:
        session_id = str(uuid.uuid4())

    file_details = []

    for file in files:
        content = await file.read()   # ✅ read ONCE

        #print(file.filename)

        # 🔹 Process
        processed = process_file(file, content)

        # 🔹 Save file (use SAME content)
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)

        file_details.append({
            "filename": file.filename,
            "size": len(content),
            "details": processed 
        })

    if session_id not in agents:
        print(f"\n\nCreating new agent for session: {session_id}\n\n")
        
        agents[session_id] = {
            "latest_file": None}   
        

        tools = Tool_Creation.create_tools_new(agents, session_id)

        agents[session_id]["agent"] = Create_Agent.create_agent(llm, prompt, tools)


    if file_details:
        agents[session_id]["latest_file"] = file_details[-1]
        print(f"Updated latest file for session {session_id}: {agents[session_id]['latest_file']}")
    #print(agents)
    agent_data = agents[session_id]
    #print(agent_data)

    

    #print(file_details)
    #print(type(query))    
    response = agent_data["agent"].invoke({"question": query})  

    return {
        "message": response["output"],
        "session_id": session_id,
        "files_received": len(file_details) > 0,
        "files": file_details
    }
