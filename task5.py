import math
import numpy as np
import pandas as pd
import random
import csv
from collections import Counter

def create_grouped_data(filename, groups_pattern, extra_columns=0, shuffle_rows=False):
    rows = []
    global_group_index = 0
    for num_groups, records_per_group in groups_pattern:
        for group in range(num_groups):
            key = f"grp{global_group_index}"
            for _ in range(records_per_group):
                # формируем строку, начиная с ключа
                line = key
                # добавляем дополнительные колонки
                for col in range(extra_columns):
                    line += f",val{col}"
                rows.append(line)
            global_group_index += 1

    if shuffle_rows:
        random.shuffle(rows)

    with open(filename, "w") as f:
        for line in rows:
            f.write(line + "\n")

def sample_key_counts(file_path, sample_prob, filter_keys=None):
    # выбирает каждую строку с определенной вероятностью sample_prob
    # подсчитывает вхождения ключей
    counts = Counter()
    sampled_total = 0
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if random.random() < sample_prob:
                sampled_total += 1
                key = row[0]
                if filter_keys is None or key in filter_keys:
                    counts[key] += 1
    return counts, sampled_total

def exact_key_counts(file_path, candidate_keys):
    # точный подсчет вхождений для ключей из candidate_keys
    counts = Counter({k: 0 for k in candidate_keys})
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            key = row[0]
            if key in counts:
                counts[key] += 1
    return counts

def detect_heavy_keys(file1, file2, threshold, sample_prob=0.001):
    # определяет проблемные ключи, которые встречаются не менее чем threshold раз в обоих файлах
    # 1 – выборка по file1
    # 2 – отбираем кандидатов, чья выборочная частота не меньше threshold * sample_prob / factor (ниже расписал подробнее об этом)
    # 3 – аналогичная выборка по file2 для кандидатов
    # 4 – для оставшихся кандидатов выполняем точный подсчет в обоих файлах и возвращаем те, у которых точная частота >= threshold

    factor = 2
    # factor нужен, чтобы компенсировать дисперсию выборки
    # в случае, если мы пропустим частые ключи из-за недостаточной выборки, они все равно туда попадут
    # при этом уменьшаем объем обрабатываемых данных за счет случайной выборки
    expected_sample_threshold = threshold * sample_prob
    # по expected_sample_threshold будем отбирать частые ключи
    # threshold умножаем на sample_prob, т.к. выборка состоит из ключей, попавших с вероятностью sample_prob

    # 1 – выборка по первому файлу
    sample_counts1, sample_size1 = sample_key_counts(file1, sample_prob)

    # 2 – отбираем кандидатов
    candidate_set = {key for key, cnt in sample_counts1.items() if cnt >= expected_sample_threshold / factor}
    if not candidate_set:
        return []

    # 3 – выборка по второму файлу только для кандидатов
    sample_counts2, sample_size2 = sample_key_counts(file2, sample_prob, filter_keys=candidate_set)
    # обновляем уже имеющийся набор кандидатов с условием на второй файл
    candidate_set = {key for key in candidate_set if sample_counts2.get(key, 0) >= expected_sample_threshold / factor}
    if not candidate_set:
        return []

    # 4 – точный подсчет в обоих файлах для оставшихся кандидатов
    exact_counts1 = exact_key_counts(file1, candidate_set)
    exact_counts2 = exact_key_counts(file2, candidate_set)
    heavy_keys = [key for key in candidate_set
                  if exact_counts1.get(key, 0) >= threshold and exact_counts2.get(key, 0) >= threshold]
    return heavy_keys

pattern = [(5, 80000), (50, 20000)]
create_grouped_data("test_file1.csv", pattern, extra_columns=0, shuffle_rows=True)
create_grouped_data("test_file2.csv", pattern, extra_columns=0, shuffle_rows=True)
heavy_threshold = 60000  # порог для проблемных ключей
problematic_keys = detect_heavy_keys('test_file1.csv', 'test_file2.csv', heavy_threshold, sample_prob=0.001) # чем ниже sample_prob, тем меньше данных в памяти, но выше дисперсия.

print(f"Проблемные ключи (>= {heavy_threshold} в обоих файлах):")
for key in problematic_keys:
    print(key)

pattern = [(1, 61000), (99, 20000)]
create_grouped_data("test_file1.csv", pattern, extra_columns=0, shuffle_rows=True)
create_grouped_data("test_file2.csv", pattern, extra_columns=0, shuffle_rows=True)
heavy_threshold = 60000
problematic_keys = detect_heavy_keys('test_file1.csv', 'test_file2.csv', heavy_threshold, sample_prob=0.001)

print(f"Проблемные ключи (>= {heavy_threshold} в обоих файлах):")
for key in problematic_keys:
    print(key)
