import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import fs_tools

# Load environment variables
load_dotenv()

# Initialize ChatOpenAI client
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

active_logs = []

def _append_log(msg: str):
    active_logs.append(msg)

# Define LangChain Tools (with logs printed when invoked)
@tool
def read_file(filepath: str) -> dict:
    """Read a resume file (PDF, TXT, DOCX) and return its content and metadata."""
    msg = f"Reading file: '{filepath}'"
    print(f"\n[LangChain Tool: 'read_file' - {msg}]")
    _append_log(msg)
    return fs_tools.read_file(filepath)

@tool
def list_files(directory: str, extension: str = None) -> list:
    """List all files in a directory, optionally filtering by extension (e.g. '.pdf', '.txt')."""
    msg = f"Listing files in directory: '{directory}' (filter: '{extension}')"
    print(f"\n[LangChain Tool: 'list_files' - {msg}]")
    _append_log(msg)
    return fs_tools.list_files(directory, extension)

@tool
def write_file(filepath: str, content: str) -> dict:
    """Write text content to a file, automatically creating parent directories if needed."""
    msg = f"Writing content to file: '{filepath}'"
    print(f"\n[LangChain Tool: 'write_file' - {msg}]")
    _append_log(msg)
    return fs_tools.write_file(filepath, content)

@tool
def search_in_file(filepath: str, keyword: str) -> dict:
    """Search for a keyword inside a file (case-insensitive) and return matching lines along with context."""
    msg = f"Searching for keyword '{keyword}' in file: '{filepath}'"
    print(f"\n[LangChain Tool: 'search_in_file' - {msg}]")
    _append_log(msg)
    return fs_tools.search_in_file(filepath, keyword)

class LangChainAssistant:
    def __init__(self):
        # Expose tools list
        self.tools = [read_file, list_files, write_file, search_in_file]
        
        # Compile agent with LLM, tools, and system prompt (prompt)
        self.agent = create_react_agent(
            model=llm,
            tools=self.tools,
            prompt=(
                "You are an LLM File Assistant. You have access to local file system tools to "
                "read, write, list, and search files. Use your tools to perform user requests and "
                "summarize findings clearly in Markdown."
            )
        )
        self.history = []

    def ask(self, user_prompt: str) -> dict:
        global active_logs
        active_logs.clear()
        self.history.append(("user", user_prompt))
        try:
            response = self.agent.invoke({"messages": self.history})
            # Save the updated conversation history (keeps state)
            self.history = response["messages"]
            # Return final textual message content and logs
            return {
                "content": self.history[-1].content,
                "logs": list(active_logs)
            }
        except Exception as e:
            return {
                "content": f"Error executing agent: {e}",
                "logs": list(active_logs)
            }

def main():
    print("==================================================")
    print("Welcome to LangChain File Assistant (OpenAI-powered)!")
    print("Type 'exit' or 'quit' to end the session.")
    print("==================================================")
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[WARNING] OPENAI_API_KEY not found in environment or .env file.")
        print("Please configure it in a .env file to enable LLM queries.")
        
    assistant = LangChainAssistant()
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
                
            print("\nAssistant: (Thinking...)")
            result = assistant.ask(user_input)
            print(f"\nAssistant:\n{result['content']}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
