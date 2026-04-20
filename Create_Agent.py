import os
import API_keys
from langchain_classic.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_react_agent
#from langchain_community.tools import WikipediaQueryRun
#from langchain_classic.utilities import WikipediaAPIWrapper
from langchain_classic import hub
from langchain_classic.agents import AgentExecutor
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_classic.agents import create_openai_tools_agent
import Help_Assist
from langchain_community.tools import Tool
import NPC
import VPM

def create_agent(llm,prompt, tools):
    print("Inside ask_agent function")
   # print(file_details)
    os.environ["OPENAI_API_KEY"] = API_keys.open_ai_key

    memory = ConversationBufferWindowMemory(
        k=2,
        memory_key="chat_history", 
        return_messages=True
        )

    agent = create_openai_tools_agent(
        llm=llm,
        prompt=prompt,
        tools=tools
    )

    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory,
        verbose=True,
        max_iterations=3,
        #early_stopping_method="generate",
        handle_parsing_errors=True,
        )
    
    return agent_executor