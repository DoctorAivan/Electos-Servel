import mariadb
import json

def read_servel_candidates(file):

    with open(file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        col = line.strip().split(";")

        candidato = {
            'id' : col[0],
            'zona' : zona(int(col[2])),
            'orden' : col[3],
            'glosa' : col[4],
            'partido' : col[5],
            'pacto' : col[6],
            'independiente' : independiente(col[8]),
            'nombre' : nombre(col[10]),
            'apellido' : col[11],
            'genero' : col[12]
        }

        insert = f"INSERT INTO candidato ( candidato_id , candidato_orden , candidato_tipo , candidato_zona , pacto_id , partido_id , candidato_nombre , candidato_nombres , candidato_apellidos , candidato_genero , candidato_independiente ) VALUES ({candidato['id']} , {candidato['orden']} , 'P' , {candidato['zona']} , {candidato['pacto']} , {candidato['partido']} , '{candidato['glosa']}' , '{candidato['nombre']}' , '{candidato['apellido']}' , '{candidato['genero']}' , {candidato['independiente']} );"

        print( insert )

def read_servel_partidos(file):

    with open(file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        col = line.strip().split(";")

        partido = {
            'id' : col[0],
            'nombre' : col[1],
            'codigo' : col[2]
        }

        insert = f"INSERT INTO partido ( partido_id , partido_nombre , partido_codigo ) VALUES ({partido['id']} , '{partido['nombre']}' , '{partido['codigo']}');"

        print( insert )

def zona(region):

    if region == 5001:
        return 3015
    elif region == 5002:
        return 3001
    elif region == 5003:
        return 3002
    elif region == 5004:
        return 3003
    elif region == 5005:
        return 3004
    elif region == 5006:
        return 3005
    elif region == 5006:
        return 3005
    elif region == 5007:
        return 3013
    elif region == 5008:
        return 3006
    elif region == 5009:
        return 3007
    elif region == 5016:
        return 3016
    elif region == 5010:
        return 3008
    elif region == 5011:
        return 3009
    elif region == 5012:
        return 3014
    elif region == 5013:
        return 3010
    elif region == 5014:
        return 3011
    elif region == 5015:
        return 3012
    else:
        return 3017

def nombre(valor):
    nombres = valor.split(" ")
    return nombres[0]

def independiente(valor):
    if valor == 'S':
        return True
    else:
        return False

def numero(valor):
    numero = format(valor, ',').replace(',', '.')
    return numero

class Servel():

    # Intancear la Conexión
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user="root",
                password="leon",
                host="127.0.0.1",
                port=3306,
                database="Servel"
            )
        except mariadb.Error as e:
            print(f"Error al conectarse a la base de datos: {e}")
            return None

    # Obtener Votos en las Regiones
    def regiones(self):

        cursor = self.conn.cursor()

        cursor.execute(f"""

            SELECT
                zonas.glosa_zona,
                zonas.cod_zona,
                votaciones.ambito,
                votaciones.votos

            FROM
                zonas,
                votaciones

            WHERE
                zonas.tipo_zona = 'S' AND
                votaciones.ambito in (5, 6, 7) AND
                votaciones.tipo_zona = 'S' AND
                votaciones.cod_zona = zonas.cod_zona

            ORDER BY
                zonas.orden_zona ASC,
                votaciones.ambito ASC

        """)

        column_names = [description[0] for description in cursor.description]
        resultados = cursor.fetchall()

        votos = []

        for resultado in resultados:
            r = {column_names[k]: item for k, item in enumerate(resultado)}

            votos.append(r)

        return votos

    # Obtener el listado de Candidatos
    def candidatos(self):

        cursor = self.conn.cursor()

        cursor.execute(f"""
            SELECT
                candidatos.*,
                votaciones.votos,
                votaciones.porcentaje_votos,
                votaciones.ganador
            
            FROM
                candidatos,
                votaciones

            WHERE
                votaciones.ambito = 4 AND
                votaciones.tipo_zona = 'S' AND
                votaciones.cod_ambito = candidatos.cod_cand AND
                votaciones.cod_zona = candidatos.cod_zona

            ORDER BY can_orden ASC
        """)

        column_names = [description[0] for description in cursor.description]
        resultados = cursor.fetchall()

        candidatos = []

        for resultado in resultados:
            r = {column_names[k]: item for k, item in enumerate(resultado)}

            candidatos.append(r)

        return candidatos

# Iniciar
if __name__ == '__main__':

    # Instanciar Servel
    query = Servel()
    candidatos = query.candidatos()

    # Objeto con el listado de candidatos
    listado_candidatos = {}

    # Iterar en candidatos
    for candidato in candidatos:

        # Crear Objecto candidato
        candidato_data = {
            "id" : candidato['cod_cand'],
            "orden" : candidato['can_orden'],
            "nombre" : candidato['glosa_nombre'].title() + ' ' + candidato['glosa_apellido'].title(),
            "pacto" : candidato['cod_pacto'],
            "partido" : candidato['cod_part'],
            "genero" : candidato['cod_genero'],
            "votos" : numero(candidato['votos']),
            "porcentaje" : candidato['porcentaje_votos'],
            "ganador" : candidato['ganador']
        }

        # Asignar una Zoxa
        candidato_zona = zona(candidato['cod_zona'])

        # Validar si existe la Zona
        if not listado_candidatos.get(candidato_zona, None):
            listado_candidatos[candidato_zona] = {}
            listado_candidatos[candidato_zona]['candidatos'] = []
            listado_candidatos[candidato_zona]['totales'] = {
                'validos' : 0,
                'blancos' : 0,
                'nulos' : 0
            }

        # Agregar el candidato a la zona
        listado_candidatos[candidato_zona]['candidatos'].append(candidato_data)

    #   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -

    # Instanciar Servel
    query = Servel()
    votos_regiones = query.regiones()

    # Iterar en candidatos
    for voto_region in votos_regiones:

        # Asignar una Zona
        region_zona = zona(voto_region['cod_zona'])

        if  voto_region['ambito'] == 5:
            listado_candidatos[region_zona]['totales']['nulos'] = numero(voto_region['votos'])

        if  voto_region['ambito'] == 6:
            listado_candidatos[region_zona]['totales']['blancos'] = numero(voto_region['votos'])

        if  voto_region['ambito'] == 7:
            listado_candidatos[region_zona]['totales']['validos'] = numero(voto_region['votos'])

    #   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -

    # Crear Json Dump 
    json_dump = json.dumps(listado_candidatos, indent=4, sort_keys=True)

    # Crear Archivo JSON
    file = open("candidatos.json", "w")
    file.write(json_dump)
    file.close()

    print("Json Creado")
