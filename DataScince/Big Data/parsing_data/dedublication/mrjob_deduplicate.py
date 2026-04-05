from mrjob.job import MRJob
from mrjob.step import MRStep
import json
from utils_normalize import normalize_title, levenshtein

# Размер скользящего окна (количество соседей для сравнения)
WINDOW = 5

# Порог расстояния Левенштейна для признания дубликатом
LEVENSHTEIN_THRESHOLD = 3


class MRBookDeduplicate(MRJob):
    """
    Дедупликация книг — алгоритм Sorted Neighborhood.

    Логика:
    1. mapper: группирует книги по normalize_title (блокировка)
    2. reducer: внутри каждой группы применяет скользящее окно (WINDOW)
       и сравнивает ТОЛЬКО跨-источниковые пары (Labirint ↔ Book24)
    3. Критерии дубликата:
       - Одинаковый автор (после нормализации)
       - Расстояние Левенштейна по оригинальному названию <= threshold
       - Одинаковое издательство
    """

    def mapper(self, _, line):
        """
        Sorted Neighborhood: ключ группировки — нормализованное название.
        Книги с одинаковым normalize_title попадут в один reducer.
        """
        book = json.loads(line)

        if not book.get("title") or not book.get("source"):
            return

        norm_title = normalize_title(book["title"])

        yield norm_title, book

    def reducer(self, norm_title, books):
        """
        Скользящее окно внутри блока с одинаковым norm_title.
        Сравнивает ТОЛЬКО Labirint ↔ Book24 пары.
        """
        books_list = list(books)

        # Разделяем по источникам
        lab_books = [b for b in books_list if b.get("source") == "Labirint"]
        b24_books = [b for b in books_list if b.get("source") == "Book24"]

        # Сортируем для детерминированности
        lab_books.sort(key=lambda b: b.get("title", ""))
        b24_books.sort(key=lambda b: b.get("title", ""))

        # Скользящее окно: проходим по каждой паре (lab, b24)
        # в пределах WINDOW соседей
        compared_pairs = set()

        for i, lab in enumerate(lab_books):
            # Определяем диапазон b24 книг для сравнения (скользящее окно)
            start = max(0, i - WINDOW // 2)
            end = min(len(b24_books), start + WINDOW)

            for j in range(start, end):
                b24 = b24_books[j]

                # Уникальный ключ пары
                pair_key = tuple(sorted([lab.get("url", ""), b24.get("url", "")]))
                if pair_key in compared_pairs:
                    continue
                compared_pairs.add(pair_key)

                # 1) Проверка автора
                author1 = self._normalize_author(lab.get("author"))
                author2 = self._normalize_author(b24.get("author"))

                if author1 and author2 and author1 != author2:
                    continue

                # 2) Levenshtein по ОРИГИНАЛЬНЫМ названиям (не нормализованным!)
                dist = levenshtein(lab["title"], b24["title"])

                if dist > LEVENSHTEIN_THRESHOLD:
                    continue

                # 3) Издательство
                pub1 = (lab.get("publisher") or "").strip().lower()
                pub2 = (b24.get("publisher") or "").strip().lower()

                if pub1 and pub2 and pub1 != pub2:
                    continue

                yield "duplicate", {
                    "book_labirint": lab,
                    "book_book24": b24,
                    "levenshtein_distance": dist,
                    "block_key": norm_title,
                    "author_match": author1 == author2 if (author1 and author2) else "unknown",
                    "publisher_match": pub1 == pub2 if (pub1 and pub2) else "unknown"
                }

    def _normalize_author(self, author):
        """Нормализация автора: 'Кинг Стивен' == 'Стивен Кинг'."""
        if not author:
            return ""
        author = author.strip().lower().replace("ё", "е")
        parts = sorted(author.split())
        return " ".join(parts)

    def steps(self):
        return [MRStep(mapper=self.mapper, reducer=self.reducer)]


if __name__ == "__main__":
    MRBookDeduplicate.run()