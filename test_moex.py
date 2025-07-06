import requests

url = "https://iss.moex.com/iss/securities/RU000A10BW96/securities.json?iss.meta=off"

try:
    response = requests.get(url, timeout=5)
    print("Status:", response.status_code)
    print("Content:", response.text[:1000])  # первые 200 символов
except requests.exceptions.RequestException as e:
    print("Ошибка:", e)