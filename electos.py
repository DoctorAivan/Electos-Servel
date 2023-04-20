import mariadb
import json

# Regiones y Cupos
dic_regiones = {
    5001 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 1',
        'cupos' : 2
    },
    5002 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 2',
        'cupos' : 2
    },
    5003 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 3',
        'cupos' : 3
    },
    5004 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 4',
        'cupos' : 2
    },
    5005 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 5',
        'cupos' : 3
    },
    5006 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 6',
        'cupos' : 5
    },
    5007 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 7',
        'cupos' : 5
    },
    5008 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 8',
        'cupos' : 3
    },
    5009 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 9',
        'cupos' : 5
    },
    5010 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 10',
        'cupos' : 3
    },
    5011 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 11',
        'cupos' : 5
    },
    5012 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 12',
        'cupos' : 3
    },
    5013 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 13',
        'cupos' : 3
    },
    5014 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 14',
        'cupos' : 2
    },
    5015 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 15',
        'cupos' : 2
    },
    5016 : {
        'nombre' : 'CIRCUNSCRIPCIÓN SENATORIAL 16',
        'cupos' : 2
    },
}

# Pactos
dic_pactos = {
    'A' : 'PARTIDO DE LA GENTE',
    'B' : 'TODO POR CHILE',
    'C' : 'PARTIDO REPUBLICANO',
    'D' : 'UNIDAD PARA CHILE',
    'E' : 'CHILE SEGURO'
}

# Librerias de Servel
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

    # Obtener el listado de Candidatos
    def candidatos(self):

        cursor = self.conn.cursor()

        cursor.execute(f"""

            SELECT
                candidatos.*,
                pactos.*,
                votaciones.votos,
                votaciones.porcentaje_votos,
                votaciones.ganador
            
            FROM
                candidatos,
                pactos,
                votaciones

            WHERE
                pactos.cod_pacto = candidatos.cod_pacto AND
                votaciones.ambito = 4 AND
                votaciones.tipo_zona = 'S' AND
                votaciones.cod_ambito = candidatos.cod_cand AND
                votaciones.cod_zona = candidatos.cod_zona

            ORDER BY votaciones.votos DESC

        """)

        column_names = [description[0] for description in cursor.description]
        resultados = cursor.fetchall()

        candidatos = []

        for resultado in resultados:
            r = {column_names[k]: item for k, item in enumerate(resultado)}

            candidatos.append(r)

        return candidatos

# Librerias de Task
class Task():

    # Obtener datos
    def zonas_base(candidatos):

        # Listado de Regiones
        regiones = {}

        # Iterar en candidatos
        for candidato in candidatos:

            # Valores para ordenar
            candidato_zona = candidato['cod_zona']
            candidato_pacto = candidato['letra_pacto']

            # Validar pactos
            if not candidato_pacto == '':

                # Validar si existe la Zona
                if not regiones.get(candidato_zona, None):
                    regiones[candidato_zona] = {}
                    regiones[candidato_zona]['pactos'] = {}

                if not regiones[candidato_zona]['pactos'].get(candidato_pacto, None):
                    regiones[candidato_zona]['pactos'][candidato_pacto] = {
                        'candidatos' : [],
                        'mayorias' : [],
                        'totales' : 0,
                        'pacto' : candidato['glosa_pacto'],
                        'letra' : candidato_pacto
                    }
            
                regiones[candidato_zona]['pactos'][candidato_pacto]['candidatos'].append({
                    'id' : candidato['cod_cand'],
                    'nombre' : candidato['glosa_cand'],
                    'genero' : candidato['cod_genero'],
                    'votos' : candidato['votos'],
                })

                regiones[candidato_zona]['pactos'][candidato_pacto]['totales'] += candidato['votos']

        return regiones

    # Agregar mayorias
    def zonas_mayorias(candidatos):

        # Objeto con el listado de candidatos
        regiones = []

        # Iterar en candidatos
        for candidato in candidatos:

            # Valores para ordenar
            candidato_zona = candidato['cod_zona']
            candidato_pacto = candidato['letra_pacto']        

            # Obtener cupos de la zona
            zona_cupos = dic_regiones[candidato_zona]['cupos']

            # Validar pactos
            if not candidato_pacto == '':

                # Agregar las zonas
                if not any(d['zona'] == candidato_zona for d in regiones):
                    regiones.append({
                        'zona' : candidato_zona,
                        'nombre' : dic_regiones[candidato_zona]['nombre'],
                        'cupos' : zona_cupos,
                        'pactos' : [],
                        'mayorias' : [],
                        'electos' : [],
                    })

                # Obtener Región
                zona = [item for item in regiones if item['zona'] == candidato_zona]

                # Obtener total de Votos
                pacto_votos = datos[candidato_zona]['pactos'][candidato_pacto]['totales']

                # Obtener listado de candidatos
                candidatos_list = datos[candidato_zona]['pactos'][candidato_pacto]['candidatos']

                # Ordenar Candidatos por Votos
                candidatos_list.sort(key=lambda x: x.get('votos'), reverse=True)

                # Agregar los pactos a la región
                if not any(d['id'] == candidato_pacto for d in zona[0]['pactos']):

                    # Crear mayorias de la Zona
                    mayorias = []

                    # Calcular mayorias basado en pucos
                    for calculo in range(zona_cupos):

                        # Calcular mayoria
                        valor = int(pacto_votos / (calculo + 1))

                        # Crear objeto con el calculo
                        mayorias.append({
                            'pacto' : candidato_pacto,
                            'votos' : valor
                        })

                        # Agregar calculo a las mayorias
                        zona[0]['mayorias'].append({
                            'pacto' : candidato_pacto,
                            'nombre' : dic_pactos[candidato_pacto],
                            'votos' : valor
                        })

                    # Agregar los pactos a la zona
                    zona[0]['pactos'].append({
                        'id' : candidato_pacto,
                        'mayorias' : mayorias,
                        'candidatos' : candidatos_list,
                        'totales' : pacto_votos
                    })

                # Ordenar las mayorias de la zona
                zona[0]['mayorias'].sort(key=lambda x: x.get('votos'), reverse=True)

        return regiones

# Iniciar
if __name__ == '__main__':

    # Instanciar Servel 
    query = Servel()
    candidatos = query.candidatos()

    # Obtener estructura Base
    datos = Task.zonas_base(candidatos)

    # Obtener estructura y sus mayorias
    regiones = Task.zonas_mayorias(candidatos)

    #       -       -       -       -       -       -       -       -       -       -

    # Ordenar Zonas por ID
    regiones.sort(key=lambda x: x.get('zona'))

    print(' ')

    for region in regiones:
        print(region['nombre'], ' - CUPOS:', region['cupos'])

        index = 1
        for mayoria in region['mayorias']:

            if index <= region['cupos']:
                print(index, ')' , mayoria['pacto'] ,  mayoria['nombre'] , mayoria['votos'])

                candidatos = [item for item in region['pactos'] if item['id'] == mayoria['pacto']]

                candidato_nombre = candidatos[0]['candidatos'][0]['nombre']
                candidato_votos = candidatos[0]['candidatos'][0]['votos']
                candidato_genero = candidatos[0]['candidatos'][0]['genero']

                print( '    ', candidato_genero, ')', candidato_nombre, candidato_votos )

            index += 1

        print('-        -       -       -       -')

    # Crear Json Dump 
    json_dump = json.dumps(regiones, indent=4, sort_keys=True)

    # Crear Archivo JSON
    file = open("electos.json", "w")
    file.write(json_dump)
    file.close()

    print("Json Creado")
