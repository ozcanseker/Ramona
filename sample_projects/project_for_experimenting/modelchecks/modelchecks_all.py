from ramona.modelcheck import modelcheck, CheckResult, ModelCheckConfig


# Global config for model checks for this file
config = ModelCheckConfig(
    severity="error"
)

@modelcheck(
        name="Check type keyword",
        description="Check if model has a type keyword."
)
def check_types(model):
    if "type" in model:
        return CheckResult.success()

    return CheckResult.failure(
        "All models require a type key."
    )


# Global config for model checks for this file
config = ModelCheckConfig(
    severity="error"
)

@modelcheck(
        name="Check id keyword",
        description="Check if model has an id keyword."
)
def has_id(model):
    if "id" in model:
        return CheckResult.success()

    return CheckResult.failure(
        "All models require an id."
    )