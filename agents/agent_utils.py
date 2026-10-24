import os
import time
from langchain_groq import ChatGroq
from graph.helper_functions.logger import get_logger

class RateLimitedLLM:
    def __init__(self, llm, min_delay=1.0):
        self.llm = llm
        self.min_delay = min_delay
        self.last_call = 0

    def invoke(self, messages, **kwargs):
        current_time = time.time()
        elapsed = current_time - self.last_call
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)

        try:
            result = self.llm.invoke(messages, **kwargs)
            self.last_call = time.time()
            return result
        except Exception as e:
            if "rate limit" in str(e).lower():
                logger = get_logger()
                logger.warning(f"Rate limit hit, waiting 30s: {e}")
                time.sleep(30)
                return self.llm.invoke(messages, **kwargs)
            raise

LARGE_MODEL = os.getenv("GROQ_LARGE_MODEL", "openai/gpt-oss-120b")
FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")

LLMS = {
    'researcher': RateLimitedLLM(ChatGroq(model=FAST_MODEL, temperature=0.1, max_tokens=1500), min_delay=1.5),
    'drafter': RateLimitedLLM(ChatGroq(model=LARGE_MODEL, temperature=0.3, max_tokens=2500), min_delay=1.5),
    'summarizer': RateLimitedLLM(ChatGroq(model=FAST_MODEL, temperature=0.0, max_tokens=1000), min_delay=1.0),
    'verifier': RateLimitedLLM(ChatGroq(model=FAST_MODEL, temperature=0.0, max_tokens=800), min_delay=1.0),
    'enhancer': RateLimitedLLM(ChatGroq(model=LARGE_MODEL, temperature=0.3, max_tokens=2500), min_delay=1.5)
}