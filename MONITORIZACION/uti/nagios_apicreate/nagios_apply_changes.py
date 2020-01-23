#!/usr/bin/python 
#Importar modulos
import time  
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import requests
import json
import logging
import os


#Definicion de datos para conexion a Nagios
token_api="xxxxxxx"
usernagios="nagio"
nagios_server="150.x.x.x"
url_nagios_config="http://"+nagios_server+"/nagiosxi/api/v1/config/"
url_nagios_consulting="http://"+nagios_server+"/nagiosxi/api/v1/objects/"
api_nagios_config_objects=url_nagios_config+"service?apikey="+token_api+"&pretty=1"
api_nagios_consulting_service=url_nagios_consulting+"service?apikey="+token_api+"&pretty=1"
nagios_service_template="xiwizard_passive_service"
api_nagios_system_status="http://"+nagios_server+"/nagiosxi/api/v1/system/status?apikey="+token_api+"&pretty=1"

def apply_changes_api_nagios(): 
    apply_changes="http://"+nagios_server+"/nagiosxi/api/v1/system/applyconfig?apikey="+token_api
    nagios_apply_changes=requests.post(apply_changes)
    if nagios_apply_changes.status_code == 200: 
	print "Cambios aplicados satisfactoriamente."

def nagios_system_status():
    #Obtener el estado de Nagios
    nagios_system_status=requests.get(api_nagios_system_status)
    #Validar que Nagios este disponible para aplicar cambios.
    if nagios_system_status.status_code == 200:
	    parsed_json_system_status = json.loads(nagios_system_status.text)
            validate_system = parsed_json_system_status['daemon_mode']
            if validate_system == "1":
                 print ( "Servicio Nagios Activo. Disponible para aplicar Cambios.")
                 return True

            elif validate_system == "null":
                 print ( "Servicio Nagios Aplicando Cambios. Espere.....")
                 return False



#Ejecutar Script para validar si hay cambios. 
result = os.system("/MONITORIZACION/uti/nagios_apicreate/check_watch_changes.sh")
if result == 0: 
	print( "No hay cambios detectados")	
	exit
elif result > 0:  
	print ( "Se detectan nuevos eventos:")
	if nagios_system_status() == True:
		print( "Servicio Nagios disponible para aplicar cambios.")
		apply_changes_api_nagios()
		
	else: 
		print( "Servicio Nagios esta aplicando cambios.")
		exit 


