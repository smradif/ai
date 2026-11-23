def validate_name(name: str) -> bool:
    return isinstance(name, str) and name.isalpha() and len(name.strip()) > 1


def validate_age(age: str) -> bool:
    try:
        numeric_age = int(age.strip())
    except (AttributeError, ValueError):
        return False
    return 18 <= numeric_age <= 90