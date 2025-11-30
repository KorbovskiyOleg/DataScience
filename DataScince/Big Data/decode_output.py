# decode_output.py
import sys
import json

for line in sys.stdin:
    line = line.strip()
    if line:
        try:
            # Формат: JSON_KEY\tJSON_VALUE
            if '\t' in line:
                key_str, value_str = line.split('\t', 1)

                # Парсим ключ и значение отдельно
                filename = json.loads(key_str)
                word_data = json.loads(value_str)

                word = word_data[0]
                score = word_data[1]

                # Декодируем русские слова
                if '\\u' in word:
                    word_decoded = word.encode('latin-1').decode('unicode-escape')
                else:
                    word_decoded = word

                print(f'{filename}\t{word_decoded}\t{score}')
            else:
                # Если нет табуляции, пробуем как чистый JSON
                data = json.loads(line)
                filename = data[0]
                word_data = data[1]
                word = word_data[0]
                score = word_data[1]

                if '\\u' in word:
                    word_decoded = word.encode('latin-1').decode('unicode-escape')
                else:
                    word_decoded = word

                print(f'{filename}\t{word_decoded}\t{score}')

        except Exception as e:
            print(f"Error: {e} - Line: {line}")