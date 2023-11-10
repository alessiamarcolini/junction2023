from llama_cpp import Llama
import config as cfg

modelPath = cfg.models["llama-2-7B"]
llm = Llama(model_path=modelPath)
prompt = "Q: Name the planets in the solar system? A:"

for word in  llm.create_completion(prompt, max_tokens=256, stop=["Q:", "\n"], echo=True, stream=True):
    print(word)

a = 1