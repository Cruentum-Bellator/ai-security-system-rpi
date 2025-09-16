import requests
import os
import base64

class SupabaseUploader:
    """
    Basit REST: /rest/v1/{table}
    Table örn: records  (columns: path(text), gender(text), score(float), ts(timestamp), note(text))
    """
    def __init__(self, url:str, anon_key:str, table:str):
        self.url = url.rstrip("/")
        self.key = anon_key
        self.table = table

    def insert_record(self, payload:dict):
        if not (self.url and self.key and self.table):
            print("[Supabase] Ayarlar eksik, kayıt atlandı.")
            return False
        api = f"{self.url}/rest/v1/{self.table}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        try:
            r = requests.post(api, headers=headers, json=payload, timeout=30)
            if r.status_code in (200,201):
                print("[Supabase] Kayıt eklendi.")
                return True
            print("[Supabase] Hata:", r.status_code, r.text)
        except Exception as e:
            print("[Supabase] İstisna:", e)
        return False
