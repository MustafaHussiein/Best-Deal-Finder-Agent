Best Deal Finder
AI-powered product comparison with citations - 100% Python, No Node.js Required!

Prerequisites

Python 3.8+ installed and added to your PATH
Basic familiarity with terminal/command prompt
No Node.js needed! This is a pure Python application


1. Install Ollama

Download and install Ollama from https://ollama.com/ for your OS.
Open a terminal and run:

bashollama pull llama3.1

Start Ollama service:

bashollama serve

Note: Keep Ollama running in the background while using the app.


2. Install Python Dependencies
Quick Setup (All-in-One)
bashpip install Flask flask-cors requests streamlit pandas
Or Use Requirements File
bashpip install -r requirements.txt

3. Run the Application
You have three options to start the app:
Option 1: Standalone (Recommended - Single Command!)
bashpython standalone_app.py

Starts both backend and frontend in one process
Open your browser at http://localhost:8501

Option 2: Using Python Script
bashcd frontend
python run_app.py

Uses Python to run Streamlit (no streamlit run command needed)
Open your browser at http://localhost:8501

Option 3: Separate Backend & Frontend
Terminal 1 - Backend:
bashcd backend
python server.py
Terminal 2 - Frontend:
bashcd frontend
streamlit run app.py

Backend runs on http://localhost:4000
Frontend opens at http://localhost:8501


4. Optional: Warm Up Ollama (Recommended)
To avoid the first request timeout, pre-load the model:
bashpython warmup_ollama.py
This loads the Ollama model into memory before starting the app, making the first query much faster!
