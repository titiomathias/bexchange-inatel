from datetime import datetime
import json
import os

def verify(data):
    try:
        payload = {
            "last_check": datetime.now().isoformat(timespec="seconds"),
            "data": data
        }

        if not os.path.exists("editais.json"):
            with open("editais.json", "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=4)
            return 1

        with open("editais.json", "r", encoding="utf-8") as f:
            try:
                stored = json.load(f)
            except json.JSONDecodeError:
                stored = None

        with open("editais.json", "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=4)

        if stored and stored.get("data") == data:
            return 0 
        else:
            return 1

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return -1
