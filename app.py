import os
import streamlit as st
import fs_tools

# Page Config
st.set_page_config(
    page_title="LLM File Assistant",
    page_icon="📂",
    layout="wide"
)

# Custom Styling for a Premium Dark Look
st.markdown("""
    <style>
    body {
        color: #e0e6ed;
    }
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
    }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        transform: translateY(-2px);
    }
    .sidebar-file-card {
        padding: 10px;
        border-radius: 6px;
        background-color: #262730;
        margin-bottom: 8px;
        border: 1px solid #4f46e5;
    }
    </style>
""", unsafe_allow_html=True)

# Lazy import of LangChainAssistant to ensure environment is fully loaded before initializing LLM
if "assistant" not in st.session_state:
    from llm_file_assistant import LangChainAssistant
    st.session_state["assistant"] = LangChainAssistant()
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "tool_logs" not in st.session_state:
    st.session_state["tool_logs"] = []

# --- SIDEBAR: File Explorer ---
with st.sidebar:
    st.title("📂 Resume Explorer")
    st.caption("Inspect and manage files inside the resumes directory.")
    st.divider()
    
    # File Uploader
    st.subheader("📤 Upload New Resume")
    uploaded_file = st.file_uploader("Choose a file (.txt, .docx, .pdf)", type=["txt", "docx", "pdf"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        target_path = os.path.join("resumes", uploaded_file.name)
        
        # Write uploaded file in binary mode
        os.makedirs("resumes", exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        st.success(f"Uploaded '{uploaded_file.name}'!")
        st.rerun()
        
    st.divider()
    
    # File List
    st.subheader("📄 Current Resumes")
    files = fs_tools.list_files("resumes")
    if not files:
        st.info("No resumes found in the resumes/ directory.")
    else:
        for f in files:
            st.markdown(
                f"""<div class="sidebar-file-card">
                <strong>{f['name']}</strong><br/>
                <small>Size: {f['size']} bytes<br/>
                Modified: {f['modified'][:16]}</small>
                </div>""",
                unsafe_allow_html=True
            )

# --- MAIN PANEL: Chat interface ---
st.title("🧠 LLM-powered File Assistant")
st.markdown("Interact with your files using natural language. The assistant will invoke local file system tools to fulfill your requests.")
st.divider()

# Display Chat Messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "logs" in msg and msg["logs"]:
            with st.expander("🛠️ File system operations executed", expanded=False):
                for log in msg["logs"]:
                    st.markdown(f"- ⚙️ {log}")

# Input Box
if prompt := st.chat_input("Ask a question (e.g., 'Find resumes mentioning Python', 'Summarize resume_john_doe.txt')"):
    # Render user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    # Run assistant
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # We can display the status of running file operations
        with st.status("Executing file system operations...", expanded=True) as status:
            # Run the agent ask method
            result = st.session_state["assistant"].ask(prompt)
            response = result["content"]
            logs = result["logs"]
            
            # Show completed logs
            if logs:
                for log in logs:
                    st.write(f"⚙️ {log}")
            else:
                st.write("No tools were called.")
                
            status.update(label="File operations completed!", state="complete", expanded=False)
            
        message_placeholder.markdown(response)
        
    st.session_state["messages"].append({
        "role": "assistant",
        "content": response,
        "logs": logs
    })
    st.rerun()
