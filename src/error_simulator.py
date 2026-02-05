# error_simulator.py
import random

def introduce_errors(dna: str, sub_rate: float = 0.01, ins_rate: float = 0.001, del_rate: float = 0.001):
    out = []
    bases = ['A', 'C', 'G', 'T']
    i = 0
    while i < len(dna):
        r = random.random()
        if r < del_rate:
            i += 1
            continue
        if r < del_rate + ins_rate:
            out.append(random.choice(bases))
            continue
        if r < del_rate + ins_rate + sub_rate:
            choices = [b for b in bases if b != dna[i]]
            out.append(random.choice(choices))
            i += 1
            continue
        out.append(dna[i])
        i += 1
    return ''.join(out)
