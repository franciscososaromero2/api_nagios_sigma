#!/usr/bin/python
import utilidades
import web, logging, sys, ConfigParser
import json
import shutil
import os 

#import logging.handlers

filePath = '/MONITORIZACION/uti/api/config.properties'

urls = (
    '/create(.*)', 'encoder',
    '/encode(.*)', 'encoder',
    '/delete(.*)', 'delete',
    '/host(.*)', 'host',
    '/testigo(.*)', 'testigo'

)

class testigo:
    def GET(self, path):
        print "Creando fichero restart nagios."
        # cfgProps = utilidades.getProperties(filePath)
        path = cfgProps.get("nagios", "testigoRestartNagios")
        print path
        return utilidades.crearfichero(path)


class host:
    def POST(self, name):
        try:
            logging.debug('Entrando en clase host-post')
            web.input()
            cfgProps = utilidades.getProperties(filePath)
            # y = web.data()

            # print web.ctx
            path = cfgProps.get("nagios", "pathNagiosCfg", raw=True)
            nombre = web.ctx.get('_fieldstorage').list[0].filename
            tipo = web.input().tipo
            contenido=web.input().file


            ruta = str(path + "/" + tipo + "/" + nombre).strip()
            # print ruta
            f = open(ruta, "w")
            f.write(contenido)
            f.close()
            logging.debug("file: " + str(ruta))
            #logger.debug("file: " + str(ruta))
            return "OK"
        except:
            e = sys.exc_info()
           # print e
            return (e)

class encoder:
    def POST(self, name):
        try:
            cfgProps = utilidades.getProperties(filePath)
            logging.debug('Entrando en clase encoder-post ')
            logging.debug("data: " + web.data())
            data=json.loads(web.data())
            query = cfgProps.get("templates", "queryTemplate", raw=True)
            target = cfgProps.get("templates", "targetfile", raw=True)

            verbo = 'update'
            dir = 'Semaas'

            if data.has_key('description') and data.has_key('documentation') and data.has_key('recoveryAction') and data.has_key('contactEmail') and data.has_key('contactName') and data.has_key('contactPhone'):
                verbo='create'


            for element in data:
                query = query.replace("%"+str(element)+"%",str(data[str(element)]).replace("/","_"))
                target = target.replace("%" + str(element) + "%", str(data[str(element)]).replace("/","_"))
                #if 'Iaas' in  data['namespace']:
                #    dir = 'Iaas'

            # print "target:" , target, verbo
            target = target.replace("%verbo%", verbo).replace(' ','_')
            target = target[:target.rfind('/')]+'/'+dir+target[target.rfind('/'):]
            #print target,str(json.dumps(data))
            logging.debug(str(target) + " - " + str(json.dumps(data)))

            f = open(target, "w")
            f.write(str(json.dumps(data)))
            f.write("\n")
            f.close()
            logging.debug("file: %s {%s}", str(target),data)
            return "OK"
        except:
            logging.error(web.data())
            e = sys.exc_info()
            #print e
            return (e)

class delete:
    def POST(self, name):
        try:
            cfgProps = utilidades.getProperties(filePath)
            logging.debug('Entrando en clase delete-post ')
            logging.debug("data: " + web.data())
            data = json.loads(web.data())
            query = cfgProps.get("templates", "queryTemplate", raw=True)
            target = cfgProps.get("templates", "targetfile", raw=True)

            verbo = 'delete'
            dir = 'Semaas'


            for element in data:
                query = query.replace("%" + str(element) + "%", str(data[str(element)]).replace("/","_"))
                target = target.replace("%" + str(element) + "%", str(data[str(element)]).replace("/","_"))
      #          if 'Iaas' in data['namespace']:
      #              dir = 'Iaas'

            # print "target:" , target, verbo
            target = target.replace("%verbo%", verbo).replace(' ', '_')
            target = target[:target.rfind('/')] + '/' + dir + target[target.rfind('/'):]
            # print target,str(json.dumps(data))
            logging.debug(str(target) + " - " + str(json.dumps(data)))

            f = open(target, "w")
            f.write(str(json.dumps(data)))
            f.write("\n")
            f.close()
            logging.debug("file: %s {%s}", str(target), data)
            return "OK"
        except:
            logging.error(web.data())
            e = sys.exc_info()
            #print e
            return (e)




if __name__ == "__main__":
    cfgProps = utilidades.getProperties(filePath)
    logLvl = cfgProps.get("logging", "level",raw=True)
    logFile = cfgProps.get("logging", "file")
    os.chmod("/MONITORIZACION/uti/api/logs/traces.log", 0644)
    logFormat = cfgProps.get("logging", "formatted", raw=True)
    logDateFormat = cfgProps.get("logging", "dateformatted", raw=True)
    # despues de leer algunos datos hace la copia baclup. (Para asegurarse que no se treemplace el backup si el fichero esta vacio)
    shutil.copy(filePath, filePath + "_bkp")
    logging.basicConfig(filename=logFile, level=logging.DEBUG, format=logFormat, datefmt=logDateFormat)
    #logging.basicConfig(filename="a.log", level=logging.DEBUG)
    #logger = logging.getLogger('apiNagiosIaasOper')
    #ch = logging.StreamHandler(sys.stdout)
    #ch.setLevel(logLvl)
    #ch.setFormatter(logging.Formatter(logFormat))
    #logger.addHandler(ch)
    #logger.info("Iniciando server encoder de mensajes Iass-Operaciones.")
    logging.debug("Iniciando server encoder de mensajes Iass-Operaciones.")

    web.config.debug = True
    app = web.application(urls, globals())
    app.run()

