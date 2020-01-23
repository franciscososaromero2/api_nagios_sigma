import os, ConfigParser

def getProperties(path):
    if os.path.exists(path):
        cfgProps = ConfigParser.ConfigParser()
        cfgProps.read(path)
        return cfgProps
    # endif
# enddef

def getProperty(path, lvl, prop):
    cfgProps = getProperties(path)
    return cfgProps.get(lvl, prop)
# enddef

def asBoolean(value):
    return value.lower() in ('s', 'si', 'yes', 'y', 'true', 't', '0')
# enddef


def crearfichero(path):
    try:
        tempFile = open(str(path), "w")
        tempFile.close()
    except:
        return -1
    return 'Fichero testigo creado en: ['+ path + ']'

#enddef
