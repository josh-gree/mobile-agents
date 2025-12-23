"""Example module for the art library."""


def hello(name: str = "World") -> str:
    """Return a greeting message.

    Args:
        name: The name to greet. Defaults to "World".

    Returns:
        A greeting string.

    Examples:
        >>> hello()
        'Hello, World!'
        >>> hello("Alice")
        'Hello, Alice!'
    """
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.

    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
    """
    return a + b
