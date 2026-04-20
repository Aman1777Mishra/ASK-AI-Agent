from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser   
from langchain_classic.prompts import PromptTemplate
import os
from API_keys import open_ai_key

def Help_Assist(query: str):
    os.environ["OPENAI_API_KEY"] = open_ai_key

    embeddings = OpenAIEmbeddings()
    vecorstore = FAISS.load_local(
        folder_path = "user_guide_faiss_index",
        embeddings = embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vecorstore.as_retriever(
        search_kwargs = {"k" : 3}
    )

    llm = ChatOpenAI(
        model = "gpt-4o-mini",
        temperature = 0.7,
        max_completion_tokens=100
    )

    prompt = PromptTemplate(
        input_variables = ["context", "question"],
        template = "Using only the following context {context}. Answer the question {question}"
    )

    chain = (
        {
            "context" : RunnableLambda(lambda x : x["question"]) | retriever,
            "question" : RunnablePassthrough()
        } | prompt | llm | StrOutputParser()
    )

    response = chain.invoke({
        "question" : query
    })

    print(response)
    return response