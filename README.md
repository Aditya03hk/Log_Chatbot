# Log Analysis 

## Overview

This project provides a comprehensive log analysis solution with two main components:

- **Logbot**: A chatbot interface that allows users to ask natural language questions about logs and get SQL-powered answers with visualizations.
- **Dashboard**: A monitoring interface that displays key metrics, trends from log data.

The system analyzes logs from three main sources:
- **VPC logs** (network traffic)
- **Access logs** (API requests)
- **Execution logs** (function performance)

---

## ✨ Features

### Logbot Features
- Natural language query processing for log data
- Automatic SQL generation and execution
- Interactive data visualizations
- Context-aware responses (understands log-related queries vs general questions)

### Dashboard Features
- Real-time monitoring of key performance indicators
- Trend analysis
- VPC, Access, and Execution log analysis
- Performance benchmarking
- Alert system for high error rates and latency spikes

---

## ⚙️ Prerequisites

Before running the application, ensure you have:

- Python 3.8 or higher
- SQLite3

# Install dependencies
pip install -r requirements.txt
---

## 🛠️ Installation Steps

### 1. Clone the repository
```bash
git clone <https://github.com/Aditya03hk/Log_Chatbot>
cd <repository-folder>
```

### 2. Set up a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate  
On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file with the following content:
```
LANGSMITH_API_KEY=your_langsmith_key
GROQ_API_KEY=your_groq_key
LANGSMITH_TRACING=false
```

### 5. Generate sample log data
```bash
python create_logs_db.py
```

### 6. Create the SQLite database
```bash
python csv_to_db.py
```

---

## 🚀 Running the Application

### Option 1: Run Logbot (Chat Interface)
```bash
streamlit run app.py
```


Both applications will open in your default browser at [http://localhost:8501](http://localhost:8501)

---


## 🗃️ Database Schema

The system uses three main tables:

### `vpc_logs`
- `timestamp`, `src_ip`, `dst_ip`, `action`, `bytes_sent`, `request_id`

### `access_logs`
- `timestamp`, `user_id`, `endpoint`, `method`, `status_code`, `request_id`

### `execution_logs`
- `timestamp`, `function_name`, `duration_ms`, `status`, `request_id`

All tables are joined using the `request_id` field.

---

## 💬 Example Queries for Logbot

Try these in the Logbot interface:

- "Show me users with failed login attempts"
- "What's the average duration of successful executions?"
- "Which endpoints have the highest error rate?"
- "List IPs with rejected VPC actions"
- "Show the trend of failed requests over time"

---

## 🔧 Customization

### Add your own log data:
- Modify `create_logs_db.py` to match your log format.
- Or replace the CSV files with your own log data before running `csv_to_db.py`.

### Modify visualizations:
- Edit `AutoVisualizer.py` to change chart styles or add new types.

### Adjust query classification:
- Edit `is_relevant.py` to fine-tune what counts as a log-related query.

---

## 🛠️ Troubleshooting

### Database connection issues:
- Ensure `logs2.db` exists in the project root.
- Verify SQLite3 is installed.

### Missing dependencies:
- Run `pip install -r requirements.txt` again.

### API key errors:
- Check your `.env` file has valid keys.
- Ensure environment variables are loaded before running the apps.

---


