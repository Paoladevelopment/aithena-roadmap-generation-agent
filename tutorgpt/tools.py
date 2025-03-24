from langchain.agents import Tool
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub

def setup_knowledge_base(
    shared_learning_repository: str = None, model_name: str = "gpt-4-0125-preview"
) -> Runnable:
    """
    Set up a QA chain using LangChain Expression Language with a product catalog.
    Returns a Runnable chain instead of a deprecated RetrievalQA.
    """
    # Load product catalog (assumes plain text)
    with open(shared_learning_repository, "r") as f:
        shared_learning_repository_text = f.read()

    # Split text
    text_splitter = CharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
    chunks = text_splitter.split_text(shared_learning_repository_text)

    # Embedding + Vector DB
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_texts(
        chunks, embeddings, collection_name="product-knowledge-base"
    )

    retriever = vectorstore.as_retriever()

    # LLM and prompt
    llm = ChatOpenAI(model_name=model_name, temperature=0)
    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # LCEL chain
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

def get_learning_resources(query: str) -> str:
    print(f"[TOOL] get_learning_resources called with query: {query}")
    return f"Mocked response: Resources for learning '{query}'"

def generate_learning_roadmap(query: str) -> str:
    print(f"[TOOL] generate_learning_roadmap called with query: {query}")
    return f"Mocked roadmap based on: {query}"

def ask_ai_tutor(query: str) -> str:
    print(f"[TOOL] ask_ai_tutor called with query: {query}")
    return f"Mocked answer to your subject-related question: '{query}'"


def get_tools(shared_learning_repository):
    # query to get_tools can be used to be mbedded and relevant tools found

    # we only use four tools for now, but this is highly extensible!
    knowledge_base = setup_knowledge_base(shared_learning_repository)
    tools = [
        Tool(
            name="LearningResourceSearch",
            func=get_learning_resources,  
            description="Search for recommended learning resources, including online courses, books, videos, and articles on a given topic."
        ),
        Tool(
            name="GenerateStudyPlan",
            func=generate_learning_roadmap,  
            description="Creates a personalized learning roadmap based on the user's goals, preferred learning style, available time, and prior knowledge. It structures a step-by-step plan to help the user achieve their learning objectives efficiently."
        ),
        Tool(
            name="AskAITutor",
            func=ask_ai_tutor,  
            description="Use this tool to answer subject-related questions with detailed explanations, examples, and references."
        ),
    ]
    return tools
