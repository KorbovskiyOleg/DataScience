# Сравнение книг Стивена Кинга — Labirint vs Book24

Проект для сравнения информации о книгах из двух книжных интернет-магазинов: **Labirint** и **Book24**.

Цель — спарсить данные, привести к единой схеме, объединить и найти дубликаты (одни и те же книги в разных магазинах) с помощью **MapReduce** (библиотека `mrjob`).

---

## 📁 Структура проекта

```
HW0_Book_Comparison/
├── data/                          # Исходные HTML-страницы
│   ├── labirint_king.html         # Список книг с Labirint
│   └── book24_king.html           # Список книг с Book24
│
├── parsing/                       # ЭТАП 1: Парсинг
│   ├── parse_labirint_list.py     # Парсинг списка Labirint
│   ├── parse_book24_list.py       # Парсинг списка Book24
│   ├── parse_labirint_book.py     # Парсинг страницы одной книги Labirint
│   ├── parse_book24_book.py       # Парсинг страницы одной книги Book24
│   ├── enrich_labirint_data.py    # Обогащение данных Labirint
│   └── enrich_book24_data.py      # Обогащение данных Book24
│
├── source/                        # Схема источников
│   ├── labirint_list.json         # Данные Labirint (сырые)
│   └── book24_list.json           # Данные Book24 (сырые)
│
├── transform/                     # ЭТАП 2: Трансформация
│   ├── transform_labirint.py      # → целевая схема Labirint
│   └── transform_book24.py        # → целевая схема Book24
│
├── target/                        # Преобразованные данные
│   ├── labirint_target.json       # Labirint в целевой схеме
│   └── book24_target.json         # Book24 в целевой схеме
│
├── combined/                      # ЭТАП 3: Объединение
│   ├── all_books.json             # Все книги (JSON)
│   └── all_books.ndjson           # Все книги (NDJSON — вход для mrjob)
│
├── dedublication/                 # ЭТАП 4: Дедупликация (MapReduce)
│   ├── utils_normalize.py         # Утилиты нормализации + Levenshtein
│   ├── mrjob_deduplicate.py       # MapReduce job (Sorted Neighborhood)
│   ├── run_dedup.py               # Скрипт запуска всего пайплайна
│   └── postprocess_output.py      # Постобработка mrjob → JSON
│
├── duplicates/                    # Результат дедупликации
│   └── result.json                # Найденные дубликаты
│
├── requirements.txt
└── README.md
```

---

## 🚀 Установка и запуск

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Полный пайплайн (все этапы)

```bash
# Этап 1: Парсинг HTML → JSON
python parsing/parse_labirint_list.py
python parsing/parse_book24_list.py

# Этап 1b: Обогащение (переход по ссылкам каждой книги)
python parsing/enrich_labirint_data.py
python parsing/enrich_book24_data.py

# Этап 2: Трансформация → целевая схема
python transform/transform_labirint.py
python transform/transform_book24.py

# Этап 3: Объединение
python dedublication/combine_sources.py

# Этап 4: Дедупликация (Sorted Neighborhood + mrjob)
python dedublication/run_dedup.py
```

### 3. Только дедупликация (если данные уже есть)

```bash
python dedublication/run_dedup.py
```

Скрипт автоматически:
1. Конвертирует `combined/all_books.json` → `combined/all_books.ndjson`
2. Запускает `mrjob_deduplicate.py` (эмуляция local runner)
3. Сохраняет результат в `duplicates/result.json`

---

## 🧠 Алгоритм дедупликации: Sorted Neighborhood + MapReduce

### Общая идея

Алгоритм **Sorted Neighborhood** решает проблему квадратичной сложности попарного сравнения (O(n²)) за счёт **блокировки** — книги с похожими названиями группируются, а сравниваются только внутри небольших групп.

### Схема работы MapReduce

