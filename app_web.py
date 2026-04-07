import streamlit as st
import os
from dotenv import load_dotenv

# Set environment variables
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
load_dotenv()

from rag.pipeline import rag_pipeline

# Page config
st.set_page_config(
    page_title="RAG Q&A System",
    page_icon="🤖",
    layout="centered"
)

# Title
st.title("🤖 RAG Question Answering System")
st.markdown("Ask questions about the documents in the knowledge base")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = rag_pipeline(prompt)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This is a RAG (Retrieval-Augmented Generation) system that:
    - Retrieves relevant information from documents
    - Generates accurate answers using AI
    - Powered by Groq's Llama 3.3 70B model
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit")
