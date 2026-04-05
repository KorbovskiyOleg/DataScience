import requests
from bs4 import BeautifulSoup
import json
import os

# Пути относительно корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_HTML = os.path.join(BASE_DIR, "data", "labirint_king.html")
OUTPUT_JSON = os.path.join(BASE_DIR, "source", "labirint_list.json")


def parse_list_page():
    with open(INPUT_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    books = []

    items = soup.find_all("div", class_="product-card")
    for item in items:
        title_tag = item.find("a", class_="product-card__name")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = "https://www.labirint.ru" + title_tag["href"]

        # Цена из data-price атрибута
        price = None
        if item.get("data-price"):
            try:
                price = int(item["data-price"])
            except:
                pass

        # Жанр из data-maingenre-name
        genre = item.get("data-maingenre-name")

        # Издательство из data-pubhouse
        publisher = item.get("data-pubhouse")

        books.append({
            "title": title,
            "url": url,
            "price": price,
            "currency": "RUB",
            "publisher": publisher,
            "author": None,
            "rating": None,
            "rating_count": None,
            "age_rating": None,
            "genre": genre,
            "subtitle": None
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

    print(f"Готово! Найдено книг: {len(books)}")


if __name__ == "__main__":
    parse_list_page()