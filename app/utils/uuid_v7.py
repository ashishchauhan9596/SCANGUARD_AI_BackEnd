import uuid6

def generate_uuid_v7() -> str:
    """Generates a time-ordered UUID v7."""
    return str(uuid6.uuid7())
