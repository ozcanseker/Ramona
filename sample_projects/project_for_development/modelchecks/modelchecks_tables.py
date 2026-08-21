from ramona.modelcheck import modelcheck, CheckResult, ModelCheckConfig

# Global config for model checks for this file
config = ModelCheckConfig(
    severity="error",
    conditions=[
        lambda model: "type" in model,
        lambda model: model["type"] == "table"
    ]
)

@modelcheck(
        name="Has columns"
)
def check_types(model):
    if "columns" in model:
        return CheckResult.success()

    return CheckResult.failure(
        "All tables require a columns key."
    )