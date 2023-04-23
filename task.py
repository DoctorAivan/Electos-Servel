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

    def validar_electos(zona):
        print(zona)

