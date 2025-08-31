Floratrack Survey App
Project Overview
The Floratrack Survey App is a citizen science project prototype designed to help conservationists track and monitor the location of Rhodesian Teak trees. The application consists of two main components: a user-friendly frontend built with Streamlit for image and location data capture, and a backend API for AI-powered plant detection and data storage.

This project empowers users to contribute to conservation efforts by simply taking a picture of a potential Rhodesian Teak tree, which is then analyzed by an AI model, and its location is automatically recorded for further analysis.

Project Components
Frontend (app.py):

A web interface for users to upload images of plants.

Uses JavaScript within an HTML component to request and capture the user's GPS coordinates.

Sends the image and GPS data to the backend API.

Displays the results, including the AI model's detection and the captured location.

Backend (main.py):

A REST API built with FastAPI that acts as the server.

Receives image and GPS data from the frontend.

Serves as a placeholder for the AI model logic to process the image.

Crucially, this is where the data storage logic is implemented, saving the detection results and location to a database (e.g., SQLite, PostgreSQL, etc.).

Prerequisites
Before you begin, ensure you have the following installed on your system:

Python 3.8+

pip (Python package installer)

Setup and Installation
Follow these steps to get the project up and running.

Install necessary dependencies
pip install streamlit streamlit-components-html fastapi uvicorn python-multipart

You will need two separate terminal windows to run the frontend and the backend simultaneously.

Step 1: Run the Backend API
Navigate to your project directory 
cd Floratrack-prototype\moonshot\backend

create a virtual environment
python -m venv venv_backend

activate virtual environment
 .\venv_backend\Scripts\activate

Install necessary dependencies
pip install requirements.txt

In your terminal, run the following command to start the backend server:
uvicorn app:app --reload

This will start the server on http://127.0.0.1:8000. 

Step 2: Run the Frontend App

Navigate to your project directory 
cd frontend

create a virtual environment
python -m venv venv_frontend

activate virtual environment
 .\venv_frontend\Scripts\activate

Install necessary dependencies
pip install requirements.txt

In your terminal, run the Streamlit app.
 python -m streamlit run app.py

This will open a new tab in your default web browser, displaying the Floratrack Survey App.
