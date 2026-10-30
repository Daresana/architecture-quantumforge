import json
import time
from pathlib import Path
from urllib.parse import quote

import requests
ROOT = Path(__file__).resolve().parent
PAGES = [
    'Luke Skywalker', 'Princess Leia', 'Han Solo', 'Chewbacca',
    'Darth Vader', 'Obi-Wan Kenobi', 'Yoda', 'Palpatine',
    'R2-D2', 'C-3PO', 'Boba Fett', 'Jabba the Hutt',
    'Lando Calrissian', 'Rey (Star Wars)', 'Finn (Star Wars)',
    'Poe Dameron', 'Kylo Ren', 'Supreme Leader Snoke',
    'Maz Kanata', 'Padmé Amidala', 'Qui-Gon Jinn', 'Mace Windu',
    'Count Dooku', 'General Grievous', 'Ahsoka Tano',
    'Captain Rex', 'Ezra Bridger', 'Sabine Wren',
    'Hera Syndulla', 'Grand Admiral Thrawn', 'Grand Moff Tarkin',
    'Mon Mothma',
]


def download_pages():
    folder = ROOT / 'raw_pages'
    folder.mkdir(exist_ok=True)
    sources = []
    saved = json.loads((ROOT / 'sources.json').read_text(encoding='utf-8'))
    russian_titles = {source['id']: source['title_ru'] for source in saved}
    session = requests.Session()
    session.headers['User-Agent'] = 'QuantumForgeStudy/1.0 (educational corpus)'

    for number, title in enumerate(PAGES, start=1):
        url = 'https://en.wikipedia.org/wiki/' + quote(title.replace(' ', '_'))
        path = folder / f'{number:02d}.html'

        if not path.exists():
            response = session.get(url, timeout=45)
            response.raise_for_status()
            path.write_text(response.text, encoding='utf-8')
            time.sleep(0.5)

        identifier = f'{number:02d}'
        sources.append({'id': identifier, 'title': title, 'title_ru': russian_titles[identifier], 'url': url})
        print(f'{number:02d} {russian_titles[identifier]}: HTML сохранён', flush=True)

    (ROOT / 'sources.json').write_text(
        json.dumps(sources, ensure_ascii=False, indent=4), encoding='utf-8'
    )


if __name__ == '__main__':
    download_pages()
