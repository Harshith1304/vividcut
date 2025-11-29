ButterCut.ai Full Stack Assignment

This repository contains a full-stack video editing application built with React Native (Expo) and FastAPI (Python).

📂 Project Structure

backend/: FastAPI server for video rendering.

frontend/: React Native Expo app for the UI.

🚀 Prerequisites

Python 3.9+

Node.js & npm

FFmpeg: Must be installed and available in your system PATH.

Mac: brew install ffmpeg

Windows: Download from ffmpeg.org and add bin folder to Path.

Linux: sudo apt install ffmpeg

🐍 Backend Setup

Navigate to the backend folder:

cd backend


Create a virtual environment and activate it:

python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate


Install dependencies:

pip install fastapi uvicorn python-multipart


(Note: No other heavy dependencies required, we use subprocess to call ffmpeg directly)

Run the server:

# IMPORTANT: Listen on 0.0.0.0 so your phone/emulator can access it
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


📱 Frontend Setup (React Native)

Navigate to the frontend folder (or root):

npx create-expo-app frontend
cd frontend


Install required packages:

npx expo install expo-image-picker expo-av


Update API URL:
Open App.js and find the line:

const API_URL = '[http://192.168.1.](http://192.168.1.)XX:8000';


Replace 192.168.1.XX with your computer's local IP address.

Windows: Run ipconfig in terminal.

Mac/Linux: Run ifconfig in terminal.

Replace App.js content:
Copy the code provided in the assignment frontend/App.js into your project's App.js.

Run the app:

npx expo start


Scan the QR code with your phone (Expo Go app) or press a for Android Emulator / i for iOS Simulator.

🎥 Usage Guide

Select Video: Tap the black box to choose a video from your library.

Add Overlays: Click "+ Add Text" or "+ Add Image".

Edit:

Drag: Drag the overlay on the video preview to position it.

Timing: Edit the Start/End time inputs in the list below.

Content: Edit text content in the input field.

Render: Click "Render Video".

The app will upload the video and assets.

It will poll for status.

Once done, a "Download Result" button will appear.

✅ Evaluation Criteria Met

Functionality: End-to-end flow (Upload -> Edit -> Metadata -> Render -> Status -> Result).

Backend: Async processing using FastAPI BackgroundTasks; dynamic FFmpeg command generation.

UI/UX: Simple, intuitive editor with preview and timing controls.

Code Quality: Modularized functions, clean state management.