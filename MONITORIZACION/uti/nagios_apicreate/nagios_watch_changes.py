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
from requests.auth import HTTPBasicAuth



#Definicion de datos para conexion a Nagios proyecto IAAS
token_api="EHvKVZI"
usernagios="nagios"
nagios_server="150.x.x.x"
url_nagios_config="http://"+nagios_server+"/nagiosxi/api/v1/config/"
url_nagios_consulting="http://"+nagios_server+"/nagiosxi/api/v1/objects/"
api_nagios_config_objects=url_nagios_config+"service?apikey="+token_api+"&pretty=1"
api_nagios_consulting_service=url_nagios_consulting+"service?apikey="+token_api+"&pretty=1"
api_nagios_consulting_host=url_nagios_consulting+"host?apikey="+token_api+"&pretty=1"
nagios_service_template="xiwizard_passive_service"
directory_alerts = "/MONITORIZACION/uti/alerts/Semaas/"
api_nagios_system_status="http://"+nagios_server+"/nagiosxi/api/v1/system/status?apikey="+token_api+"&pretty=1"

#Variables de insercion de alerta pasiva 
commandfile="/usr/local/nagios/var/rw/nagios.cmd"
now = int(time.time())



#Events are: modified, created, deleted, moved
#Definicion de la clase

class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.json"]

    def process(self, event):
        """
        event.event_type 
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            /MONITORIZACION/uti/alerts/Semaas
        """
        # the file will be processed there
        #print event.src_path, event.event_type  # print now only for degug

    
 
    def on_modified(self, event):
 	logging.debug( "Evento detectado en path: %s ", event.src_path)
        json_data = open(event.src_path).read()
        data = json.loads(json_data.replace('\n','').replace("/","_"))
        logging.debug("data: %s ", data)
	#print data

	def nagios_system_status():
	        #Obtener el estado de Nagios
        	nagios_system_status=requests.get(api_nagios_system_status)
        	#Validar que Nagios este disponible para aplicar cambios.
        	if service_status.status_code == 200:
                	parsed_json_system_status = json.loads(nagios_system_status.text)
                	validate_system = parsed_json_system_status['daemon_mode']
        		if validate_system == "1":
                		logging.info( "Servicio Nagios Activo. Disponible para aplicar Cambios.")
                		return True

        		elif validate_system == "null":
				logging.info( "Servicio Nagios Aplicando Cambios. Espere.....")
				time.sleep(5)
                		return False

###########################################################################################################################
############################Creacion de Sensores###########################################################################
###########################################################################################################################
        #Validar que exista el sensor creado  en Nagios. Si el equipo existe no hacer nada, pasar al update.
	if "create" in event.src_path:
		intentos = 0
		while intentos < 5:	
			#Validacion de Datos extraidos del archivo Json.
			if data.has_key('description') and data.has_key('documentation') and data.has_key('recoveryAction')and data.has_key('contactEmail')and data.has_key('contactName')and data.has_key('contactPhone'): 
				disciplina = data['namespace']
                		hostgroup = data['mrTypeName']
                		hostname = data['mrName']
                		service = data['alarmDisplayName']
				service_nagios = str(hostname)+"_"+str(service).replace(" ", "_")
				service_status=requests.get(api_nagios_consulting_service+"&host_name="+str(disciplina)+"&service_description="+str(service_nagios))	
				host_status=requests.get(api_nagios_consulting_host+"&host_name="+str(disciplina))
				#Validar que exista el sensor creado  en Nagios. Si el equipo existe no hacer nada, pasar al update. 
				parsed_json_host = json.loads(host_status.text)
				validate_host = parsed_json_host["hostlist"]["recordcount"]
				if nagios_system_status() == True and service_status.status_code == 200: 
					parsed_json_service = json.loads(service_status.text)
					validate_service = parsed_json_service["servicelist"]["recordcount"]
			 		if validate_service == "1": 
						logging.info( "No se puede crear el sensor ya existe en Nagios: "+str(service_nagios))	
						intentos = 5 	
					#Si el sensor del servicio no existe en Nagios. Proceder a crearlo y validar que este creado.
					elif validate_host == "1":  
						data_service_create={'host_name' : str(disciplina), 'service_description' : service_nagios ,'use' : nagios_service_template , 'applyconfig' : '0', 'force' : '1'}
						service_create=requests.post(api_nagios_config_objects, data=data_service_create)
						if service_create.status_code == 200:
							logging.info( "Servicio creado:"+str(service_nagios)+" OK.")
							logging.info( "Datos de la creacion del servicio: "+ str(data_service_create))
							time.sleep(1)
							intentos = 5
							
						else:
							logging.info( "Servicio no creado:", str(service_nagios), "error: ", str(service_create.status_code))	
					else: 
						logging.info( "No se ha generado el namespace: "+str(disciplina))	
						intentos = 5
				elif nagios_system_status() == False:
					intentos = intentos + 1
					time.sleep(60)
					logging.info( "No se pudo crear Sensor en Nagios, numero de Intentos:"+str(intentos))
					
					
