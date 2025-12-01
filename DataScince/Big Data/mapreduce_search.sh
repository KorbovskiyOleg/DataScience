#!/bin/bash
# search.sh

if [ $# -ne 2 ]; then
    echo "Использование: ./search.sh <директория> '<поисковый запрос>'"
    echo "Пример: ./search.sh data 'машинное обучение java'"
    exit 1
fi

DATA_DIR=$1
QUERY=$2
TF_OUT="tf_output.txt"

echo "🔍 ЗАПУСК ПОИСКОВОЙ СИСТЕМЫ"
echo "=========================================="
echo "Директория: $DATA_DIR"
echo "Запрос: $QUERY"
echo ""

# Проверяем, есть ли вычисленные TF данные
if [ ! -f "$TF_OUT" ] || [ ! -s "$TF_OUT" ]; then
    echo "📊 Вычисляем TF данные..."
    python tf_job.py ${DATA_DIR}/*.txt > "${TF_OUT}"
fi

# Запускаем поисковый job
echo "🔍 Выполняем поиск..."
python search_job.py "$TF_OUT" --query "$QUERY" | \
python -c "
import sys
import json

results = []
for line in sys.stdin:
    line = line.strip()
    if line:
        try:
            # Парсим JSON вывод: [\"filename\", [score, [\"word1\", \"word2\"]]]
            data = json.loads(line)
            if isinstance(data, list) and len(data) == 2:
                filename = data[0]
                score_data = data[1]
                if isinstance(score_data, list) and len(score_data) == 2:
                    score = score_data[0]
                    words = score_data[1]
                    results.append((score, filename, words))
        except:
            # Альтернативный формат
            if '\\t' in line:
                parts = line.split('\\t')
                if len(parts) == 2:
                    try:
                        key_str, value_str = parts
                        filename = json.loads(key_str)
                        value_data = json.loads(value_str)
                        if isinstance(value_data, list) and len(value_data) == 2:
                            score, words = value_data
                            results.append((score, filename, words))
                    except:
                        pass

# Сортируем по убыванию релевантности
results.sort(reverse=True)

if results:
    print('📊 РЕЗУЛЬТАТЫ ПОИСКА (отсортированы по релевантности):')
    print('==================================================')
    for i, (score, filename, words) in enumerate(results, 1):
        print(f'{i:2d}. {filename} (релевантность: {score:.4f})')
        print(f'    Найдены слова: {\", \".join(words)}')
        print()
else:
    print('❌ По запросу ничего не найдено')
"

echo "=========================================="