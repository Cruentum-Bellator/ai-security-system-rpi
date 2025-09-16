import cv2
import numpy as np
import onnxruntime as ort

class GenderClassifier:
    """
    Opsiyonel ONNX cinsiyet sınıflandırıcı.
    - Model yoksa çalışmayı bozmaz, 'unknown' döner.
    - Örn giriş: 224x224 RGB normalize [0..1]
    - Çıkış: [p_female, p_male] (varsayım)
    """
    def __init__(self, onnx_path:str|None=None):
        self.enabled = False
        self.input_size = 224
        if onnx_path and len(onnx_path) > 0:
            try:
                self.session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
                self.in_name = self.session.get_inputs()[0].name
                self.enabled = True
            except Exception as e:
                print("[Gender] Model yüklenemedi, devre dışı:", e)

    def predict(self, frame, box_xyxy):
        if not self.enabled:
            return "unknown", 0.0
        x1, y1, x2, y2 = map(int, box_xyxy)
        x1 = max(0, x1); y1 = max(0, y1)
        face = frame[y1:y2, x1:x2]
        if face.size == 0:
            return "unknown", 0.0
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        face = cv2.resize(face, (self.input_size, self.input_size))
        inp = face.astype(np.float32) / 255.0
        inp = np.transpose(inp, (2,0,1))[None, ...]
        out = self.session.run(None, {self.in_name: inp})[0].squeeze()
        # varsayım: [p_female, p_male]
        if out.ndim == 0:
            return "unknown", 0.0
        label = "female" if out[0] >= out[1] else "male"
        score = float(max(out))
        return label, score
