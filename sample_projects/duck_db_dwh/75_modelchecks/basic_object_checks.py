from ramona.model.classes.RamonaProject import Object
from ramona.modelcheck import modelcheck, CheckResult, ModelCheckConfig


# Global config for model checks for this file
config = ModelCheckConfig(
    severity="error"
)

@modelcheck(
        name="Check id keyword",
        description="Check if object has an id keyword."
)
def has_id(object: Object):
    if "id" in object:
        return CheckResult.success()

    return CheckResult.failure(
        "All object require an id."
    )

@modelcheck(
        name="Check type keyword",
        description="Check if model has a type keyword."
)
def check_types(object: Object):
    if "type" in object:
        return CheckResult.success()

    return CheckResult.failure(
        "All models require a type key."
    )


