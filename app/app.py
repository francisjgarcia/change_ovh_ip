#!/usr/bin/env python
# -*- coding: 850 -*-
# -*- coding: utf-8 -*-

from dotenv import load_dotenv
import requests
import ovh
import json
import os
import time

load_dotenv()
OVHDomain = os.getenv("OVH_DOMAIN")
OVHEndPoint = os.getenv("OVH_ENDPOINT")
OVHApplicationKey = os.getenv("OVH_APPLICATION_KEY")
OVHApplicationSecret = os.getenv("OVH_APPLICATION_SECRET")
OVHConsumerKey = os.getenv("OVH_CONSUMER_KEY")
TelegramToken = os.getenv("TELEGRAM_TOKEN")
TelegramID = os.getenv("TELEGRAM_ID")
DynuUsername = os.getenv("DYNU_USERNAME")
DynuPassword = os.getenv("DYNU_PASSWORD")
ifconfig_web = os.getenv("IFCONFIG_WEB")
client = ovh.Client(endpoint=OVHEndPoint, application_key=OVHApplicationKey, application_secret=OVHApplicationSecret, consumer_key=OVHConsumerKey)

def check_ovh_ip():
    result = client.get('/domain/zone/' + OVHDomain + '/record', fieldType='A')
    global DomainID
    DomainID = json.dumps(result[0], indent=4)
    result = client.get('/domain/zone/' + OVHDomain + '/record/' + DomainID)
    OVHIP = json.dumps(result['target'], indent=4)
    global DomainIP
    DomainIP = OVHIP.replace('"', '')

def check_public_ip():
    global PublicIP
    PublicIP = requests.get(ifconfig_web).text

def telegram_alert(bot_message, bot_token, bot_chatID):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?parse_mode=html&disable_web_page_preview=True&chat_id=' + bot_chatID + '&text=' + bot_message
    response = requests.get(send_text)

def ovh_change_ip():
    result = client.put('/domain/zone/' + OVHDomain + '/record/' + DomainID, target=PublicIP)
    result = client.post('/domain/zone/' + OVHDomain + '/refresh')

def dynu_ip():
    params = (
        ('myip', 'PublicIP'),
        ('username', DynuUsername),
        ('password', DynuPassword),
    )
    response = requests.get('http://api.dynu.com/nic/update', params=params)

while 1:
    check_ovh_ip()
    check_public_ip()
    if DomainIP != PublicIP:
        web_status_code = requests.get(ifconfig_web).status_code
        if web_status_code == 200:
            try:
                ovh_change_ip()
                print('La IP publica en OVH ha sido modificada de ' + DomainIP + ' a ' + PublicIP)
                telegram_alert("🌐 <b>Cambio de IP</b> %0A La nueva IP es " + PublicIP, TelegramToken, TelegramID)
            except:
                print('Ha habido un fallo al modificar el registro DNS en OVH.')
                telegram_alert("🔥 <b>ERROR (OVH)</b> %0A Ha sucedido un error al modificar un registro de la zona DNS " + OVHDomain, TelegramToken, TelegramID)
            try:
                dynu_ip()
                print('La IP publica en DYNU ha sido modificada de ' + DomainIP + ' a ' + PublicIP)
            except:
                print('Ha habido un fallo al modificar el registro DNS en OVH.')
                telegram_alert("🔥 <b>ERROR (DYNU)</b> %0A Ha sucedido un error al modificar la IP Pública del dominio serverfjg.dynu.net", TelegramToken, TelegramID)
    time.sleep(60)
