import os
import re
from dataclasses import dataclass


EXPRESSION_REGEX = re.compile(
    r'(?P<unpack>\.\.\.)?'
    r'(?P<type>\w+)'
    r'\('
    r'\s*'
    r'(?:'
        r'"(?P<name>[^"]+)"'
    r')?'
    r'\s*'
    r'\)'
)


@dataclass(frozen=True)
class ResolveContext:
    globals: dict
    parent: dict | None = None
    current_key: str | None = None
    parent_dict: dict | None = None
    parent_yaml: dict | None = None


# ============================================================
# Main resolver
# ============================================================

def resolve(object_to_resolve, context: ResolveContext):
    """
    Resolve any object recursively.
    """

    if isinstance(object_to_resolve, dict):
        result = {}

        for key, value in object_to_resolve.items():
            result[key] = resolve(
                value,
                ResolveContext(
                    globals=context.globals,
                    parent=object_to_resolve,
                    parent_dict=context.parent,
                    current_key=key,
                )
            )

        return result

    if isinstance(object_to_resolve, list):
        result = []

        for item in object_to_resolve:
            resolved = resolve(item, context)

            # ...globals("list")
            if ( isinstance(item, str) and item.startswith("...") and isinstance(resolved, list)):
                result.extend(resolved)
            else:
                result.append(resolved)

        return result


    if isinstance(object_to_resolve, str):
        return resolve_expression(object_to_resolve, context)

    return object_to_resolve


# ============================================================
# Expression resolver
# ============================================================

def resolve_expression(value: str, context: ResolveContext):
    value = value.strip()
    match = EXPRESSION_REGEX.match(value)

    # Check if has an unpack 
    if match and match.group("unpack"):
       return resolve_match(match, context)
    

    # These is a loop here because it is not guarenteed that the solved string also has references
    # So keep resolving until string does not change anymore
    previous = None
    while previous != value:
        previous = value
        value = EXPRESSION_REGEX.sub(
            lambda match: replace(match, context),
            value
        )

    # Split on the +
    # Strip all the "
    # join together
    return "".join(
        part.strip().strip('"')
        for part in value.split("+")
    )


def replace(match, context: ResolveContext):

    result = resolve_match(match, context)

    if not isinstance(result, str):

        raise TypeError(
            f'{match.group("type")}("{match.group("name")}") '
            "cannot be used inside a string expression"
        )

    return f'"{result}"'


def resolve_match(match, context: ResolveContext):
    resolver = RESOLVERS.get(match.group("type"))

    if resolver is None:
        raise ValueError(f'Unknown resolver "{match.group("type")}"')

    return resolver(match.group("name"), context)


# ============================================================
# Individual resolvers
# ============================================================

def resolve_globals(name: str, context: ResolveContext):
    if name not in context.globals:
        raise KeyError( f'Global "{name}" does not exist')

    value = context.globals[name]

    return value


def resolve_parent_yaml(name: str, context: ResolveContext):
    if name not in context.parent_yaml:
        raise KeyError( f'Parent yaml "{name}" does not exist')

    key = name or context.current_key

    if key not in context.parent:
        raise KeyError(f'Parent yaml does not contain "{key}"')

    return context.parent_yaml[key]


def resolve_parent(name: str | None,context: ResolveContext ):
    if context.parent is None:
        raise ValueError("No parent available")

    key = name or context.current_key

    if key not in context.parent:
        raise KeyError(f'Parent does not contain "{key}"')

    return context.parent_dict[key]


def resolve_env(name: str,context: ResolveContext):
    if name not in os.environ:
        raise KeyError(f'Environment variable "{name}" does not exist')
    
    return os.environ[name]


# ============================================================
# Resolver registry
# ============================================================

RESOLVERS = {
    "globals": resolve_globals,
    "env": resolve_env,
    "parent": resolve_parent,
    "parent_yaml": resolve_parent_yaml
}