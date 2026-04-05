import json
import os
import sys

# Добавляем текущую директорию в sys.path для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_labirint_book import parse_book_page

# Пути относительно корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE = os.path.join(BASE_DIR, "source", "labirint_list.json")

def enrich_data():
    with open(FILE, "r", encoding="utf-8") as f:
        books = json.load(f)

    updated = []

    for book in books:
        print(f"Обрабатываю: {book['title']}")

        info = parse_book_page(book["url"])

        # Обновляем только те поля, которые пришли со страницы книги
        # (некоторые уже могут быть заполнены из списка)
        if info["price"] is not None:
            book["price"] = info["price"]
        if info["currency"] is not None:
            book["currency"] = info["currency"]
        if info["subtitle"] is not None:
            book["subtitle"] = info["subtitle"]
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

        updated.append(book)

    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(updated, f, ensure_ascii=False, indent=4)

    print("ГОТОВО! Все записи обновлены.")


if __name__ == "__main__":
    enrich_data()