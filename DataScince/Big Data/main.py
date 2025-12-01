#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Главный скрипт для запуска MapReduce приложения анализа текстов
Единая точка входа для всего проекта
"""

import os
import sys
import glob
import subprocess
import json
import re
from pathlib import Path
from collections import defaultdict

# Константы
TF_OUTPUT = "tf_output.txt"
WORD_RE = re.compile(r"[A-Za-zА-Яа-я0-9]+")


def print_header():
    """Выводит заголовок приложения"""
    print("=" * 70)
    print(" " * 15 + "MAPREDUCE TEXT ANALYSIS ENGINE")
    print("=" * 70)
    print()


def get_text_files(directory):
    """Получает список текстовых файлов в директории"""
    if not os.path.exists(directory):
        return []
    
    # Ищем все .txt файлы
    pattern = os.path.join(directory, "*.txt")
    files = glob.glob(pattern)
    return sorted(files)


def analyze_documents(directory):
    """Анализирует документы в директории и возвращает статистику"""
    files = get_text_files(directory)
    
    if not files:
        return None, []
    
    stats = {
        'total_files': len(files),
        'files': []
    }
    
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                words = WORD_RE.findall(content.lower())
                word_count = len(words)
                unique_words = len(set(words))
                
                # Определяем язык (простая эвристика)
                russian_chars = sum(1 for c in content if 'а' <= c.lower() <= 'я')
                english_chars = sum(1 for c in content if 'a' <= c.lower() <= 'z')
                language = "Русский" if russian_chars > english_chars else "Английский"
                
                stats['files'].append({
                    'filename': filename,
                    'path': filepath,
                    'word_count': word_count,
                    'unique_words': unique_words,
                    'language': language,
                    'size': len(content)
                })
        except Exception as e:
            print(f"Ошибка при чтении {filename}: {e}", file=sys.stderr)
    
    return stats, files


def display_statistics(stats):
    """Отображает статистику по документам"""
    if not stats:
        print("❌ Статистика недоступна")
        return
    
    print("=" * 70)
    print(" " * 20 + "СТАТИСТИКА ПО ДОКУМЕНТАМ")
    print("=" * 70)
    print()
    print(f"📁 Общее количество документов: {stats['total_files']}")
    print()
    
    if stats['files']:
        print("📄 Детальная информация по документам:")
        print("-" * 70)
        print(f"{'№':<4} {'Файл':<25} {'Слов':<8} {'Уникальных':<12} {'Язык':<10}")
        print("-" * 70)
        
        for idx, file_info in enumerate(stats['files'], 1):
            print(f"{idx:<4} {file_info['filename']:<25} "
                  f"{file_info['word_count']:<8} {file_info['unique_words']:<12} "
                  f"{file_info['language']:<10}")
        
        print("-" * 70)
        print()
        
        # Общая статистика
        total_words = sum(f['word_count'] for f in stats['files'])
        total_unique = len(set(
            word for f in stats['files'] 
            for word in WORD_RE.findall(open(f['path'], 'r', encoding='utf-8').read().lower())
        ))
        
        print(f"📊 Общее количество слов во всех документах: {total_words}")
        print(f"📊 Общее количество уникальных слов: {total_unique}")
        print()


def compute_tf(directory):
    """Вычисляет TF для всех документов в директории"""
    files = get_text_files(directory)
    if not files:
        return False
    
    print("🔄 Вычисление Term Frequency (TF)...")
    
    # Формируем команду для tf_job.py
    cmd = ["python", "tf_job.py"] + files
    
    try:
        with open(TF_OUTPUT, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )
        print("✅ TF вычислен успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при вычислении TF: {e.stderr.decode('utf-8', errors='ignore')}")
        return False


def search_words(directory, query_words):
    """Выполняет поиск слов в документах"""
    # Проверяем наличие TF файла или вычисляем его
    if not os.path.exists(TF_OUTPUT) or os.path.getsize(TF_OUTPUT) == 0:
        if not compute_tf(directory):
            return None
    
    print(f"🔍 Поиск слов: {', '.join(query_words)}...")
    
    # Формируем запрос
    query = ' '.join(query_words)
    
    # Запускаем поиск
    cmd = ["python", "search_job.py", TF_OUTPUT, "--query", query]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            encoding='utf-8'
        )
        
        # Парсим результаты
        results = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            try:
                # Формат: ["filename", [score, ["word1", "word2"]]]
                data = json.loads(line)
                if isinstance(data, list) and len(data) == 2:
                    filename = data[0]
                    score_data = data[1]
                    if isinstance(score_data, list) and len(score_data) == 2:
                        score = score_data[0]
                        words = score_data[1]
                        results.append({
                            'filename': filename,
                            'score': score,
                            'words': words
                        })
            except json.JSONDecodeError:
                # Альтернативный формат с табуляцией
                if '\t' in line:
                    try:
                        key_str, value_str = line.split('\t', 1)
                        filename = json.loads(key_str)
                        value_data = json.loads(value_str)
                        if isinstance(value_data, list) and len(value_data) == 2:
                            score, words = value_data
                            results.append({
                                'filename': filename,
                                'score': score,
                                'words': words
                            })
                    except:
                        pass
        
        return results
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при поиске: {e.stderr.decode('utf-8', errors='ignore')}")
        return None


def get_word_counts_from_tf(query_words):
    """Извлекает точное количество вхождений слов из TF файла"""
    word_counts = defaultdict(lambda: defaultdict(int))
    
    if not os.path.exists(TF_OUTPUT):
        return word_counts
    
    # Нормализуем запрос для сравнения
    query_words_lower = [w.lower() for w in query_words]
    
    try:
        with open(TF_OUTPUT, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '\t' not in line:
                    continue
                
                try:
                    key_str, value_str = line.split('\t', 1)
                    key = json.loads(key_str)  # ["filename", "word"]
                    value = json.loads(value_str)  # count
                    
                    filename, word = key
                    count = int(value)
                    word_lower = word.lower()
                    
                    # Проверяем, есть ли это слово в запросе (с учетом регистра)
                    if word_lower in query_words_lower:
                        # Сохраняем оригинальное слово для отображения
                        word_counts[filename][word] += count
                except (json.JSONDecodeError, ValueError) as e:
                    continue
    except Exception as e:
        print(f"⚠️  Ошибка при чтении TF файла: {e}")
    
    return word_counts


def display_search_results(query_words, search_results, word_counts):
    """Отображает результаты поиска"""
    print()
    print("=" * 70)
    print(" " * 20 + "РЕЗУЛЬТАТЫ ПОИСКА")
    print("=" * 70)
    print()
    print(f"🔍 Искомые слова: {', '.join(query_words)}")
    print()
    
    if not search_results and not word_counts:
        print("❌ По запросу ничего не найдено")
        return
    
    # Объединяем результаты поиска и точные подсчеты
    all_docs = set()
    if search_results:
        all_docs.update(r['filename'] for r in search_results)
    if word_counts:
        all_docs.update(word_counts.keys())
    
    if not all_docs:
        print("❌ По запросу ничего не найдено")
        return
    
    # Сортируем документы по релевантности (если есть score) или по количеству вхождений
    doc_scores = {}
    for result in search_results:
        doc_scores[result['filename']] = result.get('score', 0)
    
    # Если нет score, сортируем по общему количеству вхождений
    def get_sort_key(filename):
        if filename in doc_scores and doc_scores[filename] > 0:
            return (1, doc_scores[filename])  # Сначала по наличию score
        elif filename in word_counts:
            total = sum(word_counts[filename].values())
            return (0, total)  # Затем по количеству вхождений
        return (0, 0)
    
    sorted_docs = sorted(
        all_docs,
        key=get_sort_key,
        reverse=True
    )
    
    print(f"📊 Найдено документов: {len(sorted_docs)}")
    print()
    print("-" * 70)
    
    for idx, filename in enumerate(sorted_docs, 1):
        print(f"\n📄 {idx}. Документ: {filename}")
        print("-" * 70)
        
        # Получаем найденные слова и их количество
        found_words_info = []
        
        # Из word_counts получаем точные количества
        if filename in word_counts:
            for word, count in word_counts[filename].items():
                found_words_info.append((word, count))
        
        # Если есть результаты поиска, добавляем информацию о score
        score = doc_scores.get(filename, 0)
        
        if found_words_info:
            print(f"   Найденные слова и количество вхождений:")
            total_occurrences = 0
            for word, count in sorted(found_words_info, key=lambda x: x[1], reverse=True):
                print(f"   • '{word}': {count} раз(а)")
                total_occurrences += count
            print(f"   📊 Всего вхождений: {total_occurrences}")
        else:
            # Если нет точных подсчетов, используем результаты поиска
            found_in_search = False
            for result in search_results:
                if result['filename'] == filename:
                    print(f"   Найденные слова: {', '.join(result['words'])}")
                    found_in_search = True
                    break
            if not found_in_search:
                print(f"   ⚠️  Слова найдены, но детальная информация недоступна")
        
        if score > 0:
            print(f"   ⭐ Релевантность: {score:.4f}")
    
    print()
    print("=" * 70)


def main():
    """Главная функция приложения"""
    print_header()
    
    # Шаг 1: Запрашиваем директорию
    print("📁 ВВОД ДИРЕКТОРИИ С ДОКУМЕНТАМИ")
    print("-" * 70)
    default_dir = "data"
    directory = input(f"Введите путь к директории с документами (по умолчанию: {default_dir}): ").strip()
    
    if not directory:
        directory = default_dir
    
    # Нормализуем путь
    directory = os.path.normpath(directory)
    
    if not os.path.exists(directory):
        print(f"❌ Директория '{directory}' не существует!")
        sys.exit(1)
    
    if not os.path.isdir(directory):
        print(f"❌ '{directory}' не является директорией!")
        sys.exit(1)
    
    print()
    
    # Шаг 2: Анализируем документы и показываем статистику
    stats, files = analyze_documents(directory)
    
    if not stats or not files:
        print(f"❌ В директории '{directory}' не найдено текстовых файлов (.txt)")
        sys.exit(1)
    
    display_statistics(stats)
    
    # Шаг 3: Запрашиваем слова для поиска
    print()
    print("=" * 70)
    print(" " * 20 + "ПОИСК ПО ДОКУМЕНТАМ")
    print("=" * 70)
    print()
    
    while True:
        query = input("Введите слова для поиска (через пробел) или 'exit' для выхода: ").strip()
        
        if query.lower() in ['exit', 'quit', 'выход', 'q']:
            print("\n👋 До свидания!")
            break
        
        if not query:
            print("⚠️  Пожалуйста, введите хотя бы одно слово")
            continue
        
        # Извлекаем слова из запроса
        query_words = [w for w in WORD_RE.findall(query) if w]
        
        if not query_words:
            print("⚠️  Не удалось извлечь слова из запроса")
            continue
        
        print()
        
        # Выполняем поиск
        search_results = search_words(directory, query_words)
        word_counts = get_word_counts_from_tf(query_words)
        
        # Отображаем результаты
        display_search_results(query_words, search_results or [], word_counts)
        
        print()
        print("-" * 70)
        print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем. До свидания!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

