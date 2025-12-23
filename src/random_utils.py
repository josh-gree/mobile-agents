import random
import string


def generate_random_string(length: int) -> str:
    """
    Generate a random alphanumeric string of the given length.

    Args:
        length: The length of the random string to generate.

    Returns:
        A random string containing uppercase letters, lowercase letters, and digits.

    Example:
        >>> result = generate_random_string(10)
        >>> len(result)
        10
        >>> all(c in string.ascii_letters + string.digits for c in result)
        True
    """
    if length < 0:
        raise ValueError("Length must be non-negative")

    # Combine uppercase, lowercase letters and digits
    characters = string.ascii_letters + string.digits

    # Generate random string
    return ''.join(random.choice(characters) for _ in range(length))
