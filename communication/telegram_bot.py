import requests

class TelegramClient:
    def __init__(self, token:str, chat_id:str):
        self.token = token
        self.chat_id = chat_id

    def send_video(self, filepath, caption="Hareket algılandı!"):
        if not self.token or not self.chat_id:
            print("[Telegram] Token/ChatID eksik, gönderim atlandı.")
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendVideo"
        try:
            with open(filepath, "rb") as f:
                data = {"chat_id": self.chat_id, "caption": caption}
                files = {"video": f}
                r = requests.post(url, data=data, files=files, timeout=60)
            if r.status_code == 200:
                print("[Telegram] Video gönderildi.")
                return True
            print("[Telegram] Hata:", r.status_code, r.text)
        except Exception as e:
            print("[Telegram] İstisna:", e)
        return False
