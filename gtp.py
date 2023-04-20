def asignar_cupos_parity(votos_nacionales, votos_circunscripciones):
    """
    Asigna los cupos para asegurar la paridad entre hombres y mujeres en un sistema electoral.

    Args:
        votos_nacionales (dict): Un diccionario con los votos nacionales por lista o pacto electoral,
                                donde las claves son los nombres de las listas o pactos y los valores son
                                la cantidad de votos obtenidos.
        votos_circunscripciones (dict): Un diccionario con los votos por circunscripción (región) senatorial,
                                       donde las claves son los nombres de las circunscripciones y los valores
                                       son diccionarios similares al de votos_nacionales, pero con los votos
                                       obtenidos por lista o pacto electoral en esa circunscripción.

    Returns:
        dict: Un diccionario con la asignación de cupos a nivel nacional y por circunscripción,
              donde las claves son los nombres de las listas o pactos y las circunscripciones, respectivamente,
              y los valores son las listas de candidatos asignados para asegurar la paridad entre hombres y mujeres.
    """
    cupos_mujeres = 25
    cupos_hombres = 25

    # Ordenar las listas o pactos de acuerdo al total de votos a nivel nacional
    listas_nacionales_ordenadas = sorted(votos_nacionales.keys(), key=lambda x: votos_nacionales[x])

    # Ordenar las circunscripciones de acuerdo al total de votos emitidos
    # en favor de las respectivas listas o pactos en cada circunscripción
    circunscripciones_ordenadas = sorted(votos_circunscripciones.keys(),
                                        key=lambda x: sum(votos_circunscripciones[x].values()))

    asignaciones_nacionales = {}  # Diccionario para almacenar las asignaciones a nivel nacional
    asignaciones_circunscripciones = {}  # Diccionario para almacenar las asignaciones por circunscripción

    while cupos_mujeres > 0 or cupos_hombres > 0:
        # Verificar si se ha alcanzado la paridad en las listas nacionales
        if cupos_mujeres <= 0:
            break

        # Obtener la lista o pacto electoral con menos votos a nivel nacional
        lista_nacional_menos_votos = listas_nacionales_ordenadas.pop(0)

        # Obtener los votos por circunscripción para la lista o pacto electoral seleccionado
        votos_lista_circunscripciones = votos_circunscripciones.get(lista_nacional_menos_votos, {})

        # Ordenar las circunscripciones de acuerdo al total de votos emitidos
        # en favor de la lista o pacto en cada circunscripción
        circunscripciones_lista_ordenadas = sorted(votos_lista_circunscripciones.keys(),
                                                    key=lambda x: votos_lista_circunscripciones[x])

        while cupos_mujeres > 0:
            
            # Verificar si se ha alcanzado la paridad en la circunscripción
            if cupos_hombres <= 0:
                break

            # Obtener la circunscripción con menos votos válidamente emitidos
            circunscripcion_menos_votos = circunscripciones_lista
