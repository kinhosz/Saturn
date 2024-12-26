def compact(hash):
    compacted_hash = {}
    for k, v in hash.items():
        if not v:
            continue
        if isinstance(v, dict):
            v = compact(v)
        compacted_hash[k] = v
    return compacted_hash
