from llama_cpp import Llama
import config as cfg

modelPath = cfg.models["llama-2-7B"]
llm = Llama(model_path=modelPath)

prompt = "Q: Name the planets in the solar system? A:"

output = llm(prompt , max_tokens=256, stop=["Q:", "\n"], echo=True, n_gpu_layers=-1)
print(output)