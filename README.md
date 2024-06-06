# CI5652-Proyecto
## Integrantes 
Pedro Rodríguez 15-11264

Gabriela Panqueva, 18-10761

Kenny Rojas, 18-10595

## Resumen

main.py: Contiene la función que permite ejecutar varias veces los algoritmos. Forma en la que hay que correr el este archivo:

`python main.py [path_in] [path_out] [files_per_batch] [type]`
        
Los tipos permitidos son: fastvc, ts, grasp, sa y cualquier otro tipo sera tomado como la busqueda local normal

runMVC.py: Contiene la función que permite ejeuctar una unica vez uno de los algoritmos. 

utils/: Modulo de python que contiene las clases y funciones necesarias para representar un grafo.

MVC_functions/: Modulo de python que contiene todos los codigos con los algoritmos a usar.

MVC_functions/utils: Modulo de python que contiene funciones utilizadas por varios algoritmos.

MVC_functions/fastVC.py: Implementación del código del algoritmo FastVC explicado en el paper Balance between Complexity and Quality: Local Search for Minimum Vertex Cover in Massive Graphs.

MVC_functions/SAMVC.py: Implementación del algoritmo del Recocido Simulado.

MVC_functions/TS.py: Implementación del algoritmo de la busqueda local tabu.

MVC_functions/local_search.py: Implementación del algoritmo de la busqueda local sin ninguna modificación.

MVC_functions/graspMVC.py: Implementación del algoritmo GRASP.

MVC_functions/geneticVC.py: Implementación de un algortimo genetico para resolver el MVC.

MVC_functions/brute_forceMVC.py: Contiene una implementación de un algoritmo exacto para solucionar MVC.

