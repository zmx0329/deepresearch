import numpy as np

from deepresearch_agent.models import get_models


class FakeSentenceTransformer:
    calls = []

    def __init__(self, model_name, *, cache_folder, device):
        self.calls.append((model_name, cache_folder, device))

    def encode(self, texts, **kwargs):
        assert kwargs["normalize_embeddings"] is True
        return np.asarray([[float(index), 1.0] for index, _ in enumerate(texts)])


def test_local_sentence_transformer_adapter_is_shared(monkeypatch, tmp_path):
    import sentence_transformers

    monkeypatch.setattr(sentence_transformers, "SentenceTransformer", FakeSentenceTransformer)
    get_models.LocalSentenceTransformerEmbeddings._models.clear()

    first = get_models.LocalSentenceTransformerEmbeddings(
        model_name="local-test-model", cache_dir=tmp_path, device="cpu"
    )
    second = get_models.LocalSentenceTransformerEmbeddings(
        model_name="local-test-model", cache_dir=tmp_path, device="cpu"
    )

    assert first.embed_query("query") == [0.0, 1.0]
    assert second.embed_documents(["a", "b"]) == [[0.0, 1.0], [1.0, 1.0]]
    assert len(FakeSentenceTransformer.calls) == 1


def test_get_embeddings_model_selects_local_provider(monkeypatch, tmp_path):
    monkeypatch.setattr(get_models, "RAG_EMBEDDING_PROVIDER", "sentence_transformer")
    monkeypatch.setattr(get_models, "RAG_SENTENCE_TRANSFORMER_MODEL", "local-test-model")
    monkeypatch.setattr(get_models, "RAG_SENTENCE_TRANSFORMER_DEVICE", "cpu")
    monkeypatch.setattr(get_models, "MODEL_CACHE_DIR", tmp_path)

    model = get_models.get_embeddings_model()

    assert isinstance(model, get_models.LocalSentenceTransformerEmbeddings)
    assert model.model_name == "local-test-model"
