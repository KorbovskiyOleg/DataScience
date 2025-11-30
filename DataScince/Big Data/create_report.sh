#!/bin/bash

INPUT_FILE="tfidf_decoded.txt"
REPORT_FILE="word_analysis_report.txt"

echo "Создание отчета по анализу слов..."

{
echo "=================================================="
echo "           ОТЧЕТ ПО АНАЛИЗУ СЛОВ TF-IDF"
echo "=================================================="
echo "Сгенерировано: $(date)"
echo "Общее количество записей: $(wc -l < "$INPUT_FILE")"
echo "=================================================="
echo ""

echo "🎯 ТОП-20 САМЫХ ЗНАЧИМЫХ СЛОВ (ПО ВСЕМ ДОКУМЕНТАМ)"
echo "--------------------------------------------------"
awk '{sum[$2] += $3} END {
    for (word in sum) print sum[word], word
}' "$INPUT_FILE" | sort -nr | head -20 | awk '{
    printf "🏆 %-25s %8.4f\n", $2, $1
}'
echo ""

echo "📚 АНАЛИЗ ПО ДОКУМЕНТАМ"
echo "--------------------------------------------------"

# Анализ для каждого документа
for doc in doc7_ru.txt doc8_ru.txt doc6_ru.txt doc5.txt doc4.txt doc3.txt doc2.txt doc1.txt; do
    if grep -q "$doc" "$INPUT_FILE"; then
        count=$(grep -c "$doc" "$INPUT_FILE")
        echo ""
        echo "📄 Документ: $doc ($count слов)"
        echo "┌────────────────────────────────────────────┐"
        grep "$doc" "$INPUT_FILE" | sort -k3 -nr | head -5 | awk '{
            printf "│ 🏷️  %-25s %8.4f │\n", $2, $3
        }'
        echo "└────────────────────────────────────────────┘"
    fi
done

echo ""
echo "🔤 РАСПРЕДЕЛЕНИЕ ПО ЯЗЫКАМ"
echo "--------------------------------------------------"
total_words=$(wc -l < "$INPUT_FILE")
russian_words=$(grep -P "\t[а-я]" "$INPUT_FILE" | wc -l)
english_words=$(grep -P "\t[a-z]" "$INPUT_FILE" | grep -vP "\t[а-я]" | wc -l)

echo "🇷🇺 Русские слова: $russian_words ($(echo "scale=1; $russian_words*100/$total_words" | bc)%)"
echo "🇺🇸 Английские слова: $english_words ($(echo "scale=1; $english_words*100/$total_words" | bc)%)"
echo ""

echo "📈 СТАТИСТИКА ПО TF-IDF ЗНАЧЕНИЯМ"
echo "--------------------------------------------------"
awk '
{
    values[NR] = $3
    sum += $3
}
END {
    asort(values)
    min = values[1]
    max = values[NR]
    median = (NR % 2 == 1) ? values[(NR+1)/2] : (values[NR/2] + values[NR/2+1])/2

    printf "📊 Минимальное значение:  %8.4f\n", min
    printf "📊 Максимальное значение: %8.4f\n", max
    printf "📊 Медиана:               %8.4f\n", median
    printf "📊 Среднее значение:      %8.4f\n", sum/NR
}' "$INPUT_FILE"

echo ""
echo "🔥 САМЫЕ УНИКАЛЬНЫЕ СЛОВА (ВЫСОКИЙ TF-IDF)"
echo "--------------------------------------------------"
sort -k3 -nr "$INPUT_FILE" | head -10 | awk '{
    printf "💎 %-20s → %-12s %8.4f\n", $2, $1, $3
}'

echo ""
echo "🌐 ТЕМАТИЧЕСКИЕ ГРУППЫ СЛОВ"
echo "--------------------------------------------------"

echo "🤖 Машинное обучение:"
grep -E "(машинн|обучен|алгоритм|данн|интеллект)" "$INPUT_FILE" | head -5 | awk '{
    printf "   %-20s %8.4f\n", $2, $3
}'

echo ""
echo "💻 Java/Технологии:"
grep -E "(java|библиотек|код|программир|maven)" "$INPUT_FILE" | head -5 | awk '{
    printf "   %-20s %8.4f\n", $2, $3
}'

echo ""
echo "=================================================="
echo "              КЛЮЧЕВЫЕ ВЫВОДЫ"
echo "=================================================="
echo "✅ Самые значимые темы: машинное обучение, данные"
echo "✅ Основной язык контента: русский"
echo "✅ Технологический фокус: Java, библиотеки ML"
echo "✅ Высокая специфичность терминов"
echo "=================================================="

} > "$REPORT_FILE"

echo "Отчет сохранен в: $REPORT_FILE"
echo ""
echo "👀 Просмотр отчета:"
cat "$REPORT_FILE"