from MVC_functions.graspMVC import graspMVC
from MVC_functions.SAMVC import SAMVC_version_blog, SAMVC
from utils.graph import * 
import time


def main():
    path = "./res/bio-yeast.mtx"

    g = AdjacencyDictGraph(read_mtx("res/datos/grafos_masivos/bio-yeast.mtx"))
    
    print("########################|Inicio|##########################")
    start = time.time()
    MVC_solution, found_time = SAMVC(g, 300, 100, 0, 0.1, 30)
    print(f"Tardo en total {time.time() - start} segundos")
    print(f"Encontro una solucion aceptable a los {found_time} segundos")
    print(f"El conjunto de vertices tiene {len(MVC_solution)} vertices")
    print(f'Es un VC?: {is_vc_alt(MVC_solution, g)}')
    print("########################|Fin|##########################")

# def main():
#     path = "./res/bio-yeast.mtx"

#     g = AdjacencyDictGraph(read_mtx("res/datos/grafos_masivos/bio-yeast.mtx"))
    
#     print("########################|Inicio|##########################")
#     print(len(greedy_randomize_building(g, 0.5)))
#     print("########################|Fin|##########################")

if __name__ == "__main__":
    main()
