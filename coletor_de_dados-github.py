import requests
import json
import time
# Auemntar o numero de fields no thinkspeak para conseguir colocar dados do solo
# Configurações ThingSpeak
THINGSPEAK_READ_API_KEY = ''
THINGSPEAK_CHANNEL_ID = ''
THINGSPEAK_URL = f'https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/feeds.json?api_key={THINGSPEAK_READ_API_KEY}&results=1'

def fetch_data():
    response = requests.get(THINGSPEAK_URL)
    if response.status_code == 200:
        data = response.json()
        print("Dados recebidos do ThingSpeak:", data)  # Adiciona impressão dos dados recebidos
        if 'feeds' in data and len(data['feeds']) > 0:
            feed = data['feeds'][0]
            
            formatted_data = {
                'created_at': feed['created_at'],
                'entry_id': feed['entry_id'],
                'field1': feed.get('field1'),
                'field2': feed.get('field2'),
                'field3': feed.get('field3'),
                'field4': feed.get('field4')
            }
            print("Dados formatados:", formatted_data)  # Adiciona impressão dos dados formatados
            return formatted_data
        else:
            print("Nenhum dado disponível no ThingSpeak.")
    else:
        print(f"Erro ao conectar ao ThingSpeak: {response.status_code}")
    return None

def main():
    while True:
        data = fetch_data()
        if data:
            with open('data.json', 'a') as f:
                json.dump(data, f)
                f.write('\n')
            print(f'Dados coletados: {data}')
        else:
            print("Nenhum dado foi coletado.")
        time.sleep(10)  # Tempo de espera ajustado para 10 segundos para depuração

if __name__ == "__main__":
    main()
