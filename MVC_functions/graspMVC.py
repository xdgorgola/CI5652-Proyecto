import time
import random
from utils.graph import *
from .local_searchMVC import local_searchMVC
from .utils.tools_MVC import vertex_gain

def build_RCL(gain:list[float], alpha:float)->list[int]:
    s: list[int] = []
    min_cs: list[float] =  min(gain)
    max_cs: list[float] =  max(gain)

    for i in range(len(gain)):
        # Modificacion de la funcion vista en clase. 
        # Esta funcion no busca la minimizar el cs
        # busca maximizarla, por lo que si alpha
        # es 0 te da todos los vertices cuyo cs
        # sea el maximo
        if gain[i] >= max_cs - alpha*(max_cs - min_cs):
            s.append(i)
    
    return s

def greedy_randomize_building(g:Graph, alpha:float, cutoff:float):
    s: list[int] = set()
    gain:list[float] = []

    # al inicio como ningun lado esta cubierto la 
    # ganancia de cualquier vertice es su grado
    # o la cantidad de lados que lo tienen como 
    # componente
    for i in range(g.vertex_count):
        gain.append(g.get_degree(i))
    
    start_time = time.time()
    while not is_vc_alt(s,g):
        if time.time() - start_time > cutoff:
            raise Exception("Tardo demasiado")
        
        RCL: list[int] = build_RCL(gain,alpha)
        e: int = random.choice(RCL)
       
        s.add(e)

        # actualizamos la ganancia
        # Como siempre agregamos 1 es facil 
        # actualizar la ganancia ya que solo 
        # es reducir la ganacia de sus vecinos
        for i in g.get_neighboors(e):
            if gain[i] > 0:
                gain[i] -= 1
        
        # Le quitamos la ganancia a e por que ya esta 
        # agregado, asi tambien ya no saldra en el RCL
        # Tambien podriamos ponerla a -1 pero creo que con
        # 0 basta
        gain[e] = 0
    
    return s 


def partial_greedy_randomize_building(g:Graph, part: set[int], alpha:float, cutoff:float):
    s: set[int] = set(part)
    gain: list[float] = []

    for i in range(g.vertex_count):
        gain.append(g.get_degree(i))

    for i in s:
        gain[i] = 0
    
    start_time = time.time()
    while not is_vc_alt(s,g):
        if time.time() - start_time > cutoff:
            raise Exception("Tardo demasiado")
        
        RCL: list[int] = build_RCL(gain, alpha)
        e: int = random.choice(RCL)
        s.add(e)

        for i in g.get_neighboors(e):
            if gain[i] > 0:
                gain[i] -= 1

        gain[e] = 0
    return s 


def calculate_loss(g:Graph, C: list[int]) -> list[int]:
    vloss: list[int] = [0 for _ in range(g.vertex_count)]
    
    for e in g.edges:
        if e[0] in C and e[1] in C:
            continue

        looser = e[0] if e[0] in C else e[1]
        vloss[looser] = vloss[looser] + 1
    
    for v in list(C):
        if vloss[v] != 0:
            continue
        C.remove(v)
        for n in g.get_neighboors(v):
            vloss[n] = vloss[n] + 1
    
    return vloss

def graspMVC(g: Graph, cutoff: int):
    c_star: set[int] | None = None
    start_time: float = time.time()
    found_time: float | None = None

    while time.time() - start_time < cutoff: 
        try:
            c_prime = greedy_randomize_building(g, 0.25, cutoff/5)
        except:
            return (set(), -1)

        vloss = calculate_loss(g,c_prime)

        c_prime_star, _ = local_searchMVC(g, cutoff/2, 100, (c_prime, vloss))
        
        if c_star == None or len(c_prime_star) > len(c_star):
            found_time = time.time()
            c_star = type(c_prime_star)(c_prime_star)
    
    return (c_star, found_time - start_time)


def partialGraspMVC(g: Graph, partial: set[int], cutoff: int):
    c_star: set[int] | None = None
    start_time: float = time.time()

    while time.time() - start_time < cutoff: 
        try:
            c_prime = partial_greedy_randomize_building(g, partial, 0.25, cutoff/5)
        except:
            return (set(), -1)

        vloss = calculate_loss(g,c_prime)
        c_prime_star, _ = local_searchMVC(g, cutoff/2, 100, (c_prime, vloss))
        
        if c_star == None or len(c_prime_star) > len(c_star):
            c_star = type(c_prime_star)(c_prime_star)
    
    return c_star