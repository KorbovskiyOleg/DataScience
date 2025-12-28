#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для очистки и нормализации испорченного файла результатов PageRank
"""

import sys
import os


def clean_results_file(input_file, output_file=None):
    """Очистка файла результатов от экранированных символов"""
    if output_file is None:
        output_file = input_file + '.cleaned'
    
    lines_processed = 0
    lines_written = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in:
            with open(output_file, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    lines_processed += 1
                    original_line = line
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
                    
                    # Проверяем формат
                    if '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            node = parts[0].strip().strip('"').strip("'")
                            links = parts[1].strip().strip('"').strip("'") if len(parts) > 1 else ''
                            rank = parts[2].strip().strip('"').strip("'") if len(parts) > 2 else '1.0'
                            
                            # Пропускаем пустые узлы
                            if not node or node.lower() == 'none' or node.lower() == 'null':
                                continue
                            
                            f_out.write(f"{node}\t{links}\t{rank}\n")
                            lines_written += 1
        
        print(f"Обработано строк: {lines_processed}")
        print(f"Записано валидных строк: {lines_written}")
        print(f"Результат сохранен в: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python clean_results.py <input_file> [output_file]")
        print("Пример: python clean_results.py pagerank_results.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Ошибка: файл '{input_file}' не найден!")
        sys.exit(1)
    
    clean_results_file(input_file, output_file)

