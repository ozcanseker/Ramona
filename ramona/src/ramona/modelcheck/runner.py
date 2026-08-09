class CheckRunner:

    def __init__(self, registry):
        self.registry = registry

    def run(self, model):

        results = []

        for check in self.registry.get_checks():

            result = check.function(model)

            results.append({
                "check": check,
                "result": result,
            })

        return results