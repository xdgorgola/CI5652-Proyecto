import os
from MVC_functions.fastVC import fastVC
from threading import Thread
import sys
from utils.graph import AdjacencyDictGraph,read_mtx

import pandas as pd

def exec_fastvc(g, time, result, index):
    solution = fastVC(g, time)
    result[index] = [len(solution[0]), solution[1]]

def main(dir_path_in, dir_path_out, files_per_batch):
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
            threads[i + 10*counter] = Thread(target= exec_fastvc, args=(g,300,result, i + 10*counter))
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
    """
    Ejemplo de como deben llamar a este script
        python .\main.py .\res\datos .\res\results\ 5
    
    """
    if len(sys.argv) != 4:
        print("Wrong amount of parameters used. Usage:")
        print("\tpython fastVC.py [path_in] [path_out] [files_per_batch]")
        sys.exit(1)

    main(*sys.argv[1:])