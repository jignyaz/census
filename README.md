# Census Survey System & AI Assistant

A modern socioeconomic survey system designed for Indian government census mapping. This application features a multi-step census survey form, a detailed real-time statistics dashboard, and an integrated AI Chat Assistant capable of translating natural language queries into safe SQL statements to query the SQLite census database directly.

## Features

- **Interactive Survey Form**: Modern, multi-step census questionnaire capturing comprehensive demographic details, household statistics, sanitation, assets, and lifestyle preferences.
- **Admin Dashboard**: Real-time summary statistics including total registered households, average household size, internet penetration, TV ownership, and gender breakdown.
- **AI Chat Assistant**: Ask questions in natural language (e.g., *"How many households use electricity as their main light source?"* or *"What is the percentage of homes with internet access?"*) and receive accurate, humanized answers generated from live database queries.
- **Safe SQL Execution**: Translates user questions to read-only SQLite queries with keywords validation preventing write/delete commands.
- **Data Visualizations**: Responsive charts displaying demographic data breakdowns.

---

## Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, SQLite
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (glassmorphism dashboard, dynamic layouts, and charts)
- **AI Integration**: Google Gemini API (`gemini-2.5-flash`) or Anthropic Claude API (`claude-3-5-sonnet`)

---

## Setup & Installation

### 1. Prerequisites
Make sure you have Python 3.10+ installed on your system.

### 2. Clone and Prepare the Workspace
Open a terminal inside the project directory:

```bash
# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
Create a `.env` file in the root directory:

```env
# Set at least one API key:
GEMINI_API_KEY=your_gemini_api_key_here
# OR
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 4. Running the Application
Start the FastAPI server:

```bash
python -m uvicorn main:app --port 8000
```

Once running, access the web pages at:
- **Form / Home**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Records Dashboard**: [http://127.0.0.1:8000/records.html](http://127.0.0.1:8000/records.html)
- **AI Assistant Chat**: [http://127.0.0.1:8000/chat.html](http://127.0.0.1:8000/chat.html)

---

## Project Structure

```text
├── main.py                 # FastAPI web server & endpoints
├── ai.py                   # Natural language SQL agent and LLM client wrapper
├── database.py             # SQLite database management, initialization, and data seeding
├── requirements.txt        # Python dependencies
├── index.html              # Main multi-step census survey form
├── records.html            # Records dashboard & administrative panel
├── chat.html               # AI chat assistant interface
├── census_data.json        # Seed data for initial database setup
├── css/                    # Custom styling stylesheets
└── js/                     # Client-side interactive script files
```

---

## License
Government Socioeconomic Survey tool. Designed for official census survey automation.
