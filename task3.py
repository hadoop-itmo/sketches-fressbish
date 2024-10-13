import mmh3
import numpy as np

class CountingBloomFilter:
    def __init__(self, k, n, cap=1):
        self.k = k
        self.n = n
        self.cap = cap # кол-во бит на каждый счетчик
        self.bit_array = np.zeros(self.n * cap, dtype=np.uint8)

    def put(self, s):
        for i in range(self.k): # для кажой хэш-функции увеличиваем счетчики
            hash_value = mmh3.hash(s, i) % self.n
            self.bit_array[hash_value] = min(self.bit_array[hash_value] + 1, (1 << self.cap) - 1)

    def get(self, s):
        return all(self.bit_array[mmh3.hash(s, i) % self.n] > 0 for i in range(self.k))

    def delete(self, s):
        for i in range(self.k): # для кажой хэш-функции уменьшаем счетчики
            hash_value = mmh3.hash(s, i) % self.n
            if self.bit_array[hash_value] > 0:
                self.bit_array[hash_value] -= 1

    def size(self):
        return np.sum(self.bit_array) / self.k # сумма счетчиков / k