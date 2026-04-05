import json
import os
import sys

# Добавляем текущую директорию в sys.path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_book24_book import parse_book_page

# Пути относительно корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(BASE_DIR, "source", "book24_list.json")


def enrich_data():
    with open(FILE, "r", encoding="utf-8") as f:
        books = json.load(f)

    updated = []

    for book in books:
        print(f"Обрабатываю: {book['title']}")

        info = parse_book_page(book["url"])

        # Обновляем только те поля, которые пришли со страницы книги
        if info["price"] is not None:
            book["price"] = info["price"]
        if info["currency"] is not None:
            book["currency"] = info["currency"]
        if info["author"] is not None:
            book["author"] = info["author"]
        if info["publisher"] is not None:
            book["publisher"] = info["publisher"]
        if info["rating"] is not None:
            book["rating"] = info["rating"]
        if info["rating_count"] is not None:
            book["rating_count"] = info["rating_count"]
        if info["age_rating"] is not None:
            book["age_rating"] = info["age_rating"]
        if info["genre"] is not None:
            book["genre"] = info["genre"]
        if info["pages"] is not None:
            book["pages"] = info["pages"]
        if info["binding"] is not None:
            book["binding"] = info["binding"]
        if info["paper"] is not None:
            book["paper"] = info["paper"]
        if info["format"] is not None:
            book["format"] = info["format"]
        if info["series"] is not None:
            book["series"] = info["series"]
        if info["sold_count"] is not None:
            book["sold_count"] = info["sold_count"]

        updated.append(book)

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=4)

    print("ГОТОВО! Все записи обновлены.")


if __name__ == "__main__":
    enrich_data()
