import time
import random
from math import exp
from utils.graph import *
from .utils.tools_MVC import *

def count_edges_covered(vc: set[int], g:Graph):
    count = 0
    for edge in g.edges:
        if edge[0] in vc or edge[1] in vc:
            count += 1

    return count

def evaluation_function(vc: set[int], g:Graph):
    uncovered_edges = g.edge_count() - count_edges_covered(vc, g)

    return uncovered_edges * g.vertex_count + len(vc)

def get_move_probability(vc_old: set[int], vc_new:set[int], g: Graph, temperature: float):
    f_x = evaluation_function(vc_old, g)
    f_y = evaluation_function(vc_new, g)

    print(f"f_x: {f_x}, f_y: {f_y}")
    print(f"temperatur: {temperature}")

    exponetial  = 0

    if f_x - f_y > 0:
        exponetial = (f_y - f_x)/temperature
        try:
            probability = 1 / exp(exponetial)
        except:
            probability = 1
    
    else:
        probability = 1
    
    return probability



def SAMVC(g: Graph, 
          cutoff: int, 
          start_temperature: float, 
          end_temperature: float, 
          alpha: float,
          temperature_max_iter: int):
    
    s_prime= set([i for i in range(g.vertex_count)])
    s_star = type(s_prime)(s_prime)

    temperature = start_temperature
    start_time: float = time.time() 
    found_time: float = start_time
    temperature_iter: int = 0

    while time.time() - start_time < cutoff and temperature > end_temperature:
            v = random.randint(0, g.vertex_count - 1)
            s_temp  = type(s_prime)(s_prime)

            if v in s_prime:
                s_temp.remove(v)
            else:
                s_temp.add(v)

            p: float = get_move_probability(s_prime, s_temp, g, temperature)
            print(f"p: {p}")
 
            if p > random.uniform(0,1):
                s_prime = type(s_temp)(s_temp)

                if is_vc_alt(s_prime, g) and evaluation_function(s_prime, g) < evaluation_function(s_star, g):
                    s_star = type(s_prime)(s_prime)
                    found_time = time.time()
            
            if temperature_max_iter == temperature_iter:
                temperature = alpha * temperature
                temperature_iter = 0
            else:
                temperature_iter += 1
    return (s_star, found_time-start_time)
