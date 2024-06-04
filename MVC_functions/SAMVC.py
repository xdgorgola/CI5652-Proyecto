import time
import random
from math import exp
from utils.graph import *
from .utils.tools_MVC import *

def evaluation_function(vc: set[int], g:Graph) -> float:
    is_vc, count_covered_edge = is_vc_gen_alt(vc, g)

    return len(vc)

def mov_probability(f_x, f_y, temperature):
    if f_x - f_y > 0:
        return 1 / (exp((f_y - f_x)/temperature))
    else:
        return 1
          

def SAMVC(g: Graph, 
          cutoff: int, 
          start_temperature: float, 
          end_temperature: float, 
          alpha: float,
          temperature_max_iter: int):
    
    s_prime, _ = construct_vc(g)
    s_star = type(s_prime)(s_prime)

    temperature = start_temperature
    start_time: float = time.time()
    found_time: float = start_time
    temperature_iter: int = 0

    while time.time() - start_time < cutoff:
        if temperature <= end_temperature:
            break
        while temperature > end_temperature: 
            u = random.choice(list(s_prime))
            v = random.randint(0, g.vertex_count - 1)

            while v in s_prime:
                v = random.randint(0, g.vertex_count - 1)

            evaluation_function_old = evaluation_function(s_prime, g)
            s_prime.remove(u)
            s_prime.add(v)
            evaluation_function_new = evaluation_function(s_prime,g)

            try:
                p: float = mov_probability(evaluation_function_old, evaluation_function_new, temperature)
            except:
                p = 1

            if p > random.uniform(0,1):
                if is_vc_alt(s_prime, g) and evaluation_function_new < evaluation_function(s_star, g):
                    s_star = type(s_prime)(s_prime)
                    found_time = time.time()
            else:
                s_prime.remove(v)
                s_prime.add(u)
            
            # print(f"temperature {temperature}")
            
            if temperature_max_iter == temperature_iter:
                temperature = alpha * temperature
                temperature_iter = 0
            else:
                temperature_iter += 1
    return (s_star, found_time-start_time)



