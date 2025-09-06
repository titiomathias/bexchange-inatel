import json
import cfscrape
from bs4 import BeautifulSoup
from utils.verifier import verify

url = "https://inatel.br/intercambios/editais/lista-editais"

def get_data_edital(soup: BeautifulSoup):
    return {
        "name": soup.span.get_text().strip(),
        "link": soup.a.get("href")
    }

def scrap(file: str):
    try:
        soup = BeautifulSoup(file, 'html.parser')

        abertos = soup.find_all("details", attrs={"name":"arrow-editais1"})[0]

        editais = abertos.find_all(class_="doc")

        dados = list(map(get_data_edital, editais))

        return dados
    except Exception as e:
        print(e)

        return None
    

def request_site():
    response = cfscrape.create_scraper().get(url)

    if response.status_code == 200:
        data = scrap(response.content)
        
        try:
            code = verify(data)

            print(code)

            if code == 1:
                return {"code": 1, "data": data, "status": response.status_code}
            else:
                return {"code": 0}
        except Exception as e:
            print("Ocorreu um erro ao verificar o json", e)
            return {"code": -1, "error": True} 
    else:
        return {"code": -1, "error": True, "status": response.status_code}
    

def listAll():
    with open("editais.json", "r", encoding="utf-8") as f:
        stored = json.load(f)
        return stored