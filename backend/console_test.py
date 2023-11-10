from llama_module import LlamaModule
from model_handler import ConsoleModelHandler


def main():
    print("Starting app in console mode")
    module = LlamaModule()
    handler = ConsoleModelHandler()
    module.execute(handler)
    print("App finished")


main()
