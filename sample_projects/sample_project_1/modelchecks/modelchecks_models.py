
from ramona import {modelcheck, CheckResult}

@modelcheck(
        name="Model: check types",
        description="Check if types of models are one of the allowed ones"
)
def check_types(model):
    if model.type in ["table", "dag"]:
        return CheckResult.succes()
    else:
        return CheckResult.failure()