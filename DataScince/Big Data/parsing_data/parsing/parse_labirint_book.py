import requests
from bs4 import BeautifulSoup
import time
import re


def parse_book_page(url):
    time.sleep(0.5)  # чтобы не спамить сайт
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0"
    })
    soup = BeautifulSoup(response.text, "html.parser")

    # -----------------------------
    # Цена (из Schema.org разметки)
    # -----------------------------
    price = None
    price_meta = soup.find("meta", itemprop="price")
    if price_meta and price_meta.get("content"):
        try:
            price = int(price_meta["content"])
        except:
            pass

    # -----------------------------
    # Валюта
    # -----------------------------
    currency = "RUB"
    currency_meta = soup.find("meta", itemprop="priceCurrency")
    if currency_meta and currency_meta.get("content"):
        currency = currency_meta["content"]

    # -----------------------------
    # Подзаголовок (оригинальное название)
    # -----------------------------
    subtitle = None
    h2 = soup.find("h2", class_="_h2_5o36c_33")
    if h2:
        subtitle = h2.get_text(strip=True) or None

    # -----------------------------
    # Автор (из Schema.org brand)
    # -----------------------------
    author = None
    brand_block = soup.find(attrs={"itemprop": "brand"})
    if brand_block:
        author_meta = brand_block.find("meta", itemprop="author")
        if author_meta and author_meta.get("content"):
            author = author_meta["content"]

    # -----------------------------
    # Издательство (из Schema.org brand)
    # -----------------------------
    publisher = None
    if brand_block:
        name_meta = brand_block.find("meta", itemprop="name")
        if name_meta and name_meta.get("content"):
            publisher = name_meta["content"]

    # -----------------------------
    # Рейтинг
    # -----------------------------
    rating = None
    rating_meta = soup.find("meta", itemprop="ratingValue")
    if rating_meta and rating_meta.get("content"):
        try:
            rating = float(rating_meta["content"])
        except:
            pass

    # -----------------------------
    # Количество оценок
    # -----------------------------
    rating_count = None
    rating_count_meta = soup.find("meta", itemprop="ratingCount")
    if rating_count_meta and rating_count_meta.get("content"):
        try:
            rating_count = int(rating_count_meta["content"])
        except:
            pass

    # -----------------------------
    # Возрастной рейтинг
    # -----------------------------
    age_rating = None
    age_tag = soup.find("div", class_="_age_1i6do_40")
    if age_tag:
        age_rating = age_tag.get_text(strip=True) or None

    # -----------------------------
    # Жанр (из breadcrumbs)
    # -----------------------------
    genre = None
    breadcrumbs = soup.find_all(attrs={"itemprop": "itemListElement"})
    if len(breadcrumbs) >= 3:
        third_crumb = breadcrumbs[2]
        name_tag = third_crumb.find("span", itemprop="name")
        if name_tag:
            genre = name_tag.get_text(strip=True)

    return {
        "price": price,
        "currency": currency,
        "subtitle": subtitle,
        "author": author,
        "publisher": publisher,
        "rating": rating,
        "rating_count": rating_count,
        "age_rating": age_rating,
        "genre": genre
    }


if __name__ == "__main__":
    # тестовый запуск
    print(parse_book_page("https://www.labirint.ru/books/618897/"))