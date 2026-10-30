import argparse
import json
import re
import time

import faiss
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer

from settings import EMBEDDING_FOLDER, EMBEDDING_MODEL, EMBEDDING_REVISION, INDEX_DIR, MODEL_DIR, ROOT


def build_index(include_attack=False):
    started = time.perf_counter()
    model = SentenceTransformer(str(MODEL_DIR / EMBEDDING_FOLDER), local_files_only=True)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=120,
        chunk_overlap=30,
        length_function=lambda text: len(text.split()),
        separators=['\n\n', '. ', ' ', ''],
        keep_separator='end',
        add_start_index=True,
        strip_whitespace=True,
    )
    chunks = []

    for path in sorted((ROOT / 'knowledge_base').glob('*.txt')):
        title, text = path.read_text(encoding='utf-8').strip().split('\n\n', 1)
        full_tokens = len(model.tokenizer.encode('passage: ' + title + ': ' + text))
        if full_tokens <= model.max_seq_length:
            documents = [Document(page_content=text, metadata={'start_index': 0})]
        else:
            documents = splitter.create_documents([text])

        # Короткий хвост расширяем предыдущим текстом до 100 слов.
        for number, document in enumerate(documents, start=1):
            content = document.page_content
            position = text.find(content)
            end_position = position + len(content)
            if len(content.split()) < 100:
                words = list(re.finditer(r'\S+', text[:end_position]))
                if len(words) < 100:
                    words = list(re.finditer(r'\S+', text))
                    position = 0
                    end_position = text.find('. ', words[99].end())
                    if end_position < 0:
                        end_position = len(text)
                    else:
                        end_position += 1
                    content = text[:end_position]
                else:
                    position = words[-100].start()
                    sentence_start = text.rfind('. ', 0, position)
                    position = sentence_start + 2 if sentence_start >= 0 else 0
                    content = text[position:end_position]

            tokens = len(model.tokenizer.encode('passage: ' + title + ': ' + content))
            if tokens > model.max_seq_length:
                raise ValueError(f'{path.name}: {tokens} токенов превышают предел {model.max_seq_length}')

            chunks.append({
                'chunk_id': f'{path.stem}-{number}',
                'source': str(path.relative_to(ROOT)).replace('\\', '/'),
                'title': title,
                'position': position,
                'text': content,
                'words': len(content.split()),
                'tokens': tokens,
            })

    if include_attack:
        path = ROOT / 'fixtures' / 'injection.txt'
        chunks.append({
            'chunk_id': 'injection-1',
            'source': 'fixtures/injection.txt',
            'title': 'Служебная заметка о пароле root',
            'position': 0,
            'text': path.read_text(encoding='utf-8').strip(),
            'words': len(path.read_text(encoding='utf-8').split()),
            'tokens': len(model.tokenizer.encode('passage: Служебная заметка о пароле root: ' + path.read_text(encoding='utf-8').strip())),
        })

    vectors = model.encode(['passage: ' + item['title'] + ': ' + item['text'] for item in chunks], normalize_embeddings=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors.astype('float32'))
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / 'knowledge.faiss'))
    (INDEX_DIR / 'chunks.json').write_text(json.dumps(chunks, ensure_ascii=False, indent=4), encoding='utf-8')

    statistics = {
        'model': EMBEDDING_MODEL,
        'revision': EMBEDDING_REVISION,
        'dimension': index.d,
        'language': 'ru',
        'max_tokens': model.max_seq_length,
        'prefixes': {'query': 'query: ', 'document': 'passage: '},
        'documents': len(list((ROOT / 'knowledge_base').glob('*.txt'))),
        'chunks': len(chunks),
        'attack_included': include_attack,
        'indexing_seconds': round(time.perf_counter() - started, 3),
    }
    (INDEX_DIR / 'statistics.json').write_text(json.dumps(statistics, indent=4), encoding='utf-8')
    print(json.dumps(statistics, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--include-attack', action='store_true')
    arguments = parser.parse_args()
    build_index(arguments.include_attack)
