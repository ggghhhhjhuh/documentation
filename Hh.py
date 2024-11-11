import requests
import csv
import time
import json
import os

# Funkcja do pobierania danych z URL
def get_speedtest_data():
    url = "https://www.speedtest.pl/storage/live.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Sprawdzenie, czy odpowiedź jest poprawna (status 200)
        return response.json()  # Zwróć dane w formacie JSON
    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych: {e}")
        return None

# Funkcja do wczytywania zapisanych wyników z pliku CSV
def load_existing_results(filename="speedtest_results.csv"):
    existing_results = set()
    if os.path.exists(filename):
        with open(filename, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Tworzymy unikalny identyfikator na podstawie pola "time" i "isp"
                existing_results.add((row["time"], row["isp"]))
    return existing_results

# Funkcja do zapisywania danych do pliku CSV
def save_to_csv(data, filename="speedtest_results.csv"):
    try:
        with open(filename, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["time", "country", "isp", "latency", "download", "upload"])
            
            # Jeśli plik jest pusty, dodajemy nagłówki
            file.seek(0, 2)  # Przesuń wskaźnik na koniec pliku
            if file.tell() == 0:
                writer.writeheader()
            
            # Zapisujemy dane
            writer.writerow(data)
            print(f"Wynik zapisany: ISP = {data['isp']}, Czas = {data['time']}, Prędkość pobierania = {data['download']} Mbps")  # Komunikat na konsoli
    except Exception as e:
        print(f"Błąd podczas zapisywania danych do pliku CSV: {e}")

# Główna funkcja
def main():
    # Wczytanie już zapisanych wyników do zbioru (unikalne kombinacje time i isp)
    filename = "speedtest_results.csv"
    existing_results = load_existing_results(filename)

    while True:
        data = get_speedtest_data()
        if data:
            for record in data:
                # Sprawdzamy, czy ISP należy do jednej z czterech wymaganych wartości
                if record["isp"] in ["24IT MEDIA Sp. z o.o.", "Platkom Tele-Informatyka", "Net-ARN", "MGK"]:
                    # Sprawdzamy, czy wynik już został zapisany (na podstawie time i isp)
                    result_key = (record["time"], record["isp"])
                    if result_key not in existing_results:
                        # Jeśli wynik nie istnieje, zapisujemy go
                        record_data = {
                            "time": record["time"],
                            "country": record["country"],
                            "isp": record["isp"],
                            "latency": record["latency"],
                            "download": record["download"],
                            "upload": record["upload"]
                        }
                        save_to_csv(record_data, filename)
                        # Dodajemy nowy wynik do zbioru, aby uniknąć duplikatów
                        existing_results.add(result_key)
        
        # Odczekaj 5 sekund przed kolejnym pobraniem danych
        time.sleep(5)

if __name__ == "__main__":
    main()
