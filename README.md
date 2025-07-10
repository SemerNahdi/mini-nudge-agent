

<div align="center">

# Mini-Nudge Agent 

A sleek micro-service that identifies stalled sales deals and generates personalized, AI-powered nudges to re-engage buyers, built with Python and FastAPI.

---

### 📌 Quick Links

[✨ Features](#features) •  [🛠️ Setup](#setup) •  [🚀 Usage](#usage) •  
[🗂️ Architecture](#architecture) •  [📡 API](#available-endpoints) •  

</div>


## Overview

* Mini-Nudge Agent processes CRM data (`crm_events.csv`) and email threads (`emails.json`).
* Detects deals idle for **7+ days** with an urgency score > 250.
* Analyzes buyer reply speed and email tone.
* Uses **OpenAI GPT-3.5-Turbo**to craft actionable nudges (≤25 words) tailored to each buyer’s communication style.
* Outputs are saved to `out/nudges.json`.
* Nudges are served via a FastAPI `/nudges` endpoint.


---

## Features

- **Data Processing:** Computes idle days, reply speed (median minutes), and urgency for deals.
- **Tone Detection:** Classifies buyer emails as formal or casual based on emojis and exclamation marks.
- **AI Nudges:** Generates concise, actionable nudges using OpenAI, personalized to tone and reply speed.
- **API:** Streams results via FastAPI at `/nudges`.
- **Testing:** Comprehensive pytest suite for robustness.
- **Reproducibility:** Clear setup with `.env` and dependency management.

---

## Setup

### Prerequisites

- Python 3.10+
- OpenAI API key

### Installation

1. **Clone the Repository:**
    ```bash
    https://github.com/SemerNahdi/mini-nudge-agent  
    cd mini-nudge-agent
    ```

2. **Set Up Virtual Environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    Dependencies include `pandas`, `openai`, `fastapi`, `uvicorn`, `python-dotenv`, `pydantic`, and `pytest`.

4. **Configure Environment:**
    ```bash
    cp .env.example .env
    ```
    Add your OpenAI API key in `.env`:
    ```
    OPENAI_API_KEY=sk-proj-...
    ```
    Add your email address in `.env`:
    ```
    YOUR_EMAIL=your_email@gmail.com
    ```

5. **Add Mock Data:**

    Place `crm_events.csv` and `emails.json` in the `data/` directory .

---

## Usage

### Run Locally

Generate nudges and save to `out/nudges.json`:

```bash
python app/run.py
````
or 

```bash
run-app
````

**Output example:**

```
✅ Generated nudges, saved to out/nudges.json
```

Here's a cleaned-up and formatted version of your Swagger section in Markdown:

---

### Run FastAPI Server

Access nudges via a web endpoint:

```bash
uvicorn app.main:app --reload
```

Visit [http://localhost:8000/nudges](http://localhost:8000/nudges) to stream the JSON output.

### Available Endpoints

#### GET /

Returns a welcome message.

**Response:**

```json
{
  "message": "Welcome to the Mini Nudge Agent API!"
}
```

#### GET /nudges

Streams generated nudge suggestions in JSON format for stalled deals.

**Response:**

A JSON array of nudge objects, each containing:

* `deal_id` (string)
* `contact` (string)
* `nudge` (string) — the personalized nudge message
* `urgency` (integer)
* `reply_speed` (float)
* `tone` (string, e.g. "formal" or "casual")

---

Would you like me to add example JSON output for `/nudges` too?

### Run Tests

Verify functionality with pytest:

```bash
pytest tests/ -v
```

Tests cover tone detection, idle days, reply speed, and deal processing.

---

## Architecture

### File Structure

```

📂 mini-nudge-agent
    📂 app
        📄 __init__.py
        📄 main.py
        📄 run.py
        📂 core
            📄 __init__.py
            📄 processor.py
            📄 classifier.py
            📄 generator.py
            📄 model.py
        📂 api
            📄 __init__.py
            📄 routes.py
        📂 utils
            📄 __init__.py
            📄 helpers.py
    📂 tests
        📄 __init__.py
        📄 test_classifier.py
        📄 test_scoring.py
    📂 data
        📄 crm_events.csv
        📄 emails.json
    📂 out
        📄 nudges.json
    📄 .env
    📄 .env.example
    📄 requirements.txt
    📄 README.md
    
```



## Components

* **Load Data** (`app/utils/helpers.py`): Reads CSV and JSON inputs.
* **Process Deals** (`app/core/processor.py`): Orchestrates metric calculations and filtering.
* **Calculate Idle Days** (`app/core/processor.py`): Computes days since last activity.
* **Calculate Reply Speed** (`app/core/processor.py`): Measures median reply time in minutes.
* **Detect Tone** (`app/core/classifier.py`): Classifies email tone (formal/casual) using emoji/exclamation heuristics.
* **Generate Nudge** (`app/core/generator.py`): Uses OpenAI GPT-3.5-Turbo for personalized nudges.
* **Structure Output** (`app/core/model.py`): Validates output with Pydantic schemas.
* **Save Output** (`app/utils/helpers.py`): Writes JSON to `out/nudges.json`.
* **FastAPI Endpoint** (`app/api/routes.py`): Streams results via `/nudges`.