```
┌─────────────────────────────────────────────────────────────┐
│                     ВХОДНЫЕ ДАННЫЕ                           │
│   all_books.ndjson (90 книг: 60 Labirint + 30 Book24)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  MAPPER (фаза группировки / Blocking)                       │
│                                                             │
│  for line in input:                                         │
│      book = json.loads(line)                                │
│      norm_title = normalize_title(book["title"])            │
│      yield norm_title, book                                 │
│                                                             │
│  ┌──────────────────────────────────────────────┐           │
│  │ normalize_title():                            │           │
│  │   1. lower() + замена Ё→Е                     │           │
│  │   2. Удаление кавычек «»""                    │           │
│  │   3. Отсечение подзаголовков после : и (      │           │
│  │   4. Удаление пунктуации (кроме дефисов)      │           │
│  │   5. Сжатие пробелов                          │           │
│  └──────────────────────────────────────────────┘           │
│                                                             │
│  Результат: 79 блоков (уникальных norm_title)               │
│    "мешок с костями" → [Lab:Мешок с костями, B24:Мешок...]  │
│    "сияние"          → [Lab:Сияние, B24:Сияние]             │
│    "112263"          → [Lab:11.22.63, B24:11/22/63]         │
│    ...                                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  REDUCER (фаза сравнения / Sorted Neighborhood Window)      │
│                                                             │
│  for each norm_title group:                                 │
│      lab_books = filter(source == "Labirint")               │
│      b24_books = filter(source == "Book24")                 │
│                                                             │
│      # Скользящее окно WINDOW=5                             │
│      for i, lab in enumerate(lab_books):                    │
│          window_start = max(0, i - WINDOW//2)              │
│          window_end   = min(len(b24), window_start+WINDOW)  │
│                                                             │
│          for j in range(window_start, window_end):          │
│              b24 = b24_books[j]                             │
│                                                             │
│              # Критерии дубликата:                          │
│              if author_match(lab, b24)          ✓           │
│              and levenshtein(title) <= 3        ✓           │
│              and publisher_match(lab, b24)      ✓           │
│                  → yield "duplicate", { ... }               │
│                                                             │
│  ┌──────────────────────────────────────────────┐           │
│  │ author_match():                               │           │
│  │   "Кинг Стивен" == "Стивен Кинг"              │           │
│  │   (слова сортируются → одинаковый результат)  │           │
│  └──────────────────────────────────────────────┘           │
│                                                             │
│  ┌──────────────────────────────────────────────┐           │
│  │ levenshtein():                                │           │
│  │   Расстояние по ОРИГИНАЛЬНЫМ названиям        │           │
│  │   (не нормализованным!):                      │           │
│  │   "Мешок с костями" vs "Мешок с костями" = 0  │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     РЕЗУЛЬТАТ                               │
│   duplicates/result.json — валидный JSON (UTF-8)            │
│   3 найденных дубликата (Labirint ↔ Book24)                 │
└─────────────────────────────────────────────────────────────┘
```

### Почему Sorted Neighborhood, а не полный перебор

| Метрика | Pairwise (All-vs-All) | Sorted Neighborhood |
|---------|----------------------|---------------------|
| Сложность | O(n × m) = 60 × 30 = **1800** пар | O(n × W) = **~15** сравнений |
| Блоков | 1 (все книги вместе) | **79** (по norm_title) |
| Лишних сравнений | 1785 (не дубликаты) | 12 (почти все — кандидаты) |
| Точность | Низкая (шум) | Высокая |


## 📊 Целевая схема данных

Все книги приводятся к единому формату:

```json
{
  "title": "Название книги",
  "url": "https://ссылка-на-книгу",
  "price": 999,
  "currency": "RUB",
  "publisher": "Издательство",
  "author": "Автор",
  "rating": 4.5,
  "rating_count": 100,
  "age_rating": "18+",
  "genre": "Жанр",
  "source": "Labirint" / "Book24"
}
```

---

## 📋 Результат дедупликации

Файл `duplicates/result.json`:

```json
{
  "algorithm": "Sorted Neighborhood",
  "window_size": 5,
  "levenshtein_threshold": 3,
  "total_duplicates": 3,
  "duplicates": [
    {
      "book_labirint": { ... },
      "book_book24": { ... },
      "levenshtein_distance": 0,
      "block_key": "мешок с костями",
      "author_match": true,
      "publisher_match": true
    }
  ]
}
```

### Найденные дубликаты

| # | Книга | Labirint | Book24 | Разница |
|---|-------|----------|--------|---------|
| 1 | Кто нашел, берет себе. Мистер Мерседес-2 | 1 011 ₽ | 442 ₽ | ×2.3 |
| 2 | Мешок с костями | 547 ₽ | 1 469 ₽ | ×2.7 |
| 3 | Сердца в Атлантиде | 964 ₽ | 1 369 ₽ | ×1.4 |

---

## 🛠 Технологии

- **Python 3.10**
- **BeautifulSoup4** — парсинг HTML
- **mrjob** — MapReduce фреймворк (локальный runner)
- **requests** — HTTP-запросы
- **Алгоритм Левенштейна** — нечёткое сравнение строк
- **Sorted Neighborhood** — эффективная блокировка при дедупликации
