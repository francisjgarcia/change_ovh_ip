#!/usr/bin/env python

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import requests
import ovh
import json
import os
import time
import ipaddress

load_dotenv()
telegram_alert_bot = telepot.Bot(os.getenv("TELEGRAM_TOKEN"))
telegram_alert_id = os.getenv("TELEGRAM_ID")
OVHDomain = os.getenv("OVH_DOMAIN")
OVHEndPoint = os.getenv("OVH_ENDPOINT")
OVHApplicationKey = os.getenv("OVH_APPLICATION_KEY")
OVHApplicationSecret = os.getenv("OVH_APPLICATION_SECRET")
OVHConsumerKey = os.getenv("OVH_CONSUMER_KEY")
DynuUsername = os.getenv("DYNU_USERNAME")
DynuPassword = os.getenv("DYNU_PASSWORD")
ifconfig_web = os.getenv("IFCONFIG_WEB")
client = ovh.Client(endpoint=OVHEndPoint, application_key=OVHApplicationKey, application_secret=OVHApplicationSecret, consumer_key=OVHConsumerKey)

def check_ovh_ip():
    try:
        result = client.get('/domain/zone/' + OVHDomain + '/record', fieldType='A')
        global DomainID
        DomainID = json.dumps(result[0], indent=4)
        result = client.get('/domain/zone/' + OVHDomain + '/record/' + DomainID)
        OVHIP = json.dumps(result['target'], indent=4)
        global DomainIP
        DomainIP = OVHIP.replace('"', '')
        ipaddress.ip_address(DomainIP)
    except:
        print("No se ha podido obtener la IP pública del registro de OVH.")

def check_public_ip():
    global public_ip
    try:
        response = requests.get(ifconfig_web, verify = True)
        if response.status_code != 200:
            print('Status:', response.status_code, 'Ha habido un problema con la solicitud de la IP Pública.')
            exit()
        data = response.json()
        public_ip = data['ip']
        ipaddress.ip_address(public_ip)
    except:
        print("Ha sucedido un error al obtener la IP pública actual.")
        exit(1)

def ovh_change_ip():
    result = client.put('/domain/zone/' + OVHDomain + '/record/' + DomainID, target=public_ip)
    result = client.post('/domain/zone/' + OVHDomain + '/refresh')

def dynu_ip():
    params = (
        ('myip', 'public_ip'),
        ('username', DynuUsername),
        ('password', DynuPassword),
    )
    response = requests.get('http://api.dynu.com/nic/update', params=params)

while 1:
    try:
        check_ovh_ip()
        check_public_ip()
        if DomainIP != public_ip:
            try:
                ovh_change_ip()
                print('La IP pública en OVH ha sido modificada de ' + DomainIP + ' a ' + public_ip)
                telegram_alert_bot.sendMessage(telegram_alert_id, "🌐 <b>Cambio de IP</b> \n La nueva IP es " + public_ip, parse_mode='HTML')
            except:
                print('Ha habido un fallo al modificar el registro DNS en OVH.')
                telegram_alert_bot.sendMessage(telegram_alert_id, "🔥 <b>ERROR (OVH)</b> \n Ha sucedido un error al modificar un registro de la zona DNS ", parse_mode='HTML')
            try:
                dynu_ip()
                print('La IP pública en DYNU ha sido modificada de ' + DomainIP + ' a ' + public_ip)
            except:
                print('Ha habido un fallo al modificar el registro DNS en DYNU.')
                telegram_alert_bot.sendMessage(telegram_alert_id, "🔥 <b>ERROR (DYNU)</b> \n Ha sucedido un error al modificar la IP pública del dominio serverfjg.dynu.net", parse_mode='HTML')
        count = 0
    except:
        if 'count' in locals():
            if count >= 3:
                print("Ha habido un error obteniendo la IP pública.")
                telegram_alert_bot.sendMessage(telegram_alert_id, "🔥 <b>ERROR (OVH)</b> \n Ha habido un error obteniendo la IP pública.", parse_mode='HTML')
            count = count+1
        else:
            count = 1
    time.sleep(1800)
