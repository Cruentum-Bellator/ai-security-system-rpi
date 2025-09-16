# AI Security System 🚀🔒

An **AI-powered security system** built on Raspberry Pi.  
This project integrates **computer vision, robotics, cloud services, and IoT messaging** into one platform:  

- YOLOv8 (ONNX) for **real-time person detection** 🧑‍🦱  
- Stepper motor (28BYJ-48 + ULN2003) for **camera tracking** 🎥  
- Flask web server for **live MJPEG video streaming** 🌐  
- Supabase for **cloud storage + database logging** ☁️  
- Telegram bot for **real-time alerts with video evidence** 📲  

---

## 📂 Project Structure
ai-security-system/
│── main.py # Entry point - integrates all modules
│── config.py # Central configuration (pins, thresholds)
│── detector.py # YOLOv8 ONNX person detection
│── gender_classifier.py # Optional gender classification
│── motor_control.py # Stepper motor control (GPIO)
│── video_utils.py # Helper functions (letterbox, NMS)
│── stream_server.py # Flask MJPEG streaming server
│── telegram_bot.py # Telegram bot integration
│── requirements.txt # Python dependencies
│── .env.example # Example environment variables
│── README.md # Documentation

---

## ⚙️ Installation

### 1. Clone the repository
```
git clone https://github.com/<your-username>/ai-security-system.git
cd ai-security-system
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
### 2. Create a virtual environment
```
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
### 3. Install dependencies
```
pip install -r requirements.txt

```
Configure .env
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
TELEGRAM_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
STREAM_USER=admin
STREAM_PASS=1234
```

---

👉 Yahya, do you want me to **include setup instructions for creating the Telegram bot and Supabase project** inside the README as well, so new users can replicate your system step by step?

