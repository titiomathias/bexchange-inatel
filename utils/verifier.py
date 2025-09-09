import json
import os

def verify(data):
    try:
        if not os.path.exists("editais.json"):
            with open("editais.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return 1

        with open("editais.json", "r", encoding="utf-8") as f:
            try:
                stored = json.load(f)
            except json.JSONDecodeError:
                stored = None

        if stored == data:
            return 0
        else:
            with open("editais.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return 1

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return -1
