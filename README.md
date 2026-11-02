# 🤖 Multi-Agent Market Research

An AI-powered **multi-agent market research and stock analysis system** built using **LangGraph, LangGraph Supervisor, LangChain, Groq, Python, Pandas, and Gradio**.

The system uses a **Supervisor Agent** to intelligently delegate user requests to specialized worker agents:

* 🔎 **Researcher Agent** — company research and stock-data retrieval
* 📊 **Analyst Agent** — numerical analysis and visualization
* 👔 **Supervisor Agent** — task routing and multi-agent orchestration

The application provides an interactive Gradio chat interface where users can ask questions about companies and their historical stock performance.

---

## 📌 Project Overview

Traditional LLM applications often rely on a single general-purpose agent that is responsible for research, data retrieval, calculations, and visualization.

This project takes a **multi-agent approach** by separating these responsibilities into specialized agents.

```text
                              USER
                                │
                                ▼
                       ┌─────────────────┐
                       │   SUPERVISOR    │
                       │      AGENT      │
                       │                 │
                       │ Task Routing    │
                       │ Orchestration   │
                       │ Delegation      │
                       └────────┬────────┘
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
        ┌─────────────────┐           ┌─────────────────┐
        │    RESEARCHER   │           │     ANALYST     │
        │      AGENT      │           │      AGENT      │
        └────────┬────────┘           └────────┬────────┘
                 │                             │
          ┌──────┴──────┐                      ▼
          ▼             ▼               ┌──────────────┐
      Wikipedia    Alpha Vantage        │ Python REPL  │
                         │              └──────┬───────┘
                         ▼                     │
                    Stock Data                 ▼
                                      Calculations / Charts
                        
```

The supervisor can delegate a task to one agent or coordinate multiple agents when a request requires both research and analysis.

---

# ✨ Key Features

* Multi-agent architecture using **LangGraph**
* Supervisor-based agent orchestration
* Specialized Researcher and Analyst agents
* Wikipedia-based company research
* Historical stock-data retrieval using Alpha Vantage API
* Pandas-based data processing
* Python-powered calculations
* Stock-data visualization
* OpenAI LLM inference
* Interactive Gradio web interface
* Independent query → answer workflow
* Tool-based agent execution
* Sequential agent handoffs
* Modular project structure

---

# 🏗️ System Architecture

The application consists of four major layers.

```text
┌──────────────────────────────────────────────────┐
│                  GRADIO UI                       │
│              User Interaction                    │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│              SUPERVISOR AGENT                    │
│                                                  │
│  • Understand user request                       │
│  • Decide which agent should work                │
│  • Coordinate multiple agents                    │
│  • Return final response                         │
└──────────────────────┬───────────────────────────┘
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
┌─────────────────────┐   ┌─────────────────────┐
│   RESEARCHER AGENT  │   │    ANALYST AGENT    │
│                     │   │                     │
│ • Company research  │   │ • Calculations      │
│ • Stock retrieval   │   │ • Data analysis     │
│                     │   │ • Visualization     │
└──────────┬──────────┘   └──────────┬──────────┘
           │                         │
      ┌────┴────┐                    ▼
      ▼         ▼               ┌──────────────┐
 Wikipedia  Alpha Vintage       │ Python REPL  │
                                └──────────────┘
```

---

# 🧠 Agents

## 1. Supervisor Agent

The Supervisor is the **orchestrator** of the system.

It does not directly perform research or numerical analysis.

Its responsibilities are:

* Understand the user's request
* Determine the type of task
* Select the appropriate worker agent
* Delegate tasks
* Coordinate multi-step workflows
* Receive results from worker agents
* Return the final response

For example:

For a more complex request:

```text
User:
"Calculate the highest closing price of Tesla
over the last 30 days."

        ↓

Supervisor

        ↓

Researcher

        ↓

Stock Data Tool

        ↓

Alpha Vintage API

        ↓

Supervisor

        ↓

Analyst

        ↓

Python

        ↓

Supervisor

        ↓

User
```

---

## 🔎 2. Researcher Agent

The Researcher Agent specializes in **information retrieval and data collection**.

It has access to two tools:

```text
wikipedia_tool
stock_data_tool
```

### Responsibilities

* Search Wikipedia
* Retrieve company information
* Retrieve historical stock data
* Convert company names to ticker symbols
* Return retrieved information to the supervisor
* Avoid performing numerical calculations itself

---

### 📚 Wikipedia Tool

The Wikipedia tool uses the `wikipedia` Python package.

Workflow:

```text
User Question
     │
     ▼
Researcher Agent
     │
     ▼
wikipedia_tool
     │
     ▼
Wikipedia Search
     │
     ▼
Relevant Page
     │
     ▼
Page Summary
     │
     ▼
Researcher
```


### 📈 Stock Data Tool

The stock-data tool retrieves stock information from Alpha Vintage API.





The tool accepts:

```text
company_ticker
num_days
```

Example:

```text
company_ticker = TSLA
num_days = 30
```

The tool loads:

```text
The tool retrieves the latest 30 available trading days and provides:
- Open price
- High price
- Low price
- Closing price
- Trading volume
- Highest closing price
- Lowest closing price
- Average closing price
- Trading period
```

