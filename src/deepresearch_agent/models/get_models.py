from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager
from langchain_core.embeddings import Embeddings
from langchain_core.messages import AIMessageChunk


import os
import threading

from deepresearch_agent.config.settings import (
    TIKTOKEN_CACHE_DIR,
    MODEL_CACHE_DIR,
    OPENAI_EMBEDDING_CONFIG,
    OPENAI_LLM_CONFIG,
    RAG_EMBEDDING_PROVIDER,
    RAG_SENTENCE_TRANSFORMER_DEVICE,
    RAG_SENTENCE_TRANSFORMER_MODEL,
)
from deepresearch_agent.models.bailian_embeddings import (
    BailianOpenAIEmbeddings,
    is_bailian_compatible_url,
)
from deepresearch_agent.models.prefix_cache import extract_usage, is_current_run_cancelled, tracker
from deepresearch_agent.harness.errors import RunCancelled


# 设置 tiktoken 缓存目录，避免每次联网拉取
def setup_cache():
    TIKTOKEN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["TIKTOKEN_CACHE_DIR"] = str(TIKTOKEN_CACHE_DIR)


setup_cache()


class LocalSentenceTransformerEmbeddings(Embeddings):
    """LangChain embedding adapter backed by a shared local SentenceTransformer."""

    _models = {}
    _models_lock = threading.Lock()

    def __init__(self, *, model_name: str, cache_dir, device: str = "cpu"):
        self.model_name = model_name
        self.cache_dir = str(cache_dir)
        self.device = device

    def _model(self):
        cache_key = (self.model_name, self.cache_dir, self.device)
        with self._models_lock:
            if cache_key not in self._models:
                from sentence_transformers import SentenceTransformer

                self._models[cache_key] = SentenceTransformer(
                    self.model_name,
                    cache_folder=self.cache_dir,
                    device=self.device,
                )
            return self._models[cache_key]

    def embed_documents(self, texts):
        vectors = self._model().encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    def embed_query(self, text):
        return self.embed_documents([text])[0]


def get_embeddings_model():
    if RAG_EMBEDDING_PROVIDER == "sentence_transformer":
        return LocalSentenceTransformerEmbeddings(
            model_name=RAG_SENTENCE_TRANSFORMER_MODEL,
            cache_dir=MODEL_CACHE_DIR,
            device=RAG_SENTENCE_TRANSFORMER_DEVICE,
        )
    config = {k: v for k, v in OPENAI_EMBEDDING_CONFIG.items() if v}
    if is_bailian_compatible_url(config.get("base_url")):
        return BailianOpenAIEmbeddings(**config)
    return OpenAIEmbeddings(**config)


class PrefixAwareChatOpenAI(ChatOpenAI):
    """在 ChatOpenAI 基础上透传调用，并从响应 usage 中记录前缀缓存命中情况。

    前缀缓存由服务端（OpenAI/DeepSeek/vLLM 等兼容网关）自动完成，本类不做任何
    请求改写，只负责观测：把每次调用的 input/hit/miss token 记入全局与当前
    Run 的累计器，供统计 API 与 Run usage 展示。
    """

    def _record_usage(self, response) -> None:
        usage = extract_usage(response)
        if usage is not None:
            tracker.record(model=self.model_name or "", usage=usage)

    def invoke(self, *args, **kwargs):
        if is_current_run_cancelled():
            raise RunCancelled("Run 已请求取消")
        response = super().invoke(*args, **kwargs)
        self._record_usage(response)
        return response

    async def ainvoke(self, *args, **kwargs):
        if is_current_run_cancelled():
            raise RunCancelled("Run 已请求取消")
        response = await super().ainvoke(*args, **kwargs)
        self._record_usage(response)
        return response

    async def astream(self, *args, **kwargs):
        if is_current_run_cancelled():
            raise RunCancelled("Run 已请求取消")
        last_chunk = None
        async for chunk in super().astream(*args, **kwargs):
            if is_current_run_cancelled():
                raise RunCancelled("Run 已请求取消")
            if isinstance(chunk, AIMessageChunk):
                last_chunk = chunk
            yield chunk
        # 流式响应的 usage 挂在最后一个 chunk 上（langchain-openai 会聚合）
        if last_chunk is not None:
            self._record_usage(last_chunk)


def get_llm_model(*, model=None, temperature=None, max_tokens=None):
    config = {k: v for k, v in OPENAI_LLM_CONFIG.items() if v is not None and v != ""}
    if model:
        config["model"] = model
    if temperature is not None:
        config["temperature"] = temperature
    if max_tokens is not None:
        config["max_tokens"] = max_tokens
    return PrefixAwareChatOpenAI(**config)

def get_stream_llm_model():
    callback_handler = AsyncIteratorCallbackHandler()
    # 将回调handler放进AsyncCallbackManager中
    manager = AsyncCallbackManager(handlers=[callback_handler])

    config = {k: v for k, v in OPENAI_LLM_CONFIG.items() if v is not None and v != ""}
    config.update({"streaming": True, "callbacks": manager})
    return PrefixAwareChatOpenAI(**config)

def count_tokens(text):
    """简单通用的token计数"""
    if not text:
        return 0
    
    model_name = (OPENAI_LLM_CONFIG.get("model") or "").lower()
    
    # 如果是deepseek，使用transformers
    if 'deepseek' in model_name:
        try:
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-V3")
            return len(tokenizer.encode(text))
        except:
            pass
    
    # 如果是gpt，使用tiktoken
    if 'gpt' in model_name:
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except:
            pass
    
    # 备用方案：简单计算
    chinese = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    english = len(text) - chinese
    return chinese + english // 4

if __name__ == '__main__':
    # 测试llm
    llm = get_llm_model()
    print(llm.invoke("你好"))

    # 由于langchain版本问题，这个目前测试会报错
    # llm_stream = get_stream_llm_model()
    # print(llm_stream.invoke("你好"))

    # 测试embedding
    test_text = "你好，这是一个测试。"
    embeddings = get_embeddings_model()
    print(embeddings.embed_query(test_text))

    # 测试计数
    test_text = "Hello 你好世界"
    tokens = count_tokens(test_text)
    print(f"Token计数: '{test_text}' = {tokens} tokens")
