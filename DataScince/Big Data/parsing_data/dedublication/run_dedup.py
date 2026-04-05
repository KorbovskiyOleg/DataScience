"""
Запуск mrjob дедупликации (алгоритм Sorted Neighborhood).

Обход проблемы Windows multiprocessing: напрямую вызываем mapper и reducer
из MRJob класса, без subprocess.
"""
import json
import os
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMBINED_JSON = os.path.join(BASE_DIR, "combined", "all_books.json")
NDJSON_PATH = os.path.join(BASE_DIR, "combined", "all_books.ndjson")
DEDUP_SCRIPT = os.path.join(BASE_DIR, "dedublication", "mrjob_deduplicate.py")
OUTPUT_JSON = os.path.join(BASE_DIR, "duplicates", "result.json")


def step1_convert_to_ndjson():
    print("\n" + "=" * 60)
    print("ШАГ 1: Конвертация JSON → NDJSON")
    print("=" * 60)

    with open(COMBINED_JSON, "r", encoding="utf-8") as f:
        books = json.load(f)

    with open(NDJSON_PATH, "w", encoding="utf-8") as f:
        for book in books:
            f.write(json.dumps(book, ensure_ascii=False) + "\n")

    print(f"  Строк: {len(books)}")
    print(f"  Файл: {NDJSON_PATH}")


def step2_run_mrjob_emulated():
    """
    Эмулирует mrjob runner (Sorted Neighborhood).
    Mapper группирует по normalize_title, reducer — скользящее окно.
    """
    print("\n" + "=" * 60)
    print("ШАГ 2: mrjob Sorted Neighborhood (emulated)")
    print("=" * 60)

    sys.path.insert(0, os.path.dirname(DEDUP_SCRIPT))
    from mrjob_deduplicate import MRBookDeduplicate

    job = MRBookDeduplicate()

    # === MAP PHASE: группируем по normalize_title ===
    print("  Map phase (группировка по normalize_title)...")
    mapper_outputs = defaultdict(list)

    with open(NDJSON_PATH, "r", encoding="utf-8") as f:
        line_count = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            for key, value in job.mapper(line_count, line):
                mapper_outputs[key].append(value)
            line_count += 1

    print(f"  Блоков (keys) после map: {len(mapper_outputs)}")
    for key, vals in sorted(mapper_outputs.items()):
        print(f"    '{key}': {len(vals)} книг")

    # === REDUCE PHASE: скользящее окно внутри каждого блока ===
    print("\n  Reduce phase (скользящее окно WINDOW=5)...")
    duplicates = []

    for key, values in mapper_outputs.items():
        for out_key, out_value in job.reducer(key, iter(values)):
            if out_key == "duplicate":
                duplicates.append(out_value)
                lab = out_value["book_labirint"]["title"]
                b24 = out_value["book_book24"]["title"]
                dist = out_value["levenshtein_distance"]
                print(f"    ДУБЛИКАТ: dist={dist} | block='{key}'")
                print(f"      Lab: '{lab}'")
                print(f"      B24: '{b24}'")

    print(f"\n  Найдено дубликатов: {len(duplicates)}")
    return duplicates


def step3_save_result(duplicates):
    print("\n" + "=" * 60)
    print("ШАГ 3: Сохранение в duplicates/result.json")
    print("=" * 60)

    result = {
        "algorithm": "Sorted Neighborhood",
        "window_size": 5,
        "levenshtein_threshold": 3,
        "total_duplicates": len(duplicates),
        "duplicates": duplicates
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  Сохранено: {len(duplicates)} дубликатов")
    print(f"  Файл: {OUTPUT_JSON}")


def main():
    print("\n" + "#" * 60)
    print("# ДУПЛИКАЦИЯ КНИГ — Sorted Neighborhood + mrjob")
    print("#" * 60)

    if not os.path.exists(COMBINED_JSON):
        print(f"\nОШИБКА: {COMBINED_JSON} не найден")
        print("Сначала запустите combine_sources.py")
        sys.exit(1)

    step1_convert_to_ndjson()
    duplicates = step2_run_mrjob_emulated()
    step3_save_result(duplicates)

    print("\n" + "#" * 60)
    print("# ГОТОВО!")
    print("#" * 60)


if __name__ == "__main__":
    main()
