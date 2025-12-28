#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для запуска PageRank с удобным вводом и выводом
"""

import subprocess
import sys
import os
import time
from collections import defaultdict


def print_header():
    """Вывод заголовка"""
    print("=" * 70)
    print(" " * 20 + "PageRank MapReduce")
    print("=" * 70)
    print()


def print_statistics(input_file, output_file, iterations, damping):
    """Вывод статистики о входных данных"""
    print("\n" + "=" * 70)
    print("СТАТИСТИКА ВХОДНЫХ ДАННЫХ")
    print("=" * 70)
    
    nodes = set()
    edges = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    node = parts[0]
                    nodes.add(node)
                    links = parts[1].split(',') if parts[1] else []
                    edges += len([l for l in links if l.strip()])
        
        print(f"Файл входных данных: {input_file}")
        print(f"Количество узлов: {len(nodes)}")
        print(f"Количество рёбер: {edges}")
        print(f"Количество итераций: {iterations}")
        print(f"Damping factor: {damping}")
        print("=" * 70 + "\n")
    except Exception as e:
        print(f"Ошибка при чтении статистики: {e}\n")


def run_pagerank(input_file, iterations=10, damping=0.85, output_file=None):
    """Запуск PageRank алгоритма"""
    
    print_header()
    print_statistics(input_file, output_file, iterations, damping)
    
    print("Запуск PageRank...")
    print("-" * 70)
    
    # Подготовка данных для первой итерации
    temp_file = "temp_pagerank_input.txt"
    
    # Инициализируем ранги
    with open(input_file, 'r', encoding='utf-8') as f_in:
        with open(temp_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                if not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    node = parts[0]
                    links = parts[1]
                    # Если ранг уже указан, используем его, иначе 1.0
                    if len(parts) >= 3 and parts[2]:
                        try:
                            initial_rank = float(parts[2])
                            f_out.write(f"{node}\t{links}\t{initial_rank}\n")
                        except ValueError:
                            f_out.write(f"{node}\t{links}\t1.0\n")
                    else:
                        f_out.write(f"{node}\t{links}\t1.0\n")
    
    # Выполняем итерации
    current_file = temp_file
    
    for iteration in range(1, iterations + 1):
        print(f"Итерация {iteration}/{iterations}...", end=' ', flush=True)
        
        next_file = f"temp_pagerank_iter_{iteration}.txt"
        
        # Запускаем mrjob
        cmd = [
            sys.executable, 'pagerank.py',
            '--damping', str(damping),
            '-r', 'inline',  # Запуск локально, без Hadoop
            current_file
        ]
        
        try:
            start_time = time.time()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                check=True,
                cwd=os.getcwd()
            )
            elapsed = time.time() - start_time
            
            # Сохраняем результат
            lines_written = 0
            with open(next_file, 'w', encoding='utf-8') as f:
                # mrjob выводит результаты в stdout
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Пропускаем служебные строки mrjob
                    if (line.startswith('No configs') or 
                        line.startswith('Creating') or 
                        line.startswith('Streaming') or
                        line.startswith('Running') or
                        line.startswith('Using') or
                        line.startswith('Job') or
                        line.startswith('Counters:')):
                        continue
                    
                    # Убираем кавычки и служебные символы
                    clean_line = line.replace('"', '').replace("'", "").strip()
                    
                    # Декодируем экранированные символы (если они есть)
                    # Сначала убираем двойные экранирования (обрабатываем в обратном порядке)
                    # Заменяем множественные экранирования
                    while '\\\\t' in clean_line or '\\\\\\\\' in clean_line:
                        clean_line = clean_line.replace('\\\\t', '\\t')
                        clean_line = clean_line.replace('\\\\\\\\', '\\\\')
                    
                    # Заменяем литеральные \t на реальные табуляции
                    clean_line = clean_line.replace('\\t', '\t')
                    # Убираем оставшиеся двойные обратные слеши (но оставляем одиночные, если они нужны)
                    clean_line = clean_line.replace('\\\\', '\\')
                    
                    # Убираем возможные None/null в начале (от mrjob)
                    if clean_line.startswith('None\t'):
                        clean_line = clean_line[5:]  # Убираем "None\t" (5 символов)
                    elif clean_line.startswith('null\t'):
                        clean_line = clean_line[5:]  # Убираем "null\t"
                    elif clean_line.startswith('"None"\t') or clean_line.startswith("'None'\t"):
                        clean_line = clean_line[7:] if clean_line.startswith('"None"\t') else clean_line[7:]
                    elif clean_line.startswith('"null"\t') or clean_line.startswith("'null'\t"):
                        clean_line = clean_line[7:] if clean_line.startswith('"null"\t') else clean_line[7:]
                    
                    # Проверяем, что это строка с данными (содержит табуляцию)
                    if '\t' in clean_line:
                        # Проверяем формат: node\tlinks\trank
                        parts = clean_line.split('\t')
                        if len(parts) >= 2:
                            # Нормализуем строку: убираем лишние пробелы и кавычки
                            node = parts[0].strip().strip('"').strip("'")
                            links = parts[1].strip().strip('"').strip("'") if len(parts) > 1 else ''
                            rank = parts[2].strip().strip('"').strip("'") if len(parts) > 2 else '1.0'
                            
                            # Пропускаем пустые узлы
                            if not node or node.lower() == 'none' or node.lower() == 'null':
                                continue
                            
                            # Записываем в правильном формате
                            output_line = f"{node}\t{links}\t{rank}\n"
                            f.write(output_line)
                            lines_written += 1
            
            # Проверяем, что файл не пустой
            if lines_written == 0:
                print(f"✗ Предупреждение: нет данных в выводе!")
                if result.stderr:
                    print(f"Ошибки: {result.stderr[:200]}")
                return None
            
            print(f"✓ ({elapsed:.2f} сек)")
            
            # Используем результат как вход для следующей итерации
            if current_file != temp_file and os.path.exists(current_file):
                try:
                    os.remove(current_file)
                except:
                    pass
            current_file = next_file
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка!")
            print(f"Ошибка: {e.stderr}")
            return None
        except Exception as e:
            print(f"✗ Ошибка: {e}")
            return None
    
    print("-" * 70)
    print("Вычисление завершено!\n")
    
    # Сохраняем финальный результат
    if output_file:
        if os.path.exists(current_file):
            # Копируем содержимое с нормализацией данных
            with open(current_file, 'r', encoding='utf-8') as f_in:
                with open(output_file, 'w', encoding='utf-8') as f_out:
                    for line in f_in:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Декодируем экранированные символы
                        # Убираем множественные экранирования
                        while '\\\\t' in line or '\\\\\\\\' in line:
                            line = line.replace('\\\\t', '\\t')
                            line = line.replace('\\\\\\\\', '\\\\')
                        
                        line = line.replace('\\t', '\t').replace('\\\\', '\\')
                        
                        # Убираем None/null в начале
                        if line.startswith('None\t'):
                            line = line[5:]
                        elif line.startswith('null\t'):
                            line = line[5:]
                        elif line.startswith('"None"\t') or line.startswith("'None'\t"):
                            line = line[7:]
                        elif line.startswith('"null"\t') or line.startswith("'null'\t"):
                            line = line[7:]
                        
                        # Нормализуем формат
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            node = parts[0].strip().strip('"').strip("'")
                            links = parts[1].strip().strip('"').strip("'") if len(parts) > 1 else ''
                            rank = parts[2].strip().strip('"').strip("'") if len(parts) > 2 else '1.0'
                            
                            # Пропускаем пустые узлы
                            if not node or node.lower() == 'none' or node.lower() == 'null':
                                continue
                            
                            f_out.write(f"{node}\t{links}\t{rank}\n")
            
            # Удаляем временный файл после копирования
            try:
                os.remove(current_file)
            except:
                pass
        else:
            print(f"Предупреждение: файл {current_file} не найден!")
    else:
        output_file = current_file
    
    return output_file


def print_results(output_file, top_n=10):
    """Вывод результатов PageRank"""
    print("=" * 70)
    print("РЕЗУЛЬТАТЫ PAGERANK")
    print("=" * 70)
    
    results = []
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    node = parts[0]
                    rank = float(parts[2])
                    results.append((node, rank))
        
        # Сортируем по рангу
        results.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n{'Ранг':<8} {'PageRank':<15} {'Узел'}")
        print("-" * 70)
        
        for i, (node, rank) in enumerate(results[:top_n], 1):
            print(f"{i:<8} {rank:<15.6f} {node}")
        
        if len(results) > top_n:
            print(f"\n... и ещё {len(results) - top_n} узлов")
        
        print("\n" + "=" * 70)
        print(f"Всего узлов: {len(results)}")
        print(f"Максимальный PageRank: {results[0][1]:.6f}")
        print(f"Минимальный PageRank: {results[-1][1]:.6f}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"Ошибка при чтении результатов: {e}\n")


def cleanup_temp_files():
    """Удаление временных файлов"""
    import glob
    temp_files = glob.glob("temp_pagerank*.txt")
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass


def main():
    """Главная функция"""
    print_header()
    
    # Параметры по умолчанию
    input_file = "graph.txt"
    output_file = "pagerank_results.txt"
    iterations = 10
    damping = 0.85
    
    # Проверка аргументов командной строки
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        iterations = int(sys.argv[3])
    if len(sys.argv) > 4:
        damping = float(sys.argv[4])
    
    # Проверка существования входного файла
    if not os.path.exists(input_file):
        print(f"Ошибка: файл '{input_file}' не найден!")
        print("\nИспользование: python run_pagerank.py [input_file] [output_file] [iterations] [damping]")
        print("Пример: python run_pagerank.py graph.txt results.txt 10 0.85")
        return
    
    try:
        # Запуск PageRank
        result_file = run_pagerank(input_file, iterations, damping, output_file)
        
        if result_file:
            # Вывод результатов
            print_results(result_file)
            print(f"Результаты сохранены в файл: {result_file}\n")
        
        # Очистка временных файлов
        cleanup_temp_files()
        
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        cleanup_temp_files()
    except Exception as e:
        print(f"\nОшибка: {e}")
        cleanup_temp_files()


if __name__ == '__main__':
    main()

