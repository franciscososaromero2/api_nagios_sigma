#!/bin/bash

#Autor:Francisco Sosa Romero francisco.sosa2@bbva.com
#Descripción: Monitorización de cambios en Nagios.
#Version1.0

MIN=1

valida_cambios()
{

DELETE_SERVICE=`cat $LOGS_API | grep "Servicio Borrado" | tail -1`
CREATE_SERVICE=`cat $LOGS_API | grep "Servicio creado"  | tail -1`

LOG_CHANGES=/MONITORIZACION/uti/nagios_apicreate/logs/apply_changes.log



if [ -f $LOGS_API ]; then
	EVENTS=0

       if [ -n "$CREATE_SERVICE" ]; then
	echo " `date ` Se detecto la creacion de un servicio." >> $LOG_CHANGES
        EVENTS=1
	fi

	if [ -n "$DELETE_SERVICE" ]; then
        echo " `date` Se detecto el borrado de un servicio." >> $LOG_CHANGES
        EVENTS=1
        fi

	if [ $EVENTS = 1 ]; then 
		echo "Evento Detectado:"
		 rm -f $LOGS_API
		exit 1
	else
		echo "No hay eventos detectados"
		 rm -f $LOGS_API
		exit 0
	fi

else
echo "Analizando cambios  en $RUTALOGS"
exit 0

fi
}
 


########################################################################################
######################Definicion del LOG      ###################
########################################################################################




RUTALOGS=/MONITORIZACION/uti/nagios_apicreate/logs/traces.log
LOGS_API="/tmp/logapi_registers8746848w"


if [ -f $RUTALOGS ]; then

	for (( i = $MIN; i >=0; i-- )) ; do
	    INTERVALO=$(date +%H:%M -d "-$i  min")
	    DIA=$(date +%Y-%m-%d)
	    awk '{if (substr($2,1,5)=="'$INTERVALO'" && substr($1,1,10)=="'$DIA'" && $8=="'INFO'") print $0 }' $RUTALOGS  >> $LOGS_API 
	done

else

	echo "Archivo log $RUTALOGS."
	echo "`date` No Hay registros recientes." >> $LOG_CHANGES
	exit 0

fi


if [ -f $LOGS_API ]; then

	valida_cambios

                echo "`date` No se encontraron registros de servicios creados o borrados." >> $LOG_CHANGES
                rm -f $LOGS_API
                exit 0


rm -f $LOGS_API

fi

