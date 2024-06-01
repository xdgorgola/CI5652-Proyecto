import time
import random
from math import exp
from utils.graph import *
from .utils.tools_MVC import *

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
        while temperature > end_temperature: 
            v = random.randint(0, g.vertex_count - 1)

            p: float = exp(-(1 + g.get_degree(v))/temperature)

            if v in s_prime and p < random.uniform(0,1):
                s_prime.remove(v)
            
            if v not in s_prime and p < random.uniform(0,1):
                s_prime.add(v)

            if is_vc_alt(s_prime, g) and len(s_prime) < len(s_star):
                s_star = type(s_prime)(s_prime)
                found_time = time.time()
            
            if temperature_max_iter == temperature_iter:
                temperature = alpha * temperature
                temperature_iter = 0
            else:
                temperature_iter += 1
    return (s_star, found_time-start_time)



def SAMVC_version_blog(g: Graph, 
          cutoff: int, 
          start_temperature: float, 
          end_temperature: float, 
          alpha: float):
    
    vc: set[int] = set([i for i in range(g.vertex_count)])

    start_time: float = time.time()
    found_time: float | None = None

    temperature = start_temperature
    while time.time() - start_time < cutoff:
        while temperature > end_temperature:
            v = random.randint(0, g.vertex_count - 1)
            while v in vc:
                vc.remove(v)
                if not is_vc_alt(vc, g):
                    vc.add(v)
                else:
                    vc.add(v)

                p: float = exp(-(1+g.get_degree(v))/temperature)

                if p < random.uniform(0,1):
                    vc.remove(v)
            
            temperature = alpha * temperature
    
    return (vc, time.time() - start_time)



