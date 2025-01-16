def _select(table, id, column):
    sql = f"""
SELECT {column}
FROM {table}
WHERE id = {id};
    """

    return sql

def _select_by(table, column, value):
    sql = f"""
SELECT id
FROM {table}
WHERE {column} = {value};
    """

    return sql

def _insert(table, values):
    sql = f"""
INSERT INTO {table} ({", ".join(map(str, values.keys()))})
VALUES ({", ".join(map(str, values.values()))})
RETURNING id;
    """

    return sql

def _update(table, id, values):
    body = ""
    for k, v in values.items():
        if body != '':
            body += ',\n'
        body += f"{k} = {v}"

    sql = f"""
UPDATE {table}
SET {body}
WHERE id = {id};
    """

    return sql

def _where(table, **kwargs):
    # Assuming temporaly that kwargs = { k: [] }
    body = ""
    for k, v in kwargs.items():
        prepared_vals = []
        for d_v in v:
            if isinstance(d_v, str):
                prepared_vals.append(f"'{d_v}'")
            else:
                prepared_vals.append(str(d_v))

        if body != '':
            body += "\n AND "

        vals_str = ", ".join(prepared_vals)
        body += f"{k} IN ({vals_str})"

    sql = f"""
SELECT id
FROM {table}
WHERE {body};
    """

    return sql
