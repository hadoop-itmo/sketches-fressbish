import mmh3
import numpy as np

class numpyBloomFilter_k:
    def __init__(self, k, n):
        self.k = k
        self.n = n
        self.bit_array = np.zeros(self.n, dtype=bool)

    def put(self, s):
        for i in range(self.k): # в цикле проходимся по k хэш-функций
            hash_value = mmh3.hash(s, i) % self.n
            self.bit_array[hash_value] = True

    def get(self, s):
        return all(self.bit_array[mmh3.hash(s, i) % self.n] for i in range(self.k))

    def size(self):
        return np.sum(self.bit_array) / self.k # кол-во единиц в массиве / k