#################################################################################################################################################
#################################################Creacion de estados para los servicio###########################################################
#################################################################################################################################################
	if "update" in event.src_path:
		intentos_estado = 0
		while intentos_estado < 10:
               		#Validacion de Datos extraidos del archivo Json para actualizar la alerta..
               		if data.has_key('status') and data.has_key('mrTypeName') and data.has_key('timestamp')and data.has_key('alarmDisplayName')and data.has_key('namespace')and data.has_key('mrName'):
                       		disciplina = data['namespace']
                       		hostgroup = data['mrTypeName']
                       		hostname = data['mrName']
                       		service = data['alarmDisplayName']
                       		service_nagios = str(hostname)+"_"+str(service).replace(" ", "_")
				service_state = data['status']
				timestamp = data['timestamp']
				reason = data['reason']
				logging.info("Servicio actualizado OK."+str(service_nagios))
				service_status=requests.get(api_nagios_consulting_service+"&host_name="+str(disciplina)+"&service_description="+str(service_nagios))
                       		if service_status.status_code == 200:
                                	parsed_json_service = json.loads(service_status.text)
                              		validate_service = parsed_json_service["servicelist"]["recordcount"]
                                	if validate_service == "1" and nagios_system_status() == True:
						#intentos_estado=5
                                        	logging.info( "Servicio Existe en Nagios, enviando estado de la notificacion:" + str(validate_service))
						#Obtener datos del servicio desde la plantilla Json de la definicion del servicio.
                                        	file_service_json = str(directory_alerts)+"create."+disciplina+"."+hostname+"."+str(service).replace(" ","_")+".json"
                                      		json_data_service = open(file_service_json).read()
                                     		data_service = json.loads(json_data_service)     
                                       		documentation = data_service['documentation']
						recoveryAction = data_service['recoveryAction']
						contactEmail = data_service['contactEmail']
						contactName = data_service['contactName']
						contactPhone = data_service['contactPhone']
						#logging.info ("Abriendo archivo Json "+ file_service_json)
                	                        logging.info ("Datos del servicio: "+ str(data_service))
										


						##Definicion de codigo de la alerta. 
						if service_state == "OK": 
							service_state_num = 0
							cadenaToNagioSrv = "PROCESS_SERVICE_CHECK_RESULT;"+disciplina+";"+service_nagios+";"+str(service_state_num)+";"+reason
						elif service_state == "WARNING":
							service_state_num = 1
							cadenaToNagioSrv = "PROCESS_SERVICE_CHECK_RESULT;"+disciplina+";"+service_nagios+";"+str(service_state_num)+";"+reason+" Accion de recuperacion:"+recoveryAction+" Contacto:"+contactName
					 	elif service_state == "CRITICAL":
							service_state_num = 2
							cadenaToNagioSrv = "PROCESS_SERVICE_CHECK_RESULT;"+disciplina+";"+service_nagios+";"+str(service_state_num)+";"+reason+" Accion de recuperacion:"+recoveryAction+" Contacto:"+contactName
				
					
						#################Insercion del estado de la alerta.#######################
					
						cmd=cadenaToNagioSrv.replace('\n', '')
						os.system("echo "  + "["+ str(now)+"]" + " " + "'" + str(cmd) + "'" +"  > " +str(commandfile))
						logging.info ("Datos de la insercion en nagios:" +str(cadenaToNagioSrv))
						intentos_estado = 10
	
	
					else: 	
						intentos_estado = intentos_estado + 1
						logging.info ("Servicio no existe en Nagios: "+service_nagios+" No insertara informacion. Numero de Intentos:"+str(intentos_estado))
						time.sleep(60)
						#exit


