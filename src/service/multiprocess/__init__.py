import multiprocessing
import ollama

ollama_lock = multiprocessing.Lock()

def multiprocess_chat(*args, **kwargs):
    with ollama_lock:
        return ollama.chat(*args, **kwargs)
