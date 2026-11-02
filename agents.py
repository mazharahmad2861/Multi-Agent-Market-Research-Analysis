from dotenv import load_dotenv

#from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver

from tools import (
    wikipedia_tool,
    stock_data_tool,
    python_repl_tool,
)



# Load environment variables


load_dotenv()



# LLM


#llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0,)

llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0
)


# ============================================================
# Research Agent
# ============================================================

research_agent = create_agent(
    model=llm,
    tools=[
        wikipedia_tool,
        stock_data_tool,
    ],
    system_prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, including "
        "looking up factual information and stock data.\n"
        "- DO NOT write any code.\n"
        "- After completing your task, return the results.\n"
        "- Respond ONLY with the results of your work."
    ),
    name="researcher",
)


# ============================================================
# Analyst Agent
# ============================================================

analyst_agent = create_agent(
    model=llm,
    tools=[
        python_repl_tool,
    ],
    system_prompt=(
        "You are an analyst agent that can execute Python code.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with tasks that require running Python code "
        "to produce an output.\n"
        "- Use the Python tool when calculations, data analysis, "
        "or visualizations are required.\n"
        "- After completing your task, return the results.\n"
        "- Respond ONLY with the results of your work."
    ),
    name="analyst",
)


# ============================================================
# Checkpointer
# ============================================================

checkpointer = InMemorySaver()


config = {
    "configurable": {
        "thread_id": "1",
        "user_id": "1",
    }
}


# ============================================================
# Supervisor
# ============================================================

supervisor = create_supervisor(
    model=llm,
    agents=[
        research_agent,
        analyst_agent,
    ],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- A research agent named 'researcher': assign research "
        "and data collection tasks to this agent.\n"
        "- An analyst agent named 'analyst': assign data analysis "
        "and visualization tasks to this agent.\n\n"
        "RULES:\n"
        "- Assign work to one agent at a time.\n"
        "- Do not call agents in parallel.\n"
        "- Do not do any work yourself.\n"
        "- Delegate each task to the most appropriate agent."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile(
    checkpointer=checkpointer
)