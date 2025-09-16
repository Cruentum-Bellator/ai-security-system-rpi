import cv2
import time
from picamera2 import Picamera2
from datetime import datetime
import os

from utils.config import *
from detection.detector import PersonDetector
from detection.gender_classifier import GenderClassifier
from control.motor_control import StepMotor
from communication.telegram_bot import TelegramClient
from communication.supabase_uploader import SupabaseUploader
from streaming.stream_server import make_app
import threading

def clamp(v, lo, hi): return max(lo, min(hi, v))

def run_stream(app):
    # Flask'i ayrı thread'de başlat
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, threaded=True)

def main():
    # ==== Bileşenler ====
    detector = PersonDetector(
        onnx_path=YOLO_ONNX_PATH,
        input_size=INPUT_SIZE,
        conf_thres=CONF_THRES,
        iou_thres=IOU_THRES,
        person_cls_id=PERSON_CLASS_ID,
        force_cpu=True
    )
    genderer = GenderClassifier(GENDER_ONNX_PATH)
    motor = StepMotor(GPIO_PINS, step_delay=STEP_DELAY)
    tele = TelegramClient(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    supa = SupabaseUploader(SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_TABLE)
    app, publish_frame = make_app(STREAM_USER, STREAM_PASS)

    # ==== Yayın Sunucusu ====
    t = threading.Thread(target=run_stream, args=(app,), daemon=True)
    t.start()
    print("[Stream] http://<pi_ip>:5000  (Basic Auth ile)")

    # ==== Kamera ====
    picam2 = Picamera2()
    cfg = picam2.create_preview_configuration(main={"format":"RGB888","size":(FRAME_W, FRAME_H)})
    picam2.configure(cfg)
    picam2.start()
    time.sleep(1.0)

    center_x = FRAME_W // 2
    last_move_t = 0.0

    # Video kaydı
    writer = None
    recording = False
    rec_start = 0
    video_name = ""

    try:
        while True:
            frame = picam2.capture_array()       # BGR değil, RGB gelir → çevir
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            boxes, scores, _ = detector.run(frame)

            # Yayın için frame'i hemen publish et
            publish_frame(frame)

            # Çizim & seçim
            target_idx = None
            if len(boxes):
                centers_x = ((boxes[:,0] + boxes[:,2]) / 2)
                diffs = abs(centers_x - center_x)
                target_idx = int(diffs.argmin())

            # Motor kontrol
            if target_idx is not None:
                x1,y1,x2,y2 = boxes[target_idx]
                cx = int((x1 + x2)/2)
                dx = cx - center_x
                if abs(dx) > DEADBAND_PX:
                    steps = int(abs(dx) * STEP_GAIN)
                    steps = clamp(steps, STEP_MIN, STEP_MAX)
                    now = time.time()
                    if now - last_move_t >= MOVE_COOLDOWN:
                        motor.step(steps if dx > 0 else -steps)
                        last_move_t = now
                cv2.line(frame, (center_x, 0), (center_x, FRAME_H), (255,255,255), 1)
                cv2.putText(frame, f"dx={dx}", (center_x+10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

            # Video tetikleme: kişi varsa kayıt başlat, yoksa durdur
            person_detected = len(boxes) > 0
            if person_detected and not recording:
                video_name = f"motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                writer = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), VIDEO_FPS, (FRAME_W, FRAME_H))
                recording = True
                rec_start = time.time()
                print("[Video] Kayıt başladı:", video_name)

                # İlk kareden supabase'e foto ve meta
                tx1,ty1,tx2,ty2 = map(int, boxes[target_idx]) if target_idx is not None else (0,0,FRAME_W,FRAME_H)
                gender, gscore = genderer.predict(frame, (tx1,ty1,tx2,ty2))
                thumb = frame.copy()
                cv2.rectangle(thumb, (tx1,ty1),(tx2,ty2),(0,255,0),2)
                thumb_name = video_name.replace(".mp4", ".jpg")
                cv2.imwrite(thumb_name, thumb)

                supa.insert_record({
                    "path": thumb_name,          # ya storage link ya da sadece isim (senin tablo şeman göre)
                    "gender": gender,
                    "score": gscore,
                    "ts": datetime.now().isoformat(),
                    "note": "AI alarm snapshot"
                })

            if recording and writer is not None:
                writer.write(frame)
                if time.time() - rec_start >= VIDEO_SECONDS or not person_detected:
                    writer.release()
                    writer = None
                    recording = False
                    print("[Video] Kayıt bitti, Telegram'a gönderiliyor...")
                    tele.send_video(video_name, caption="AI Alarm: İnsan algılandı")
                    # İsteğe bağlı: dosyayı silmek istersen:
                    # os.remove(video_name)

            # FPS (konsola hafif log)
            # (OpenCV penceresi açmıyoruz; yayın tarayıcıdan izlenecek)
            time.sleep(0.005)

    except KeyboardInterrupt:
        print("\n[EXIT] Durduruluyor...")
    finally:
        if writer is not None:
            writer.release()
        motor.cleanup()