###############################################################################################################################################
############################################Borrado de Sensores################################################################################
###############################################################################################################################################

	if "delete" in event.src_path:
		intentos_delete = 0
		while intentos_delete < 5:
                	#Validacion de Datos extraidos del archivo Json.
                	if data.has_key('description') and data.has_key('documentation') and data.has_key('recoveryAction')and data.has_key('contactEmail')and data.has_key('contactName')and data.has_key('contactPhone'):
                        	disciplina = data['namespace']
                        	hostgroup = data['mrTypeName']
                        	hostname = data['mrName']
                        	service = data['alarmDisplayName']
                        	service_nagios = str(hostname)+"_"+str(service).replace(" ", "_")
      		                service_status=requests.get(api_nagios_consulting_service+"&host_name="+str(disciplina)+"&service_description="+str(service_nagios))
                       		#Validar que exista el sensor creado  en Nagios. Si el equipo borrarlo..
                        	if nagios_system_status() == True and service_status.status_code == 200:
                                	parsed_json_service = json.loads(service_status.text)
                                	validate_service = parsed_json_service["servicelist"]["recordcount"]
                             		if validate_service == "1":
                                		logging.info( "Se procede  a borrar el servicio: "+str(service_nagios))
						#data_service_delete={'host_name':disciplina, 'service_description': service_nagios,'applyconfig':'0'}
                                        	service_delete=requests.delete(api_nagios_config_objects+"&host_name="+str(disciplina)+"&service_description="+str(service_nagios)+"&applyconfig=0")
						#logging.info ("Informacion del Borrado: "+str(service_delete))
						time.sleep(2)
						if service_delete.status_code == 200: 
							logging.info ("Servicio Borrado en Nagios:" +service_nagios)
					 		intentos_delete = 5	
                               		#Si el sensor del servicio no existe en Nagios. Indicar  que no existe.
                               		elif validate_service == "0":
						logging.info ("Servicio no existe en Nagios proceder a borrar.")	
						intentos_delete = 5
					else: 
						logging.info ("No se puede obtener informacion del servicio:"+service_nagios)
						intentosi_delete = intentos_intentos_delete + 1
						time.sleep(60)
				elif nagios_system_status() == False: 
					intentos_delete = intentos_delete + 1
                                        logging.info ("Servicio Nagios se encuentra aplicando cambios, reintentando:"+str(intentos))
					time.sleep(60)



#Definicion del demonio para monitorizar cambios en los archivos.
if __name__ == '__main__':
    logging.basicConfig(filename = "/MONITORIZACION/uti/nagios_apicreate/logs/traces.log",level=logging.DEBUG,format='%(asctime)s - %(funcName)s - %(lineno)s - %(levelname)s - %(pathname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    os.chmod("/MONITORIZACION/uti/nagios_apicreate/logs/traces.log", 0644)
    observer = Observer()
    observer.schedule(MyHandler(), path=directory_alerts if directory_alerts else '.')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
