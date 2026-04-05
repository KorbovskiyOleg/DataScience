from bs4 import BeautifulSoup
import json
import os

# Пути относительно корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_HTML = os.path.join(BASE_DIR, "data", "book24_king.html")
OUTPUT_JSON = os.path.join(BASE_DIR, "source", "book24_list.json")


def parse_list_page():
    with open(INPUT_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    books = []

    cards = soup.find_all("article", class_="product-card")
    for card in cards:
        # Название
        title_tag = card.find("a", class_="product-card__name")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        url = "https://book24.ru" + title_tag["href"]

        # Цена
        price = None
        if card.get("data-b24-price"):
            try:
                price = int(card["data-b24-price"])
            except:
                pass

        # Жанр
        genre = card.get("data-b24-category")

        # Издательство
        publisher = card.get("data-b24-brand")

        # Автор
        author_tag = card.find("a", class_="author-list__item")
        author = author_tag.get_text(strip=True) if author_tag else None

        books.append({
            "title": title,
            "url": url,
            "price": price,
            "currency": "RUB",
            "publisher": publisher,
            "author": author,
            "rating": None,
            "rating_count": None,
            "age_rating": None,
            "genre": genre,
            "pages": None,
            "binding": None,
            "paper": None,
            "format": None,
            "series": None,
            "sold_count": None
        })

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

    print(f"Готово! Найдено книг: {len(books)}")


if __name__ == "__main__":
    parse_list_page()
