import os
import math
from MVC_functions.fastVC import fastVC
from MVC_functions.TS import tabu_search
from MVC_functions.graspMVC import graspMVC
from MVC_functions.patrickStar import patrick_star, random_fragmentation, patrick_fitness
from MVC_functions.local_searchMVC import local_searchMVC
from MVC_functions.SAMVC import SAMVC
from threading import Thread
import sys
from utils.graph import AdjacencyDictGraph, is_vc_gen_alt,read_mtx

import pandas as pd

def exec_TS(g, result, index):
    solution = tabu_search(g, 100, 50)
    result[index] = [len(solution[0]), solution[1]]

def exec_grasp(g, time, result, index):
    solution = graspMVC(g, time)
    result[index] = [len(solution[0]), solution[1]]

def exec_local(g, time, result, index):
    solution = local_searchMVC(g, time)
    result[index] = [len(solution[0]), solution[1]]

def exec_fastvc(g, time, result, index):
    solution = fastVC(g, time)
    result[index] = [len(solution[0]), solution[1]]

def exec_samvc(g, time, result, index):
    MVC_solution, found_time = SAMVC(g, 300, 30, 0.0001, 0.9999, 30)
    result[index] = [len(MVC_solution), found_time]

def main(dir_path_in:str, dir_path_out:str, files_per_batch:str, type:str):
    """
    Utiliza hilos para realizar fastvc en varios archivos al mismo tiempo 
    10 veces seguidas.

    Cuando termina crea un archivo .csv por cada archivo en dir_path_in,
    cada archivo tiene el tamaño del mejor C que encontro y cuanto tiempo
    le tomo encontrarlo.

    Cada ejecucion de Fastvc tiene un tiempo limite de 5 minutos
    
    Args:
    ----------
    dir_path_in: Direccion con todos los archivos a procesar

    dir_path_out: Direccion donde se guardaran los archivos .csv 
                  con los resultados de las 10 corridas de fastvc
                  sobre cada garfo en los archivos de entrada
    
    files_per_batch: El numero de archivos que quieres procesar
                     al mismo tiempo
    """
    graphs = os.listdir(dir_path_in)
    files_per_batch = int(files_per_batch)

    counter = 0
    result = [[None, None]] * 10 * files_per_batch
    threads = [None] * 10 * files_per_batch
    files_name = []
    
    for file in graphs:
        path = os.path.join(dir_path_in, file)
        g = AdjacencyDictGraph(read_mtx(path))

        print(f"Lanzando Hilos para el archivo {file}")
        for i in range(10):
            if type == "fastvc":
                threads[i + 10*counter] = Thread(target= exec_fastvc, args=(g,300,result, i + 10*counter))
            elif type == "ts":
                threads[i + 10*counter] = Thread(target= exec_TS, args=(g,result, i + 10*counter))
            elif type == "grasp":
                threads[i + 10*counter] = Thread(target= exec_grasp, args=(g,300,result, i + 10*counter))
            elif type == "sa":
                threads[i + 10*counter] = Thread(target= exec_samvc, args=(g,300,result, i + 10*counter))
            else:
                threads[i + 10*counter] = Thread(target= exec_local, args=(g,300,result, i + 10*counter))
                
            threads[i + 10*counter].start()
        print(f"Hilos Lanzados para el archivo {file}")

        counter += 1
        files_name.append(file)
        
        if counter == files_per_batch:
            for i in range(len(threads)):
                threads[i].join()
            
            for i in range(files_per_batch):
                pd.DataFrame(result[10*i : 10*(i+1)], columns=["size", "time"]).to_csv(os.path.join(dir_path_out, "result-" + files_name[i][0:-4] + ".csv"), sep=";", index=False)
            
            print(f"Archivos {files_name} procesados")

            counter = 0
            result = [[None, None]] * 10 * files_per_batch
            threads = [None] * 10 * files_per_batch
            files_name = []
    
    if counter > 0:
        for i in range(len(threads)):
            if threads[i] != None:
                threads[i].join()
            
        for i in range(counter):
            pd.DataFrame(result[10*i : 10*(i+1)], columns=["size", "time"]).to_csv(os.path.join(dir_path_out, "result-" + files_name[i][0:-4] + ".csv"), sep=";", index=False)


if __name__ == "__main__":
    g = AdjacencyDictGraph(read_mtx("./res/bio-yeast.mtx"))
    #g = AdjacencyDictGraph(read_mtx("./res/web-google.mtx"))
    #g = AdjacencyDictGraph(read_mtx("./res/ia-email-univ.mtx"))
    #g = AdjacencyDictGraph(read_mtx("./res/ia-fb-messages.mtx"))
    #g = AdjacencyDictGraph(read_mtx("./res/tech-internet-as.mtx"))
    #g = AdjacencyDictGraph(read_mtx("./res/ia-wiki-Talk.mtx"))

    res = patrick_star(g, 60 * 60, 60 * 2, 1, 16, 1, 1, lambda bm: patrick_fitness(bm, g), lambda bm: random_fragmentation(bm, 35), None)
    (is_vc, cov_amnt) = is_vc_gen_alt(set(res[0].true_pos()), g)
    print(f"Amount set {res[0].amount_set}\n Time {res[1]}\n Fitness {res[2]}\n IsVc {is_vc}\n Covered Amount {cov_amnt}\n {res[0]}")