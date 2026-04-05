import requests
from bs4 import BeautifulSoup
import time
import re


def _find_dt(soup, pattern):
    """Находит dt элемент по regex паттерну в тексте span внутри dt."""
    for dt in soup.find_all("dt"):
        span = dt.find("span")
        if span:
            text = span.get_text(strip=True)
            if re.match(pattern, text):
                return dt
    return None


def _get_dd_value(dt):
    """Получает значение dd для данного dt."""
    dd = dt.find_next_sibling("dd")
    if dd:
        return dd.get_text(strip=True)
    return None


def parse_book_page(url):
    time.sleep(0.5)  # чтобы не спамить сайт
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0"
    })
    soup = BeautifulSoup(response.text, "html.parser")

    # -----------------------------
    # Цена (из Schema.org)
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
    # Подзаголовок (полное название) - НЕ ИСПОЛЬЗУЕМ
    # -----------------------------

    # -----------------------------
    # Автор (из dt/dd)
    # -----------------------------
    author = None
    author_meta = soup.find("meta", itemprop="author")
    if author_meta and author_meta.get("content"):
        author = author_meta["content"]
    else:
        dt_author = _find_dt(soup, r"^Автор:")
        if dt_author:
            author = _get_dd_value(dt_author)

    # -----------------------------
    # Издательство
    # -----------------------------
    publisher = None
    publisher_meta = soup.find("meta", itemprop="publisher")
    if publisher_meta and publisher_meta.get("content"):
        publisher = publisher_meta["content"]
    else:
        dt_publisher = _find_dt(soup, r"^Издательство:")
        if dt_publisher:
            publisher = _get_dd_value(dt_publisher)

    # -----------------------------
    # Рейтинг
    # -----------------------------
    rating = None
    rating_meta = soup.find("meta", itemprop="ratingValue")
    if rating_meta and rating_meta.get("content"):
        try:
            rating = float(rating_meta["content"].replace(",", "."))
        except:
            pass

    # -----------------------------
    # Количество отзывов
    # -----------------------------
    rating_count = None
    review_meta = soup.find("meta", itemprop="reviewCount")
    if review_meta and review_meta.get("content"):
        try:
            rating_count = int(review_meta["content"])
        except:
            pass

    # -----------------------------
    # Возрастной рейтинг
    # -----------------------------
    age_rating = None
    dt_age = _find_dt(soup, r"^Возрастное ограничение:")
    if dt_age:
        age_rating = _get_dd_value(dt_age)

    # -----------------------------
    # Жанр
    # -----------------------------
    genre = None
    genre_meta = soup.find("meta", itemprop="genre")
    if genre_meta and genre_meta.get("content"):
        genre = genre_meta["content"]
    else:
        dt_genre = _find_dt(soup, r"^Раздел:")
        if dt_genre:
            genre = _get_dd_value(dt_genre)

    # -----------------------------
    # ISBN - НЕ ИСПОЛЬЗУЕМ
    # -----------------------------

    # -----------------------------
    # Количество страниц
    # -----------------------------
    pages = None
    pages_meta = soup.find("meta", itemprop="numberOfPages")
    if pages_meta and pages_meta.get("content"):
        try:
            pages = int(pages_meta["content"])
        except:
            pass
    else:
        dt_pages = _find_dt(soup, r"^Количество страниц:")
        if dt_pages:
            pages_text = _get_dd_value(dt_pages)
            if pages_text:
                try:
                    pages = int("".join(filter(str.isdigit, pages_text)))
                except:
                    pass

    # -----------------------------
    # Переплёт
    # -----------------------------
    binding = None
    dt_binding = _find_dt(soup, r"^Переплет:")
    if dt_binding:
        binding = _get_dd_value(dt_binding)

    # -----------------------------
    # Бумага
    # -----------------------------
    paper = None
    dt_paper = _find_dt(soup, r"^Бумага:")
    if dt_paper:
        paper = _get_dd_value(dt_paper)

    # -----------------------------
    # Формат
    # -----------------------------
    format_val = None
    dt_format = _find_dt(soup, r"^Формат:")
    if dt_format:
        format_val = _get_dd_value(dt_format)

    # -----------------------------
    # Серия
    # -----------------------------
    series = None
    dt_series = _find_dt(soup, r"^Серия:")
    if dt_series:
        series = _get_dd_value(dt_series)

    # -----------------------------
    # Купили N раз
    # -----------------------------
    sold_count = None
    sold_text = soup.find(string=re.compile(r"Купили\s+(\d+)\s+раз"))
    if sold_text:
        match = re.search(r"Купили\s+(\d+)\s+раз", sold_text)
        if match:
            try:
                sold_count = int(match.group(1))
            except:
                pass

    return {
        "price": price,
        "currency": currency,
        "author": author,
        "publisher": publisher,
        "rating": rating,
        "rating_count": rating_count,
        "age_rating": age_rating,
        "genre": genre,
        "pages": pages,
        "binding": binding,
        "paper": paper,
        "format": format_val,
        "series": series,
        "sold_count": sold_count
    }


if __name__ == "__main__":
    # тестовый запуск
    result = parse_book_page("https://book24.ru/product/mesok-s-kostami-8798885/")
    for key, value in result.items():
        print(f"{key}: {value}")
