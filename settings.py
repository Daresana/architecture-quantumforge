import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODEL_DIR = Path(os.environ.get('MODEL_DIR', ROOT / 'models'))
INDEX_DIR = Path(os.environ.get('INDEX_DIR', ROOT / 'index'))
EMBEDDING_MODEL = 'intfloat/multilingual-e5-small'
EMBEDDING_REVISION = '614241f622f53c4eeff9890bdc4f31cfecc418b3'
EMBEDDING_FOLDER = 'embedding-ru'
GENERATION_MODEL = 'Qwen/Qwen2.5-1.5B-Instruct'
GENERATION_REVISION = '989aa7980e4cf806f80c7fef2b1adb7bc71aa306'
TOP_K = 3
MIN_SCORE = 0.82
UNKNOWN = 'Я не знаю. В базе знаний нет подтверждённого ответа.'

REASONS = {
    'generated': 'Ответ сформирован по найденному контексту',
    'no_context': 'Подходящий контекст не найден',
    'blocked_query': 'Запрос заблокирован до генерации',
    'blocked_output': 'Ответ заблокирован проверкой секретов',
    'invalid_citations': 'Ответ отклонён из-за неверных ссылок',
}
