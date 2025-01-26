"""
MicroPython IoT Weather Station Example for Wokwi.com

To view the data:

1. Go to http://www.hivemq.com/demos/websocket-client/
2. Click "Connect"
3. Under Subscriptions, click "Add New Topic Subscription"
4. In the Topic field, type "wokwi-weather" then click "Subscribe"

Now click on the DHT22 sensor in the simulation,
change the temperature/humidity, and you should see
the message appear on the MQTT Broker, in the "Messages" pane.

Copyright (C) 2022, Uri Shaked

https://wokwi.com/arduino/projects/322577683855704658
"""

import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient
import urequests

# MQTT Server Parameters
MQTT_CLIENT_ID = "micropython-weather-demo"
MQTT_BROKER    = "broker.mqttdashboard.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "wokwi-weather"

# ThingSpeak Configuration
THINGSPEAK_URL = "http://api.thingspeak.com/update"
THINGSPEAK_API_KEY = "YOUR_API_KEY"  # Replace with your ThingSpeak API key

def send_to_thingspeak(temp, hum):
    print("Enviando datos a ThingSpeak...")
    try:
        # Crear URL con parámetros
        url = f"{THINGSPEAK_URL}?api_key={THINGSPEAK_API_KEY}&field1={temp}&field2={hum}"
        
        # Hacer la solicitud HTTP
        response = urequests.get(url)
        if response.status_code == 200:
            print("Datos enviados correctamente!")
        else:
            print(f"Error al enviar datos: {response.status_code}")
        response.close()
    except Exception as e:
        print("Error al conectar con ThingSpeak:", e)

sensor = dht.DHT22(Pin(15))

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")

prev_weather = ""
while True:
  print("Midiendo condiciones del clima... ", end="")
  sensor.measure()
  temp = sensor.temperature()
  hum = sensor.humidity()
  
  message = ujson.dumps({
    "temperatura": temp,
    "humedad": hum,
  })
  
  if message != prev_weather:
    print("Actualizado!")
    print("Reportando para el tópico MQTT {}: {}".format(MQTT_TOPIC, message))
    client.publish(MQTT_TOPIC, message)
    # Enviar datos a ThingSpeak
    send_to_thingspeak(temp, hum)
    prev_weather = message
  else:
    print("Sin cambios")
  
  time.sleep(1)
