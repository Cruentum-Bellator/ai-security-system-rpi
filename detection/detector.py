import onnxruntime as ort
import numpy as np
import cv2
from utils.video_utils import letterbox, xywh2xyxy, nms_xyxy, scale_coords

class PersonDetector:
    def __init__(self, onnx_path, input_size, conf_thres, iou_thres, person_cls_id=0, force_cpu=True):
        available = ort.get_available_providers()
        providers = (["CPUExecutionProvider"]
                     if (force_cpu or "CUDAExecutionProvider" not in available)
                     else ["CUDAExecutionProvider", "CPUExecutionProvider"])
        self.session = ort.InferenceSession(onnx_path, providers=providers)
        self.in_name = self.session.get_inputs()[0].name
        self.input_size = input_size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.person_id = person_cls_id

    def run(self, frame):
        h0, w0 = frame.shape[:2]
        img, r, dxy = letterbox(frame, (self.input_size, self.input_size))
        img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_in = img_in.transpose(2, 0, 1).astype(np.float32) / 255.0
        img_in = np.expand_dims(img_in, 0)

        out = self.session.run(None, {self.in_name: img_in})[0]
        pred = np.squeeze(out)
        if pred.ndim == 1:
            pred = pred[:, None]

        boxes_xywh = pred[0:4, :].T
        cls_scores = pred[4:, :].T
        person_scores = cls_scores[:, self.person_id]

        mask = person_scores >= self.conf_thres
        boxes_xywh = boxes_xywh[mask]
        person_scores = person_scores[mask]

        if boxes_xywh.size == 0:
            return [], [], (r, dxy, w0, h0)

        boxes_xyxy = xywh2xyxy(boxes_xywh)
        keep = nms_xyxy(boxes_xyxy, person_scores, self.iou_thres)
        boxes_xyxy = boxes_xyxy[keep]
        person_scores = person_scores[keep]
        boxes_xyxy = scale_coords(boxes_xyxy, r, dxy, w0, h0)
        return boxes_xyxy, person_scores, (r, dxy, w0, h0)
