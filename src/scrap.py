"""
Скрапер для books.toscrape.com
Запуск: python src/scrap.py
"""

import time
import csv
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt


class SimpleScraper:
    def __init__(self):
        self.products = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_books(self, max_pages=3):
        products = []

        for page in range(1, max_pages + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            print(f"[СТРАНИЦА] {page}: {url}")

            try:
                response = self.session.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                books = soup.find_all('article', class_='product_pod')

                for book in books:
                    data = self._parse_book(book)
                    if data:
                        products.append(data)

                print(f"  Найдено: {len(books)} книг, всего: {len(products)}")
                time.sleep(1)

            except Exception as e:
                print(f"  Ошибка: {e}")

        self.products = products
        return products

    def _parse_book(self, book):
        try:
            title = book.find('h3').find('a').get('title', '')

            price_text = book.find('p', class_='price_color').text
            price = float(re.findall(r'[\d.]+', price_text)[0])

            rating_class = book.find('p', class_='star-rating').get('class')[1]
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating = rating_map.get(rating_class, 0)

            stock = book.find('p', class_='instock availability')
            availability = 'in_stock' if stock and 'In stock' in stock.text else 'unknown'

            return {
                'name': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'category': 'books',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except:
            return None

    def save_to_csv(self, filename="data/products.csv"):
        """Сохранение в CSV (папка data в корне)"""
        if not self.products:
            print("Нет данных для сохранения")
            return

        os.makedirs("data", exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['name', 'price', 'rating', 'availability', 'category', 'timestamp'])
            writer.writeheader()
            writer.writerows(self.products)

        print(f"Сохранено {len(self.products)} записей в {filename}")

    def make_report(self):
        """Создание отчёта и графика (папка data в корне)"""
        if not self.products:
            print("Нет данных для анализа")
            return

        df = pd.DataFrame(self.products)
        os.makedirs("data", exist_ok=True)

        # ===== ОТЧЁТ =====
        lines = []
        lines.append("=" * 60)
        lines.append("ОТЧЁТ ПО СКРАПИНГУ")
        lines.append("=" * 60)
        lines.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Всего книг: {len(df)}")
        lines.append(f"Средняя цена: {df['price'].mean():.2f} GBP")
        lines.append(f"Максимальная цена: {df['price'].max():.2f} GBP")
        lines.append(f"Минимальная цена: {df['price'].min():.2f} GBP")
        lines.append(f"Средний рейтинг: {df['rating'].mean():.2f}")
        lines.append("")

        lines.append("-" * 60)
        lines.append("ТОП-5 САМЫХ ДОРОГИХ КНИГ")
        lines.append("-" * 60)
        for i, row in df.nlargest(5, 'price').iterrows():
            lines.append(f"{i + 1}. {row['name'][:50]} - {row['price']:.2f} GBP (⭐{row['rating']})")

        lines.append("")
        lines.append("-" * 60)
        lines.append("ТОП-5 ЛУЧШИХ ПО РЕЙТИНГУ")
        lines.append("-" * 60)
        for i, row in df.nlargest(5, 'rating').iterrows():
            lines.append(f"{i + 1}. {row['name'][:50]} - ⭐{row['rating']} ({row['price']:.2f} GBP)")

        lines.append("")
        lines.append("=" * 60)
        lines.append("ВЫВОДЫ")
        lines.append("=" * 60)
        lines.append(f"Самая дорогая книга: {df.loc[df['price'].idxmax(), 'name'][:40]} ({df['price'].max():.2f} GBP)")
        lines.append(f"Самая дешёвая книга: {df.loc[df['price'].idxmin(), 'name'][:40]} ({df['price'].min():.2f} GBP)")
        lines.append(f"Всего проанализировано: {len(df)} книг")
        lines.append("=" * 60)

        with open("data/report.txt", "w", encoding='utf-8') as f:
            f.write("\n".join(lines))

        print("\n" + "\n".join(lines))
        print(f"\n[OK] Отчёт сохранён: data/report.txt")

        # ===== ГРАФИК =====
        plt.figure(figsize=(10, 6))
        plt.hist(df['price'], bins=15, edgecolor='black', alpha=0.7, color='steelblue')
        plt.axvline(df['price'].mean(), color='red', linestyle='--',
                    label=f'Средняя: {df["price"].mean():.2f} GBP')
        plt.xlabel('Цена (GBP)')
        plt.ylabel('Количество книг')
        plt.title('Распределение цен на книги')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('data/price_plot.png', dpi=150, bbox_inches='tight')
        plt.close()

        print(f"[OK] График сохранён: data/price_plot.png")


def main():
    print("\n" + "=" * 50)
    print("СКРАПЕР ЗАПУЩЕН")
    print("=" * 50)
    print("Источник: books.toscrape.com")
    print("Страниц: 3")
    print("=" * 50 + "\n")

    scraper = SimpleScraper()
    scraper.scrape_books(max_pages=3)
    scraper.save_to_csv()
    scraper.make_report()

    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 50)
    print(f"Собрано книг: {len(scraper.products)}")
    print(f"Данные: data/products.csv")
    print(f"Отчёт: data/report.txt")
    print(f"График: data/price_plot.png")
    print("=" * 50)
    print("\n[OK] СКРАПИНГ ЗАВЕРШЁН")


if __name__ == "__main__":
    main()