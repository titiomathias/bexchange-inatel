import json

def verify(data):
    try:
        with open("editais.json", "r", encoding="utf-8") as f:
            stored = json.load(f)

        if stored == data:
            return 0
        else:
            with open("editais.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return 1
    except Exception as e:
        print(f"Erro: {e}")
        return -1
