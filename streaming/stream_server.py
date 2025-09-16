from flask import Flask, Response, request, abort
from functools import wraps
import threading
import time
import cv2

def make_app(username, password):
    app = Flask(__name__)
    latest_jpeg_lock = threading.Lock()
    latest_jpeg = {"buf": None}

    def check_auth(u, p):
        return u == username and p == password

    def auth_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return Response(
                    "Authentication required", 401,
                    {"WWW-Authenticate": 'Basic realm="Login Required"'}
                )
            return fn(*args, **kwargs)
        return wrapper

    @app.route("/")
    @auth_required
    def index():
        return "MJPEG stream is live. Visit /mjpeg"

    @app.route("/mjpeg")
    @auth_required
    def mjpeg():
        def gen():
            while True:
                with latest_jpeg_lock:
                    buf = latest_jpeg["buf"]
                if buf is not None:
                    yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
                           buf + b"\r\n")
                time.sleep(0.02)
        return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

    # Publisher: main loop buna frame verir
    def publish_frame(frame_bgr):
        ret, jpeg = cv2.imencode(".jpg", frame_bgr)
        if ret:
            jb = jpeg.tobytes()
            with latest_jpeg_lock:
                latest_jpeg["buf"] = jb

    return app, publish_frame
