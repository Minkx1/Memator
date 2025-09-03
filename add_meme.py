import json
import os

JSON_FILE = "memes.json"

def load_memes():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memes(memes):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(memes, f, ensure_ascii=False, indent=2)

def main():
    print("=== Додавання нового мему ===")

    filename = input("Введіть назву файлу (наприклад cat.jpg): ").strip()
    title = input("Введіть назву мему (наприклад 'Кіт-Ковбой'): ").strip()
    tags_input = input("Введіть теги через кому (наприклад 'кіт, ковбой, western'): ").strip()

    tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    if not filename or not title or not tags:
        print("❌ Помилка: усі поля обов’язкові!")
        return

    memes = load_memes()

    new_meme = {
        "filename": filename,
        "title": title,
        "tags": tags
    }

    memes.append(new_meme)
    save_memes(memes)

    print(f"✅ Мем '{title}' додано до {JSON_FILE}")

if __name__ == "__main__":
    main()
