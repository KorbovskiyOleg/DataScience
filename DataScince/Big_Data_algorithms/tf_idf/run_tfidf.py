#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для запуска TF*IDF MapReduce приложения
"""

import os
import subprocess
import sys

def count_documents(data_dir):
    """Подсчитывает количество документов в директории"""
    count = 0
    for filename in os.listdir(data_dir):
        if filename.endswith('.txt'):
            count += 1
    return count

def main():
    # Путь к директории с данными
    data_dir = 'data'
    
    # Проверяем наличие директории
    if not os.path.exists(data_dir):
        print(f"Ошибка: директория {data_dir} не найдена!")
        sys.exit(1)
    
    # Подсчитываем количество документов
    num_docs = count_documents(data_dir)
    print(f"Найдено документов: {num_docs}")
    
    # Запрашиваем поисковый запрос
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
    else:
        query = input("Введите поисковый запрос (слова через пробел): ")
    
    if not query:
        print("Ошибка: поисковый запрос не может быть пустым!")
        sys.exit(1)
    
    print(f"Поисковый запрос: {query}")
    print("\nЗапуск MapReduce...\n")
    
    # Формируем команду для запуска
    cmd = [
        'python', 'tf_idf.py',
        '--num-docs', str(num_docs),
        '--query', query,
        data_dir + '/*.txt'
    ]
    
    # Запускаем MapReduce
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Ошибка: не найден файл tf_idf.py или Python не установлен!")
        sys.exit(1)

if __name__ == '__main__':
    main()

