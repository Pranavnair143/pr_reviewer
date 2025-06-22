# 🔍 Azure PR Reviewer

A **Streamlit-based GENAI** application that leverages **LangChain**, **LangGraph**, and **OpenAI** to perform AI-powered reviews of Azure DevOps pull requests.  
This tool is designed to provide **code-specific suggestions** for PRs using concurrent tool execution via LangGraph agents.

> ⚠️ This is a demo project. It does not yet handle all edge cases and is intended for exploration and experimentation with LangGraph workflows.

---

## 🖥️ Features

- 🔗 **Azure DevOps Integration**: Provide a PR link and Personal Access Token (PAT) to review.
- 💬 **Code Review Suggestions**: Uses LLMs to generate helpful code review messages.
- ⚙️ **Extraction Modes**:
  - `Only code changes`
  - `Full code`
- 👁️‍🗨️ **Agentic Structure**: Tools are invoked in parallel using LangGraph's execution model.

---

## 🚀 Demo Screenshot

![Demo Screenshot](https://drive.google.com/file/d/1DhJh539cR89OKcfZrleq6yCPyjTPqMqI/view?usp=sharing)

---

## 📁 Project Structure (Key Components)

```bash
.
├── agents/                 # LangGraph agents and tools
├── llms/                   # LLM wrappers (e.g. OpenAI config)
├── utils/                  # Helper utilities
├── .env.sample             # Sample env variables
├── main.py                 # Streamlit app
├── requirements.txt        # Python dependencies
└── README.md
```

## 🛠️ Project Setup Instructions

### 1. 📂 Clone the Repository

```bash
git clone https://github.com/your-username/azure-pr-reviewer.git
cd azure-pr-reviewer
```

### 2. 🐍 Create Virtual Environment
Requires Python 3.11

For Unix/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```
For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 📦 Install Requirements
```bash
pip install -r requirements.txt
```

### 4. 🔐 Setup Environment Variables
Copy the sample .env.sample file to .env:
```
.env
OPENAI_API_KEY='<your-openai-api-key>'
LANGCHAIN_API_KEY= "<your-langsmith-api-key>" # not mandatory, its useful for debugging purpose
LANGCHAIN_TRACING_V2='true'
LANGCHAIN_PROJECT='pr_checker'
```

### 5. ▶️ Run the Application
```bash
streamlit run main.py
```
By default, the app will launch at: http://localhost:8501

## 🔑 How to Get a Personal Access Token (PAT) from Azure DevOps
1. Go to Azure DevOps

2. Click on your profile avatar (top-right) → Security

3. Under Personal Access Tokens, click + New Token

4. Set the scopes:

5. Code > Read

6. Generate and copy the token securely

7. Paste the token into the Personal Access Token field in the app

## 🧠 Tech Stack

- LangChain

- LangGraph

- Streamlit

- Azure DevOps REST API

## 📌 Notes

- Works only with Azure DevOps PR links

- Requires valid PAT token

- Best for testing how LangGraph handles tool-based agent execution concurrently
