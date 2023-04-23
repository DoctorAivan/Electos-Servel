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

# Pactos Totales
dic_pactos_totales = []
dic_pactos_electos = [
    {
        'id' : 'A',
        'electos' : 0,
        'votos' : 0
    },
    {
        'id' : 'B',
        'electos' : 0,
        'votos' : 0
    },
    {
        'id' : 'C',
        'electos' : 0,
        'votos' : 0
    },
    {
        'id' : 'D',
        'electos' : 0,
        'votos' : 0
    },
    {
        'id' : 'E',
        'electos' : 0,
        'votos' : 0
    }
]
dic_zonas_electos = []
dic_zonas_electos_finales = []

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
                votaciones.ambito = 7 AND
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
                pactos.*,
                partidos.*,
                votaciones.votos,
                votaciones.porcentaje_votos,
                votaciones.ganador
            
            FROM
                candidatos,
                pactos,
                partidos,
                votaciones

            WHERE
                pactos.cod_pacto = candidatos.cod_pacto AND
                partidos.cod_part = candidatos.cod_part AND
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
    def zonas_base(candidatos, region_votos):

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
                    'pacto' : candidato['letra_pacto'],
                    'partido' : candidato['sigla_part'],
                    'votos' : candidato['votos'],
                })

                regiones[candidato_zona]['pactos'][candidato_pacto]['totales'] += candidato['votos']

        for region in dic_regiones:

            votos_validos = [item for item in region_votos if item["cod_zona"] == region]

            dic_zonas_electos.append({
                'id' : region,
                'nombre' : dic_regiones[region]['nombre'],
                'cupos' : dic_regiones[region]['cupos'],
                'validos' : votos_validos[0]['votos'],
                'pactos' : []
            })

            dic_zonas_electos_finales.append({
                'id' : region,
                'nombre' : dic_regiones[region]['nombre'],
                'cupos' : dic_regiones[region]['cupos'],
                'electos' : []
            })

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

        # Asignar totales nacionales
        for region in regiones:

            # Iterar en los pactos
            for pacto in region['pactos']:

                # Obtener la letra del pacto
                pacto_id = pacto['id']

                # Validar si el nodo existe
                if not any(d['pacto'] == pacto_id for d in dic_pactos_totales):
                    dic_pactos_totales.append({
                        'pacto' : pacto_id,
                        'votos' : 0
                    })

                # Obtener el pacto
                pacto_total = [item for item in dic_pactos_electos if item['id'] == pacto_id]
                pacto_total[0]['votos'] += pacto['totales']

        return regiones

    # Buscar un nodo en un array
    def find(array = [] , key = '' , value = ''):
        respuesta = [item for item in array if item[key] == value]
        return respuesta

    def validar_electos(zona = 0, pacto = '', candidatos=[]):

        # Buscar el Pacto
        zona = Task.find(array = dic_zonas_electos_finales,
                        key = 'id',
                        value = zona)
        
        candidatos_hombres = Task.find(array = candidatos,
                                key = 'genero',
                                value = 'M')
        
        candidatos_mujeres = Task.find(array = candidatos,
                                key = 'genero',
                                value = 'F')

        #       -       -       -       -       -       -       -       -

        # Validar Zonas de 2 Cupos
        if( zona[0]['cupos'] == 2 ):

            # Se ingresa la primera mayoria
            if( len(zona[0]['electos']) == 0):
                zona[0]['electos'].append( candidatos[0] )

            # Validamos el Genero del segundo candidato para rectificar paridad
            else:
                genero_anterior = zona[0]['electos']
                
                # Validar la paridad de genero en la zona
                if( genero_anterior[0]['genero'] == 'F' ):
                    zona[0]['electos'].append( candidatos_hombres[0] )
                else:
                    zona[0]['electos'].append( candidatos_mujeres[0] )

        #       -       -       -       -       -       -       -       -

        # Validar Zonas de 3 Cupos
        if( zona[0]['cupos'] == 3 ):

            # Se ingresa la primera mayoria
            if( len(zona[0]['electos']) == 0):
                zona[0]['electos'].append( candidatos[0] )

            # Se ingresa la segunda mayoria
            elif( len(zona[0]['electos']) == 1):
                zona[0]['electos'].append( candidatos[0] )

            # Validamos el Genero del tercer candidato para rectificar paridad
            elif( len(zona[0]['electos']) == 2):

                total_hombres = 0
                total_mujeres = 0

                candidatos_electos = zona[0]['electos']

                for candidato in candidatos_electos:

                    if( candidato['genero'] == 'M' ):
                        total_hombres += 1
                    else:
                        total_mujeres += 1

                if( total_hombres == 2 ):
                    zona[0]['electos'].append( candidatos_mujeres[0] )
                elif( total_mujeres == 2 ):
                    zona[0]['electos'].append( candidatos_hombres[0] )
                else:
                    zona[0]['electos'].append( candidatos[0] )

                print('Hombres' , total_hombres , '-', 'Mujeres' , total_mujeres )

        #       -       -       -       -       -       -       -       -

        if( zona[0]['cupos'] == 5 ):
            pass


