from custom_types.orchestration_types import ExecutionReturn

class ModuleBase:
    def __init__(model_name: str):
        pass

    def execute(request: any) -> ExecutionReturn:
        pass
