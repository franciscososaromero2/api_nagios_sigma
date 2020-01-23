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




#Variables para insercion de eventos en Elastic
directory_alerts = "/MONITORIZACION/uti/alerts/Semaas/"
elastic_server="http://192.x.x.x"
elastic_port="8020"
user_elastic="user"
pass_elastic="passs"
url_elastic=str(elastic_server)+":"+str(elastic_port)+"/alertanagios/encode"
auth_elastic=HTTPBasicAuth(user_elastic, pass_elastic)
#now = datetime.now()
print url_elastic
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
	print data

	####Validar el tipo de evento#################
	if data.has_key('status') and data.has_key('mrTypeName') and data.has_key('timestamp')and data.has_key('alarmDisplayName')and data.has_key('namespace')and data.has_key('mrName'):
                                disciplina = data['namespace']
                                hostgroup = data['mrTypeName']
                                hostname = data['mrName']
                                service = data['alarmDisplayName']
                                service_nagios = str(hostname)+"_"+str(service)
                                service_state = data['status']
                                timestamp = data['timestamp']
                                reason = data['reason']
				now = time.strftime("%d-%m-%Y %H:%M:%S")

                                logging.info("Servicio actualizado OK."+str(service_nagios))
				data_elastic={"disciplina":str(disciplina), "hostgroup":str(hostgroup), "hostname":str(hostname), "service":str(service),"service_state":str(service_state), "@timestamp": str(now), "reason":str(reason)}			


			        ####Insertar Data en Elastic del Evento#######
			        elastic_insert_event=requests.post(url_elastic, auth=auth_elastic, data=json.dumps(data_elastic) , headers={'Content-Type' : 'application/json'})
			        print elastic_insert_event.text
			        if elastic_insert_event.status_code == 200 or elastic_insert_event.status_code == 201:
					logging.info("Insercion en Elastic Search del evento OK, Codigo HTTP:" +str(elastic_insert_event.status_code)+" Info MSG:"+str(data_elastic))

			        else:
        				logging.error("Insercion fallida en Elastic search:"+str(service_nagios)+" Codigo de error:"+str(elastic_insert_event.status_code)+ " Detalle:"+str(elastic_insert_event.text))
	


#Definicion del demonio para monitorizar cambios en los archivos.
if __name__ == '__main__':
    logging.basicConfig(filename = "/MONITORIZACION/uti/nagios_apicreate/logs/elastic_insert.log",level=logging.DEBUG,format='%(asctime)s - %(funcName)s - %(lineno)s - %(levelname)s - %(pathname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
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
