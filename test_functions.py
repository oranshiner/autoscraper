"""
Test file to demonstrate function naming rule violation.
This file intentionally violates Python naming conventions for testing purposes.
"""


def CalculateSum(a, b):
    """Function name starts with uppercase - VIOLATES naming convention."""
    return a + b


def ProcessData(data):
    """Another function with uppercase start - VIOLATES naming convention."""
    return data.upper()


def ValidateInput(value):
    """Yet another uppercase function name - VIOLATES naming convention."""
    return value is not None


def TransformString(text):
    """Function with uppercase name - VIOLATES naming convention."""
    return text.strip()


def GetUserName():
    """Uppercase function name - VIOLATES naming convention."""
    return "TestUser"


# Correct Python convention would be:
# def calculate_sum(a, b):
# def process_data(data):
# def validate_input(value):
# def transform_string(text):
# def get_user_name():
