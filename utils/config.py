import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "records")

STREAM_USER = os.getenv("STREAM_USER", "admin")
STREAM_PASS = os.getenv("STREAM_PASS", "admin")

# Model yolları
YOLO_ONNX_PATH = os.getenv("YOLO_ONNX_PATH", "yolov8n.onnx")
GENDER_ONNX_PATH = os.getenv("GENDER_ONNX_PATH", "")  # opsiyonel

# Çeşitli ayarlar
INPUT_SIZE = int(os.getenv("INPUT_SIZE", "640"))
CONF_THRES = float(os.getenv("CONF_THRES", "0.4"))
IOU_THRES  = float(os.getenv("IOU_THRES", "0.45"))
PERSON_CLASS_ID = 0

VIDEO_SECONDS = int(os.getenv("VIDEO_SECONDS", "10"))
VIDEO_FPS = int(os.getenv("VIDEO_FPS", "20"))
FRAME_W = int(os.getenv("FRAME_W", "640"))
FRAME_H = int(os.getenv("FRAME_H", "480"))

# Step motor
GPIO_PINS = [17, 18, 27, 22]   # IN1..IN4
DEADBAND_PX = int(os.getenv("DEADBAND_PX", "25"))
STEP_GAIN = float(os.getenv("STEP_GAIN", "0.02"))   # pixel -> step
STEP_MIN = int(os.getenv("STEP_MIN", "1"))
STEP_MAX = int(os.getenv("STEP_MAX", "12"))
STEP_DELAY = float(os.getenv("STEP_DELAY", "0.002"))
MOVE_COOLDOWN = float(os.getenv("MOVE_COOLDOWN", "0.03"))
