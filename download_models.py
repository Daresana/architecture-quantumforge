from huggingface_hub import snapshot_download

from settings import (
    EMBEDDING_MODEL,
    EMBEDDING_FOLDER,
    EMBEDDING_REVISION,
    GENERATION_MODEL,
    GENERATION_REVISION,
    MODEL_DIR,
)


def download_models():
    models = [
        (EMBEDDING_FOLDER, EMBEDDING_MODEL, EMBEDDING_REVISION),
        ('generation', GENERATION_MODEL, GENERATION_REVISION),
    ]

    for folder, repository, revision in models:
        snapshot_download(
            repo_id=repository,
            revision=revision,
            local_dir=MODEL_DIR / folder,
            allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model', '*.md'],
            ignore_patterns=['onnx/*', 'openvino/*'],
            max_workers=2,
        )


if __name__ == '__main__':
    download_models()
