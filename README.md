# Sentinel‑AI‑AutoTriage

**Enterprise‑grade SOC automation framework for Microsoft Sentinel**

## 🌐 Overview
Sentinel‑AI‑AutoTriage connects to Microsoft Sentinel, ingests Tier‑1 incidents and uses a large‑language model (LLM) to analyse and enrich the context of each incident. When appropriate, it automatically closes incidents and adds detailed comments and classifications. Automation rules in Microsoft Sentinel can triage incidents by changing status, assigning an owner, tagging, escalating and closing incidents; this project extends those capabilities with AI‑driven reasoning.

## 📦 Features

* **Secure Authentication:** Uses `azure-identity` to obtain tokens via `DefaultAzureCredential`, which automatically chooses the right authentication mechanism for the environment【987667603810256†L350-L364】. Service principal credentials (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`) are read from environment variables【987667603810256†L428-L433】.
* **Incident Ingestion:** Leverages `azure-mgmt-securityinsight` to list and fetch active incidents from Microsoft Sentinel. The library exposes `IncidentsOperations` and `AutomationRulesOperations` endpoints for managing incidents.
* **LLM‑based Analysis:** Sends incident summaries to an LLM (OpenAI API or local model via LangChain). The model returns suggested severity, recommended actions and resolution status.
* **Auto‑Close Workflow:** If the LLM categorises an incident as benign or resolved, the framework updates the incident’s status to “Closed” and adds a comment explaining why. This minimises analyst fatigue and ensures repeatable triage.
* **Logging & Observability:** Comprehensive logging using the Python `logging` module. Every API call, decision and error is recorded, enabling full auditability.
* **Extensible:** Modular functions allow integration with other ticketing or SIEM platforms. The LLM component is abstracted to enable plug‑in of different models.

## 🛠️ Stack
| Component | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Azure SDK** | `azure-identity`, `azure-mgmt-securityinsight` |
| **AI/LLM** | `openai` or `langchain` for model interfacing |
| **Others** | `dotenv` for reading `.env` files, `rich` for colourful logging (optional) |

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/eric-ariel-rimon/Sentinel-AI-AutoTriage.git
   cd Sentinel-AI-AutoTriage
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   Create a `.env` file in the project root and populate it with:
   ```ini
   AZURE_CLIENT_ID=<your service principal client ID>
   AZURE_TENANT_ID=<your tenant ID>
   AZURE_CLIENT_SECRET=<your client secret>
   SUBSCRIPTION_ID=<Azure subscription ID>
   RESOURCE_GROUP=<Sentinel resource group>
   WORKSPACE_NAME=<Sentinel workspace name>
   OPENAI_API_KEY=<optional – only if using OpenAI API>
   ```
4. **Run the auto‑triage script:**
   ```bash
   python src/auto_triage.py
   ```

## 📄 File Structure

```
Sentinel-AI-AutoTriage/
├── README.md                 # Project overview and instructions
├── requirements.txt          # Python dependencies
├── .env.example              # Sample environment variables
├── src/
│   ├── __init__.py
│   ├── auto_triage.py        # Main entry point for the automation
│   ├── sentinel_client.py    # Wraps Azure SDK calls
│   ├── llm_client.py         # Abstracts LLM interactions
│   └── models.py             # Data models and utility functions
└── logs/                     # Log files generated at runtime
```

## ✅ Roadmap

* [x] Implement initial incident ingestion and closing logic.
* [ ] Integrate sentiment and context analysis for richer enrichment.
* [ ] Add support for additional SIEMs (Splunk, ELK).
* [ ] Create a dashboard to visualise triage outcomes.

## 📄 License
This project is released under the MIT License. See `LICENSE` for more information.
