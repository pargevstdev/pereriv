# importing required Modules
from db import *


def insert_table(table, data):
    sql = f"insert into {table} ({','.join(key for key in data.keys())}) values ({','.join('%s' for key in data.keys())})"
    values = tuple(data.values())
    return insert(sql, values)


def get_administrator(email, password):
    return get_row("users", {"email": email, "password": password, "group_id": 1})


def update_row(table_name, entity):
    return update_to(table_name, entity)


def insert_into_many(table_name, entity: list, insert_ignore=False, which_db="mysql_piiprotect"):
    pk_field_name = "id"
    parameter_placeholder = "%s"
    keys = [key for key in entity[0].keys() if key != pk_field_name]
    values = [tuple([value for key, value in val.items() if key != pk_field_name]) for val in entity]
    ignore = 'ignore' if insert_ignore else ''
    sql = f"insert {ignore} into {table_name} ({','.join(keys)}) values ({','.join(parameter_placeholder for key in keys)})"
    return insert_many(sql, values, which_db)


def insert_ignore(table_name, entity):
    return insert_into(table_name, entity, insert_ignore=True)


def get_row(table_name, fields_values):
    rows = fetch_row(table_name, fields_values)
    return rows[0] if rows is not None else None


def get_data(table_name, field_values):
    rows = fetch_row(table_name, field_values)
    return rows if rows else []


def get_rows(sql, values):
    rows = fetch_or_none(sql, values)
    return rows if rows is not None else []


def delete_row(table_name, field_name, field_value):
    return delete_from(table_name, field_name, field_value)


def get_data(table, fields_values, which_fields=None):
    return fetch_row(table, fields_values, which_fields) or []


def get_data_where_not_in(table, where_column, where_in, which_fields=None, additional_condition=None):
    sql = f"""
        SELECT {which_fields or '*'} FROM {table} WHERE {where_column} not in ( {', '.join("%s" for v in where_in)} ) { ('AND ' + ' AND '.join(f'{key}=%s' for key in additional_condition.keys()) if additional_condition else "")}
    """
    values = [v for v in where_in]
    if additional_condition:
        values += list(additional_condition.values())
    return fetch_or_none(sql, tuple(values)) or []
