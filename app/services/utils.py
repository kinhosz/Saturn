import uuid

def list_to_str(l):
    return ", ".join(map(str, l))

def generate_numeric_uuid():
    unique_id = uuid.uuid4()

    numeric_id = int(unique_id.int % (10 ** 15))
    return numeric_id
