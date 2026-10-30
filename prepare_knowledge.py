import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def prepare_knowledge():
    fragments = json.loads((ROOT / 'source_fragments.json').read_text(encoding='utf-8'))
    terms = json.loads((ROOT / 'terms_map.json').read_text(encoding='utf-8'))
    names = sorted(terms, key=len, reverse=True)
    pattern = re.compile(r'(?<!\w)(' + '|'.join(re.escape(name) for name in names) + r')(?!\w)')
    folder = ROOT / 'knowledge_base'
    folder.mkdir(exist_ok=True)

    # Читаем выбранные описания из русских текстовых копий источников.
    for fragment in fragments:
        source = ROOT / fragment['source_file']
        article = source.read_text(encoding='utf-8')
        if not 0 <= fragment['start'] < fragment['end'] <= len(article):
            raise ValueError(f"Некорректные границы фрагмента {fragment['id']}")
        text = article[fragment['start']:fragment['end']]
        if not re.search('[А-Яа-яЁё]', text):
            raise ValueError(f"Фрагмент {fragment['id']} должен быть на русском")

        title = pattern.sub(lambda match: terms[match.group()], fragment['title'])
        text = pattern.sub(lambda match: terms[match.group()], text)
        path = folder / (fragment['id'] + '.txt')
        path.write_text(title + '\n\n' + text + '\n', encoding='utf-8')
        print(f'{path.name}: {title}, слов: {len(text.split())}')


if __name__ == '__main__':
    prepare_knowledge()
