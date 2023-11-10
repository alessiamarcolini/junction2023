from model_handler import ConsoleModelHandler
import sys

def main():
    module_name = sys.argv[1]
    module_import = __import__(module_name, fromlist=["Module"])

    module = module_import.Module()

    print("Starting app in console mode")
    handler = ConsoleModelHandler()
    module.execute(handler)
    print("App finished")


main()
