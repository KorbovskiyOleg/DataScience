import json
import os

# Пути относительно корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT = os.path.join(BASE_DIR, "source", "book24_list.json")
OUTPUT = os.path.join(BASE_DIR, "target", "book24_target.json")


def transform_book24():
    # Создаём папку target, если её нет
    os.makedirs("target", exist_ok=True)

    with open(INPUT, "r", encoding="utf-8") as f:
        books = json.load(f)

    target = []

    for b in books:
        item = {
            "title": b.get("title"),
            "url": b.get("url"),
            "price": b.get("price"),
            "currency": b.get("currency", "RUB"),
            "publisher": b.get("publisher"),
            "author": b.get("author"),
            "rating": b.get("rating"),
            "rating_count": b.get("rating_count"),
            "age_rating": b.get("age_rating"),
            "genre": b.get("genre"),
            "source": "Book24"
        }
        target.append(item)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(target, f, ensure_ascii=False, indent=4)

    print(f"Готово! Сохранено книг: {len(target)}")


if __name__ == "__main__":
    transform_book24()