# Iniciar
if __name__ == '__main__':

    # Instanciar Servel 
    query = Servel()
    candidatos = query.candidatos()

    query_regiones = Servel()
    region_votos = query_regiones.regiones()

    # Obtener estructura Base
    datos = Task.zonas_base(candidatos , region_votos)

    # Obtener estructura y sus mayorias
    regiones = Task.zonas_mayorias(candidatos)

    #       -       -       -       -       -       -       -       -       -       -

    # Ordenar Zonas por ID
    regiones.sort(key=lambda x: x.get('zona'))

    #print(' ')

    for region in regiones:

        index = 1
        for mayoria in region['mayorias']:

            if index <= region['cupos']:

                # Buscar la Region
                region_electos = Task.find(array = dic_zonas_electos,
                                        key = 'id',
                                        value = region['zona'])

                region_electos[0]['pactos'].append({
                    'id' : mayoria['pacto'],
                    'votos' : mayoria['votos'],
                    'electos' : []
                })

            index += 1

    dic_pactos_totales.sort(key=lambda x: x.get('votos'), reverse=False)

    #       -       -       -       -       -       -       -       -       -       -

    print('-        -       -       -       -       -       -       -       -')

    dic_zonas_electos.sort(key=lambda x: x.get('id'), reverse=False)

    for zona_electos in dic_zonas_electos:

        print( zona_electos['id'] , '-' , zona_electos['nombre'] , f"- Escaños : {zona_electos['cupos']}" )

        # Buscar el Pacto
        zona_pactos = Task.find(array = regiones,
                                key = 'zona',
                                value = zona_electos['id'])

        # Enlistar los Pactos electos de la zona por Mayoria
        for pacto in zona_electos['pactos']:

            # Buscar el Pacto
            pacto_total = Task.find(array = dic_pactos_electos,
                                    key = 'id',
                                    value = pacto['id'])
            
            # Buscar el Pacto
            pacto_candidatos = Task.find(array = zona_pactos[0]['pactos'],
                                    key = 'id',
                                    value = pacto['id'])
            
            # Buscar el Pacto
            candidatos_hombres = Task.find(array = pacto_candidatos[0]['candidatos'],
                                    key = 'genero',
                                    value = 'M')
            
            candidatos_mujeres = Task.find(array = pacto_candidatos[0]['candidatos'],
                                    key = 'genero',
                                    value = 'F')


            Task.validar_electos(zona = zona_electos['id'],
                                 pacto = pacto['id'],
                                 candidatos = pacto_candidatos[0]['candidatos'])

            print( pacto['id'] , pacto_candidatos[0]['candidatos'][0]['nombre'] )

            # Sumar a candidatos electos
            pacto_total[0]['electos'] += 1

        print('-        -       -       -       -       -       -       -       -')

    #       -       -       -       -       -       -       -       -       -       -

    print('ELECTOS POR PACTO')

    dic_pactos_electos.sort(key=lambda x: x.get('votos'), reverse=False)

    for pacto_electos in dic_pactos_electos:
        print( '>' , pacto_electos['id'] , ':' , pacto_electos['electos'] , '-' , 'votos' , ':' , pacto_electos['votos'] )

    # Crear Json Dump 
    json_dump = json.dumps(regiones, indent=4, sort_keys=True)

    # Crear Archivo JSON
    file = open("electos.json", "w")
    file.write(json_dump)
    file.close()

    print(' ')
    
    for zona_electos in dic_zonas_electos_finales:
        print( zona_electos['id'] , '-' , zona_electos['nombre'] , f"- Escaños : {zona_electos['cupos']}" )

        for electo in zona_electos['electos']:
            print(electo['pacto'] , electo['genero'] , electo['votos'] , electo['nombre'] )

        print(' ')

    print("Json Creado")