and returns the requested historical data.

---

## 📊 3. Analyst Agent

The Analyst Agent is responsible for tasks requiring computation or visualization.

It has access to:

```text
python_repl_tool
```

### Responsibilities

* Calculate maximum values
* Calculate minimum values
* Calculate averages
* Calculate percentage changes
* Analyze retrieved data
* Generate visualizations
* Execute Python code when required

For example:

```text
Calculate the highest and lowest closing
price of Apple over the last 30 days.
```

The analyst can use Python operations such as:

```python
df["Close"].max()
```

and:

```python
df["Close"].min()
```

This separates **LLM reasoning** from **actual numerical computation**.

---

### 🐍 Python REPL Tool

The Python tool allows the Analyst Agent to execute Python code.

It can be used for:

* Data analysis
* Calculations
* Statistical operations
* Plotting
* Visualization

Example:

```python
import matplotlib.pyplot as plt

plt.plot(df["Close"])
plt.title("Stock Price")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.show()
```

The agent can therefore transform retrieved stock data into useful analytical results or charts.

---


# 🔗 Agent Handoffs

One of the important concepts demonstrated by this project is **agent-to-agent handoff**.

The supervisor can transfer a task to a worker agent.

Conceptually:

```text
Supervisor
    │
    │ transfer_to_researcher
    ▼
Researcher
    │
    │ performs task
    ▼
Researcher
    │
    │ transfer_back_to_supervisor
    ▼
Supervisor
```

For example:

```text
transfer_to_researcher
```

moves the task to the Researcher Agent.

After completing its work, the researcher can hand control back to the supervisor.

This creates a controlled multi-agent workflow rather than simply giving one LLM access to every tool.

---

# 🛠️ Technology Stack

| Technology           | Purpose                                   |
| -------------------- | ----------------------------------------- |
| Python               | Core programming language                 |
| LangChain            | Agent and tool abstractions               |
| LangGraph            | Agent workflow orchestration              |
| LangGraph Supervisor | Supervisor-based multi-agent architecture |
| Groq                 | LLM inference                             |
| Llama 3.3 70B        | Current LLM used by the project           |
| Wikipedia            | Company research                          |
| Pandas               | Stock-data processing                     |
| Python REPL          | Code execution and calculations           |
| Matplotlib           | Visualization                             |
| Gradio               | Web interface                             |
| CSV                  | Historical stock-data storage             |

---

# 📁 Project Structure

```text
multi-agent-market-research/
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── main.py
├── agents.py
├── tools.py
│
└── data/
    ├── AAPL.csv
    ├── AMZN.csv
    ├── META.csv
    ├── MSFT.csv
    ├── NFLX.csv
    └── TSLA.csv
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/mazharahmad2861/Multi-Agent-Market-Research-Analysis
cd multi-agent-market-research-analysis
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Configure API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Make sure `.env` is ignored by Git:

```gitignore
.env
```

---

# 🚀 Running the Application

Run:

```bash
python main.py
```

You should see something similar to:

```text
Running on local URL:
http://127.0.0.1:7860
```

Open:

```text
http://127.0.0.1:7860
```

in your browser.

---

# 💬  Queries Types

#### Company Research
#### Stock Data 
#### Numerical Analysis
#### Visualization
#### Multi-Agent Query



# 🧩 Why Multi-Agent Architecture?

A single agent could technically be given all of these tools:

```text
Wikipedia
Stock Data
Python
```

However, this creates a general-purpose agent with many responsibilities.

This project instead uses specialization:

```text
┌──────────────────────────────────┐
│          SUPERVISOR              │
│          Orchestration           │
└────────────────┬─────────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
┌──────────────┐    ┌──────────────┐
│  RESEARCHER  │    │   ANALYST    │
│              │    │              │
│ Retrieval    │    │ Computation  │
│ Research     │    │ Visualization│
└──────────────┘    └──────────────┘
```

Advantages include:

* Clear separation of responsibilities
* Easier debugging
* Better tool organization
* More controlled agent behavior
* Easier extension with additional agents
* Demonstrates agent orchestration patterns

---

# 🎯 Design Principles

### 1. Separation of Responsibilities

Each agent has a clearly defined role.

```text
Supervisor → Orchestration
Researcher → Retrieval
Analyst → Computation
```

---

### 2. Tool-Based Execution

Agents don't need to know everything themselves.
They use tools


### 3. Deterministic Computation

Numerical calculations are delegated to Python rather than relying on the LLM to manually calculate values.


### 4. Sequential Delegation

The supervisor assigns work to one agent at a time.


# 🧠 Important LangGraph Concepts Demonstrated

This project provides hands-on experience with several important concepts:

### Agents

Specialized LLM-powered workers capable of using tools.

### Tools

Functions exposed to agents for performing external operations.

### Supervisor

An agent responsible for delegating tasks to other agents.

### Handoffs

Mechanisms for transferring control between agents.

### State

Information passed through the LangGraph workflow.

### Compiled Graph

The executable representation of the LangGraph workflow.

### Multi-Agent Orchestration

Coordinating multiple specialized agents to complete a larger task.

---



# ⚠️ Limitations

### 1. Historical CSV Data

The project currently doesn't retrieve real-time market data.

The stock-data tool reads local CSV files.

### 2. Dataset Coverage

Only the companies for which CSV files exist can be queried.

Currently:

```text
AAPL
AMZN
META
MSFT
NFLX
TSLA
```

### 3. Python Execution

The Python REPL executes generated Python code. Arbitrary code execution should not be exposed directly to untrusted users in a production environment without appropriate isolation and security controls.

### 4. Wikipedia Retrieval

Wikipedia search results depend on the search query and available Wikipedia content.

### 5. LLM Routing

Agent routing is influenced by the LLM and system prompts. Strong tool-use instructions are therefore important for reliable behavior.

---

# 🚀 Future Improvements

The project can be extended significantly.

## 1. Live Stock Data

Replace static CSV files with a market-data API.

```text
Current:

