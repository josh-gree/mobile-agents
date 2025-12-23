"""Tests for the example module."""

import pytest

from art.example import add, hello


def test_hello_default():
    """Test hello function with default argument."""
    assert hello() == "Hello, World!"


def test_hello_with_name():
    """Test hello function with custom name."""
    assert hello("Alice") == "Hello, Alice!"
    assert hello("Bob") == "Hello, Bob!"


def test_add():
    """Test add function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0


def test_add_negative():
    """Test add function with negative numbers."""
    assert add(-5, -3) == -8
    assert add(-10, 5) == -5


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 1, 2),
        (10, 20, 30),
        (100, 200, 300),
    ],
)
def test_add_parametrized(a, b, expected):
    """Test add function with parametrized inputs."""
    assert add(a, b) == expected
