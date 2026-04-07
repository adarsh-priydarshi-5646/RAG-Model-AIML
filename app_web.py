import streamlit as st
import os
from dotenv import load_dotenv
import time

# Set environment variables
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
load_dotenv()

from rag.pipeline import rag_pipeline
from rag.retriever import retrieve

# Page config
st.set_page_config(
    page_title="RAG Q&A System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        border-left: 5px solid #4CAF50;
    }
    .chat-message.assistant {
        background-color: #1e2129;
        border-left: 5px solid #2196F3;
    }
    .chat-message .message {
        color: #ffffff;
        font-size: 1rem;
        line-height: 1.6;
    }
    .chat-message .role {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        opacity: 0.8;
    }
    .source-doc {
        background-color: #262730;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
        border-left: 3px solid #FFC107;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .stats-box {
        background-color: #262730;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    h1 {
        color: #4CAF50;
    }
    .subtitle {
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_sources" not in st.session_state:
    st.session_state.show_sources = True

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("RAG Question Answering System")
    st.markdown('<p class="subtitle">Ask questions about your documents and get AI-powered answers</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Settings")
    
    # Show sources toggle
    st.session_state.show_sources = st.checkbox(
        "Show source documents", 
        value=st.session_state.show_sources,
        help="Display the source documents used to generate answers"
    )
    
    # Number of sources
    num_sources = st.slider(
        "Number of sources to retrieve",
        min_value=1,
        max_value=5,
        value=3,
        help="More sources = more context but slower response"
    )
    
    st.markdown("---")
    
    # System info
    st.header("System Info")
    
    # Check if vector DB exists
    import os
    db_exists = os.path.exists("vectorstore/db/index.faiss")
    
    if db_exists:
        st.success("Vector Database: Ready")
        
        # Count documents
        try:
            from rag.ingestion import load_documents
            from app.config import DATA_PATH
            docs = load_documents(DATA_PATH)
            st.info(f"Documents loaded: {len(docs)}")
        except:
            st.info("Documents: Available")
    else:
        st.error("Vector Database: Not found")
        st.warning("Run: python ingest.py")
    
    st.markdown("---")
    
    # Model info
    st.header("Model Info")
    st.markdown("""
    - **Provider**: Groq
    - **Model**: Llama 3.3 70B
    - **Vector DB**: FAISS
    - **Embeddings**: Mock (1536D)
    """)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    
    # Example questions
    st.header("Example Questions")
    example_questions = [
        "Who created Python?",
        "What are the key features?",
        "What is Python used for?",
        "Tell me about Python's design philosophy"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{question}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()

# Main chat area
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.messages:
        role_name = "You" if message["role"] == "user" else "Assistant"
        
        st.markdown(f"""
        <div class="chat-message {message['role']}">
            <div class="role">{role_name}</div>
            <div class="message">{message['content']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show sources if available
        if message["role"] == "assistant" and "sources" in message and st.session_state.show_sources:
            with st.expander("View Source Documents", expanded=False):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"""
                    <div class="source-doc">
                        <strong>Source {i}:</strong><br>
                        {source[:300]}...
                    </div>
                    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    st.markdown(f"""
    <div class="chat-message user">
        <div class="role">You</div>
        <div class="message">{prompt}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate response
    with st.spinner("Searching documents and generating answer..."):
        try:
            # Retrieve documents
            docs = retrieve(prompt, k=num_sources)
            
            # Generate answer
            response = rag_pipeline(prompt)
            
            # Extract source texts
            sources = [doc.page_content for doc in docs]
            
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
                "sources": sources
            })
            
            st.rerun()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_msg
            })

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Secure** - Your data stays private")
with col2:
    st.markdown("**Fast** - Powered by Groq")
with col3:
    st.markdown("**Free** - No cost to use")

