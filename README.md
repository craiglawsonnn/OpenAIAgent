# AI-Powered Customer Service Chatbot

A full-stack AI chatbot system that simulates a production-ready customer support agent using OpenAI, Flask, JavaScript, and SQLite. This project features natural conversation flow, function calling, memory summarization, database interaction, and a responsive chat UI.

---

##  Tech Stack

- **Backend:** Python, Flask, OpenAI API (function calling)
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Database:** SQLite (for simulating order lookup + session memory)
- **AI Model:** GPT-3.5-Turbo-1106 (with support for GPT-4o)

---

## Features

✅ Message-based chatbot interface  
✅ Function calling with real-time tool simulation  
✅ SQLite-backed order tracking  
✅ Responsive, animated chat UI with typing effect  
✅ Memory summarization every 6+ turns to reduce token usage  
✅ Fallback handling for unknown order IDs  
✅ Fully configurable via `tools.json` for extensibility

---

## Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/craiglawsonnn/OpenAIAgent.git
cd OpenAIAgent
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

5. **Initialize the database**
```bash
python -c "from db import init_db; init_db()"
```

6. **Start the Flask server**
```bash
python app.py
```

7. **Visit the chatbot UI**
Go to `http://127.0.0.1:5000/` in your browser.

---

## Project Structure

```
├── app.py               # Flask backend
├── db.py                # SQLite init + helper
├── tools.json           # Tool definitions for function calling
├── requirements.txt     # Python dependencies
├── .env                 # Your OpenAI API key
├── templates/
│   └── index.html       # Frontend chat UI
├── static/              # (Optional) future CSS/JS
└── venv/                # Virtual environment
```

---

## Memory Optimization

To avoid expensive token inflation, this chatbot:
- Tracks message history for each session
- Summarizes it every 6 turns using GPT
- Feeds a compressed context back into the model
- Simulates long-term memory efficiently

---

## Sample Queries

Try asking:
- `What's the status of order 5672?`
- `I'd like to return order 1234 due to damage.`
- `Can I update my phone number on file?`
- `Check refund ABC123.`

---

## Future Improvements

-  User authentication + session persistence
-  Dashboard to view sessions/summaries
-  Switch to PostgreSQL or MongoDB
-  Add natural language analytics & tagging
-  WebSocket or streaming response support
-  Multi-language translation support

---

## Screenshots


![image](https://github.com/user-attachments/assets/5a4a504a-5903-4fff-a09f-60f48c3e841f)

---

## License

MIT License — free to use, modify, and share.

---

##  Author

**Craig Lawson**  
 Developer |  Systems Thinker |  Based in Ireland  
Feel free to [connect on LinkedIn](https://www.linkedin.com/in/craig-law-son) or [drop a message](mailto:craig.lawson89@gmail.com)!

---

## Acknowledgements

- [OpenAI](https://platform.openai.com)
- Everyone building transparent, helpful AI tools
