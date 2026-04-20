from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_classic.embeddings import OpenAIEmbeddings
from langchain_classic.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_core.documents import Document
import os
import API_keys

#print("CWD:", os.getcwd())
#print("Files here:", os.listdir())

os.environ["OPENAI_API_KEY"] = API_keys.open_ai_key

loader = UnstructuredWordDocumentLoader("User_Guide.docx")
document = loader.load()


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap = 50
)

chunks = text_splitter.split_text(document[0].page_content)

chunk_doc = [
    Document(
        page_content=chunk,
        metadata = {"source" : "user_guide", "chunk_id" : i}
    )
    for i, chunk in enumerate(chunks)
]

embeddings = OpenAIEmbeddings()

vectorstore = FAISS.from_documents(
    documents = chunk_doc,
    embedding = embeddings
)

vectorstore.save_local("user_guide_faiss_index")
