import urequests
import network
import time
import json
from machine import Pin, SoftI2C, ADC
import ssd1306
import dht

def do_connect(ssid, key):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, key)
        while not wlan.isconnected():
            pass
    ip, mascara, gateway, dns = wlan.ifconfig()
    print(f'network config: ip = {ip}, máscara = {mascara}, gateway = {gateway}, dns = {dns}')

def collect_data(dht_sensor, soil_sensor):
    dht_sensor.measure()
    time.sleep(0.5)
    umidade = dht_sensor.humidity()
    temperatura = dht_sensor.temperature()
    umidade_solo = soil_sensor.read()
    return temperatura, umidade, umidade_solo

def determine_condition(moisture_value):
    if moisture_value is None:
        return "Desconhecido"
    moisture_value = int(moisture_value)
    wet_threshold = 2500
    dry_threshold = 4000
    if moisture_value < dry_threshold and moisture_value > wet_threshold:
        return "Umidade ideal"
    elif moisture_value < wet_threshold:
        return "Muito umido"
    else:
        return "Muito seco"

def main():
    # Configurações para o ThingSpeak
    HTTP_HEADERS = {'Content-Type': 'application/json'}
    THINGSPEAK_WRITE_API_KEY = ""
    UPDATE_TIME_INTERVAL = 2000 # in ms (ajustado para 10 segundos para depuração)
    last_update = time.ticks_ms()

    # Configurações do Wi-fi
    do_connect('', '')

    # Configurações para o display OLED ssd1306
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    dht_sensor = dht.DHT22(Pin(4))
    soil_sensor = ADC(Pin(34))
    soil_sensor.atten(ADC.ATTN_11DB) # Configura a atenuação para faixa completa (0-3.3V)
    relay = Pin(2, Pin.OUT)

    while True:
        if time.ticks_ms() - last_update >= UPDATE_TIME_INTERVAL:
            temperatura, umidade, umidade_solo = collect_data(dht_sensor, soil_sensor)
            condicao_umidade = determine_condition(umidade_solo)
            # Envio das leituras de temperatura, umidade, umidade do solo e condição da umidade
            json_readings = {
                'field1': temperatura,
                'field2': umidade,
                'field3': umidade_solo,
                'field4': condicao_umidade # Adicione esta linha para enviar a condição de umidade
            }
            print("Dados sendo enviados ao ThingSpeak:", json_readings) # Adiciona impressão dos dados enviados
            try:
                request = urequests.post('https://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY, json=json_readings, headers=HTTP_HEADERS)
                request.close()
            except OSError as e:
                print(f'Erro no envio dos dados ({e})')

            oled.fill(0)
            oled.show()
            oled.text('Temp.: ' + str(temperatura) + 'C', 20, 10)
            oled.text('Umid.: ' + str(umidade) + '%', 20, 30)
            oled.text('Solo: ' + condicao_umidade, 0, 50)
            oled.show()
            print(f'Temperatura = {temperatura}, Umidade = {umidade}, Umidade do Solo = {umidade_solo} - Condição: {condicao_umidade}')

            if condicao_umidade == "Muito seco":
                for _ in range(10):  # Pisca rapidamente como um pisca-alerta
                    relay.value(True)
                    time.sleep(0.5)  # Tempo ajustado
                    relay.value(False)
                    time.sleep(0.5)  # Tempo ajustado
            elif condicao_umidade == "Muito umido":
                relay.value(True)
                time.sleep(2.5)
                relay.value(False)
                time.sleep(2.5)
            else:
                relay.value(False)

            last_update = time.ticks_ms()

main()
