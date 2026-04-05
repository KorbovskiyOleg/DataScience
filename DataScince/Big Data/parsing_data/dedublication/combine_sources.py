import json
import os

LAB = "../target/labirint_target.json"
BOOK24 = "../target/book24_target.json"
OUTPUT = "../combined/all_books.json"

os.makedirs("../combined", exist_ok=True)

def combine():
    with open(LAB, "r", encoding="utf-8") as f:
        lab = json.load(f)

    with open(BOOK24, "r", encoding="utf-8") as f:
        book24 = json.load(f)

    combined = lab + book24

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=4)

    print(f"Готово! Объединено записей: {len(combined)}")


if __name__ == "__main__":
    combine()