CSV → Pandas → Agent

Future:

Market API → Pandas → Agent
```

---

## 2. More Financial Tools

Add tools for:

```text
Financial statements
Revenue
Profit
EPS
P/E ratio
Market capitalization
Dividends
Balance sheet
Cash flow
```

---

## 3. Additional Specialized Agents

For example:

```text
                    Supervisor
                         │
       ┌─────────┬───────┼────────┬─────────┐
       ▼         ▼       ▼        ▼         ▼
  Researcher  Analyst  News    Financial  Chart
                       Agent    Agent      Agent
```

---

## 4. News Research Agent

Add a specialized agent for:

```text
Latest company news
Market events
Earnings announcements
Corporate announcements
```

---

## 5. Database Integration

Instead of CSV files:

```text
CSV
 ↓
PostgreSQL
```

or:

```text
CSV
 ↓
DuckDB
```

---

## 6. Persistent Memory

The current application can treat each query independently.

A future version could add LangGraph persistence using a checkpointer:

```text
User
 ↓
Conversation
 ↓
Persistent State
 ↓
Supervisor
```

This would allow the system to support context-aware conversations.

---

## 7. Production Deployment

Possible deployment architecture:

```text
                 User
                  │
                  ▼
             Web Interface
                  │
                  ▼
                API
                  │
                  ▼
             LangGraph
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
    Researcher           Analyst
        │                   │
        ▼                   ▼
   Data Services       Compute Service
```

Potential technologies:

```text
FastAPI
Docker
AWS
PostgreSQL
Redis
LangSmith
```

---

# 📊 Example End-to-End Scenario

User asks:

```text
Analyze Tesla's stock over the last 30 days,
calculate the average closing price,
and create a chart.
```

### Step 1 — Supervisor

Identifies that the request requires:

```text
Data Retrieval
+
Numerical Analysis
+
Visualization
```

### Step 2 — Researcher

Calls:

```text
stock_data_tool
```

with:

```text
TSLA
30
```

### Step 3 — Stock Tool

Loads:

```text
data/TSLA.csv
```

and retrieves the requested data.

### Step 4 — Researcher → Supervisor

Returns the stock data.

### Step 5 — Supervisor → Analyst

Delegates the analysis.

### Step 6 — Analyst

Uses Python to calculate:

```python
df["Close"].mean()
```

and creates a visualization.

### Step 7 — Analyst → Supervisor

Returns the results.

### Step 8 — Supervisor

Combines the results into the final response.

### Final architecture

```text
                         USER
                          │
                          ▼
                    SUPERVISOR
                          │
                          ▼
                     RESEARCHER
                          │
                          ▼
                  stock_data_tool
                          │
                          ▼
                      TSLA.csv
                          │
                          ▼
                     RESEARCHER
                          │
                          ▼
                    SUPERVISOR
                          │
                          ▼
                      ANALYST
                          │
                          ▼
                     PYTHON REPL
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
             Calculation         Chart
                 │                 │
                 └────────┬────────┘
                          ▼
                     SUPERVISOR
                          │
                          ▼
                         USER
```

---





# 🔮 Future Architecture

The long-term version of this project could evolve into:

```text
                         ┌───────────────┐
                         │     USER      │
                         └───────┬───────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │    SUPERVISOR     │
                       └─────────┬─────────┘
                                 │
       ┌─────────────┬───────────┼─────────────┬─────────────┐
       ▼             ▼           ▼             ▼             ▼
  Researcher      Analyst     News Agent   Financial     Visualization
     Agent         Agent                    Agent           Agent
       │             │           │             │             │
       ▼             ▼           ▼             ▼             ▼
 Wikipedia        Python      News APIs    Financial      Charts
 Stock API        Pandas      Search       Data APIs      Reports
       │             │           │             │             │
       └─────────────┴───────────┴─────────────┴─────────────┘
                                 │
                                 ▼
                           FINAL RESPONSE
```

This would transform the current learning project into a more complete **AI-powered financial research and analysis platform**.

---

# 👨‍💻 Author

**Mazhar Ahmad**

Built as a hands-on project to explore **LangGraph multi-agent orchestration, supervisor architectures, tool calling, and Agentic AI systems**.
