import re
import unicodedata


def normalize_title(title: str) -> str:
    """Нормализация названий книг:
    - нижний регистр
    - замена Ё → Е
    - удаление лишних пробелов и пунктуации (кроме дефисов в словах)
    - удаление подзаголовков после : и (
    - НОРМАЛИЗАЦИЯ КАВЫЧЕК «»"" → обычные
    """

    if not title:
        return ""

    title = title.lower()
    title = title.replace("ё", "е")

    # Нормализуем кавычки «»"" → пустота
    title = title.replace("\u00ab", "").replace("\u00bb", "")
    title = title.replace("\u201c", "").replace("\u201d", "")
    title = title.replace('"', '')

    # Убираем всё после : и ( (но НЕ после дефиса!)
    title = re.split(r"[:\(]", title)[0]

    # Убираем подзаголовки вида " - подзаголовок" и " — подзаголовок"
    title = re.split(r"\s[\-\u2014]\s", title)[0]

    # Убираем лишние пробелы
    title = " ".join(title.split())

    # Убираем пунктуацию (кроме дефиса внутри слов)
    title = re.sub(r"[^\w\s\-]", "", title)

    return title.strip()


def levenshtein(a: str, b: str) -> int:
    """Стандартный алгоритм Левенштейна."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a

    if len(b) == 0:
        return len(a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(
                min(
                    prev[j + 1] + 1,
                    curr[j] + 1,
                    prev[j] + (ca != cb)
                )
            )
        prev = curr

    return prev[-1]