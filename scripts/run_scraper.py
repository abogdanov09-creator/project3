"""
Запуск скрапера с интервалом
"""

import sys
import os
import argparse
import time
import schedule

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrap import SimpleScraper


def do_scrape(pages=3):
    print(f"\n[ЗАПУСК] Скрапинг {pages} страниц...")
    scraper = SimpleScraper()
    data = scraper.scrape_books(max_pages=pages)
    if data:
        scraper.save_to_csv()
        scraper.make_report()
        print(f"[OK] Собрано {len(data)} книг")
    else:
        print("[ERROR] Данные не собраны")


def continuous(interval, pages):
    print(f"[СТАРТ] Каждые {interval} часов, {pages} страниц")
    do_scrape(pages)
    schedule.every(interval).hours.do(do_scrape, pages)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[СТОП] Остановлено пользователем")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pages', '-p', type=int, default=3)
    p.add_argument('--interval', '-i', type=int, default=None)
    args = p.parse_args()

    if args.interval:
        continuous(args.interval, args.pages)
    else:
        do_scrape(args.pages)


if __name__ == "__main__":
    main()