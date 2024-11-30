import mmh3
import numpy as np
import math

class HyperLogLog:
    def __init__(self, b):
        self.b = b
        self.m = 1 << b
        self.registers = [0] * self.m
        if self.m == 16:
            self.a = 0.673
        elif self.m == 32:
            self.a = 0.697
        elif self.m == 64:
            self.a = 0.709
        else:
            self.a = 0.7213 / (1 + 1.079 / self.m)

    def put(self, s):
        x = mmh3.hash(s, signed=False)
        x_bin = bin(x)[2:].zfill(32)
        j = int(x_bin[:self.b], 2)
        w = x_bin[self.b:]
        self.registers[j] = max(self.registers[j], len(w) - len(w.lstrip('0')) + 1)

    def est_size(self):
        Z = sum(2.0 ** -reg for reg in self.registers)
        E = self.a * self.m * self.m / Z
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0:
                E = self.m * math.log(self.m / V)
        elif E > (1 / 30.0) * (1 << 32):
            E = -(1 << 32) * math.log(1 - E / (1 << 32))
        return E