#Import the modules
import requests
import json
import time
import urllib.parse
import xml.dom.minidom
import subprocess
from Config import *
from Conexion import *
from classes.Alumno import *
from classes.Centro import *
from classes.Ciclo import *
from classes.Modulo import *

def main():
    # 
    alumnosFicheroJson = []
    alumnosMoodle = []
        
    # Creo la conexión para la 1era llamada
    miConexion = Conexion(url1, path1+"2020", usuario1, password1, method1)
    # Hago la 1era llamada
    print( 'Making the call to the 1st web service:')
    resp_data = miConexion.getJson()

    y = json.loads(resp_data);
    if y is not None:
        codigo=y["codigo"]
        mensaje=y["mensaje"]
        idSolicitud=y["idSolicitud"]
        print("Código: " , codigo, ", Mensaje: ", mensaje, "idSolicitud: ", idSolicitud)

        if codigo == 0: # éxito en la 1era llamada
            # 
            print( 'Waiting 10 seconds before the first call to the 2nd web service...')
            for x in range(1, 11):
                time.sleep( 10 )
                print( 'Iteration number ' + str(x))
                miConexion = Conexion(url2, path2 + str(idSolicitud), usuario2, password2, method2)
                resp_data = miConexion.getJson()
                y = json.loads(resp_data)
                if y is not None:
                    codigo=y["codigo"]
                    mensaje=y["mensaje"]
                    print("codigo: " + str(codigo) + ", mensaje: " + str(mensaje))
                    if codigo == 0: # éxito de la 2nda llamada
                        procesaJsonEstudiantes(y, alumnosFicheroJson)
                        break
                    else: # Error  en la 2ª llamada
                        print("Fichero aún no listo. Código: " + str(codigo) 
                            + ", mensaje: " + str(mensaje))
        else: # Error en la 1era llamada
            print("Error en la llamada al 1er web service")
    
    # Iterating over alumnosFicheroJson for testing
    for alumno in alumnosFicheroJson:
        # print("-", repr(alumno) )
        # los cursos de moodle tienen el formato shortname ${COD_CENTRE}-${siglasCiclo}-${COD_ENSENANZA}
        if not existeAlumnoEnMoodle(alumno):
            crearAlumnoEnMoodle(alumno)
        

        
    # print("Alumnos en fichero json", len(alumnosFicheroJson) )
    #

    #
    # End of main 
    # 

def procesaJsonEstudiantes(y, alumnosFicheroJson):
    """
    Procesa el fichero JSON obteniendo los alumnos y que estudian y los
    añade a alumnosFicheroJson
    """
    estudiantes=y["estudiantes"]
    # print( "type(estudiantes): ", type(estudiantes) ) # str
    estudiantesJson=json.loads(estudiantes)
    # print( "type(estudiantesJson: ",type(estudiantesJson) ) # dict

    fecha=estudiantesJson["fecha"]
    hora=estudiantesJson["hora"]
    alumnos=estudiantesJson["alumnos"]

    # print("fecha: " + str(fecha) + " y hora: " + str(hora) + " de creación del fichero")
    i = 0
    for alumno in alumnos:
        # print("i: ", i)
        # print("type(alumno): ", type(alumno) ) # dict
        idAlumno = alumno["idAlumno"]
        idTipoDocumento = alumno["idTipoDocumento"]
        documento = alumno["documento"]
        nombre = alumno["nombre"]
        apellido1 = alumno["apellido1"]
        apellido2 = alumno["apellido2"]
        email = alumno["email"]
        centros = alumno["centros"]
        # print( "type(centros): ", type(centros) ) # list
        # print( "len(centros): ", len(centros) ) # 
        # creo el objeto
        miAlumno = Alumno(idAlumno, idTipoDocumento, documento, nombre, 
                apellido1, apellido2, email)
        # miAlumno.toText()
        #
        j=0
        for centro in centros:
            # print("  i: " + str(i) + ", j: " + str(j) + ", centro: " + str(centro) )
            # print("type(centro): ", type(centro) ) # dict

            codigoCentro = centro["codigoCentro"]
            centroo = centro["centro"]
            ciclos=centro["ciclos"]
            # print("ciclos: ", ciclos)
            # print("type(ciclos): ", type(ciclos) ) # str

            miCentro = Centro(codigoCentro, centroo)

            k = 0
            for ciclo in ciclos:
                # print("    i: ", i, ", j: ", j, ", k: ", k, ", ciclo: ", ciclo )
                # print("type(ciclo): ", type(ciclo) ) # dict
                
                idFicha = ciclo["idFicha"]
                codigoCiclo = ciclo["codigoCiclo"]
                cicloo = ciclo["ciclo"]
                siglasCiclo = ciclo["siglasCiclo"]
                modulos = ciclo["modulos"]

                miCiclo = Ciclo(idFicha, codigoCiclo, cicloo, siglasCiclo)

                l = 0
                for modulo in modulos:
                    #
                    idMateria = modulo["idMateria"]
                    moduloo = modulo["modulo"]
                    siglasModulo = modulo["siglasModulo"]
                    #
                    miModulo = Modulo(idMateria, moduloo, siglasModulo)
                    #
                    miCiclo.addModulo(miModulo)
                #
                miCentro.addCiclo(miCiclo)
            # Add miCentro to miAlumno
            miAlumno.addCentro(miCentro)
        # Add miAlumno to alumnosFicheroJson
        alumnosFicheroJson.append(miAlumno)
    #
    # End of procesaJsonEstudiantes
    #

def existeAlumnoEnMoodle(alumno):
    """
    Comprueba si el alumno dado existe en moodle
    Devuelve true si existe
    Devuelve false si no existe
    """
    print("existeAlumnoEnMoodle(...)")

    # moosh -n  user-list "username = 'estudiante1'"
    cmd = "moosh -n  user-list \"username = '"+ alumno.getDocumento() +"'\""
    result = subprocess.run( cmd )
    print(result)
    return True
    #
    # End of existeAlumnoEnMoodle
    #

def crearAlumnoEnMoodle(alumno):
    """
    Crea un usuario en moodle con los datos del objeto alumno
    Devuelve el id del alumno creado
    """
    print("crearAlumnoEnMoodle(...)")
    # moosh user-create --password estudiante --email alumnado@education.catedu.es --digest 2 --city Aragón --country ES --firstname "Estudiante10" --lastname "Diez" estudiante10
    return None
    #
    # End of crearAlumnoEnMoodle
    #


###################################################
# Lanzamos!
###################################################
main()