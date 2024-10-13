import mmh3
import numpy as np

class numpyBloomFilter:
    def __init__(self, n):
        self.n = n
        self.bit_array = np.zeros(self.n, dtype=bool)  # битовый массив numpy

    def put(self, s):
        hash_value = mmh3.hash(s) % self.n # хэш
        self.bit_array[hash_value] = True

    def get(self, s):
        hash_value = mmh3.hash(s) % self.n # хэш
        return self.bit_array[hash_value]

    def size(self):
        return np.sum(self.bit_array) # кол-во единиц в массиве