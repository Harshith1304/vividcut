VividCut - Mobile Video Editor

VividCut is a high-performance mobile video editing application built with React Native (Expo) and FastAPI. It allows users to overlay text and images on videos, apply filters, customize fonts, and render the final output using FFmpeg.

✨ Features

Video Editing: Upload a source video and overlay multiple elements.

Text Overlays:

Custom Fonts (Impact, Arial, Courier, Georgia, Verdana).

Color Selection (Mint, White, Gold, etc.).

Drag to move, pinch/buttons to scale.

Tap to edit text content.

Image Overlays:

Upload images from gallery.

Apply filters (Grayscale, Sepia, Invert).

System-native cropping and editing before upload.

Real-time Controls:

Timeline editing (Start/End times).

Delete individual overlays or the main video.

Rendering Engine:

FastAPI backend using FFmpeg for frame-accurate rendering.

Background task processing.

Auto-download of the final result.

🛠️ Prerequisites

Node.js & npm (For Frontend).

Python 3.9+ (For Backend).

FFmpeg:

Windows: Download build from gyan.dev, extract, and add bin folder to System PATH.

Mac: brew install ffmpeg.

Expo Go App: Installed on your physical Android/iOS device.

🚀 Backend Setup (FastAPI)

Navigate to the backend folder:

cd backend


Create and activate virtual environment:

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate


Install dependencies:

pip install fastapi uvicorn python-multipart


Start the Server:

uvicorn main:app --host 0.0.0.0 --port 8000 --reload


📱 Frontend Setup (React Native)

Navigate to the frontend folder:

cd frontend


Install dependencies:

npm install
npx expo install expo-image-picker expo-av


Configure IP Address:

Find your computer's local IP address (ipconfig on Windows, ifconfig on Mac).

Note: If using a Mobile Hotspot, look for the adapter usually named "Local Area Connection* X" (often 192.168.137.1).

Open frontend/App.js and update line 11:

const API_URL = 'http://YOUR_IP_ADDRESS:8000';


Start the App:

npx expo start


Scan the QR code with the Expo Go app on your phone.

⚠️ Troubleshooting Connection Issues

If your phone says "Network Request Failed" or "Upload Failed":

Firewall (Most Common):

Open "Allow an app through Windows Firewall".

Find python.exe (or main).

Ensure BOTH "Private" and "Public" checkboxes are checked.

Same Network: Ensure your phone and laptop are on the exact same Wi-Fi network (or phone is connected to Laptop's hotspot).

Correct IP: Double-check ipconfig to ensure your IP hasn't changed.

🎨 Project Structure

VividCut/
├── backend/
│   ├── main.py           # FastAPI Server & FFmpeg Logic
│   ├── uploads/          # Temp storage for uploaded assets
│   └── outputs/          # Storage for rendered videos
│
└── frontend/
    ├── App.js            # Main React Native Application
    ├── assets/           # Icons and splash screens
    └── package.json      # JS Dependencies
