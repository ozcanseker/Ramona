from functools import wraps

from jinja2 import pass_context


def generator_global_function(function):
    @pass_context
    @wraps(function)
    def wrapper(context, *args, **kwargs):
        return function(context, *args, **kwargs)

    wrapper._ramona_generator_global = True

    return wrapper