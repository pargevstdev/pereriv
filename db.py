# Importing MySql Modules and config Modules
from mysql.connector import MySQLConnection, Error
db_config = {'host':'127.0.0.1','database':'pereriv','user':'root','password':'root','port':'3306'}


# return Row(s) with a cetain criteria or None if  do/does not exist
def fetch_or_none(sql, values, which_db="pereriv"):
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, values)
        rows = cursor.fetchall()
        row_count = cursor.rowcount
        return None if row_count == 0 else rows
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


# Insert and return  the last inserted row identity or None
def insert(sql, values, which_db="pereriv"):
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql, values)
        last_rowid = None
        if cursor.lastrowid:
            last_rowid = cursor.lastrowid
        conn.commit()
        return last_rowid
    except Error as error:
        raise error
    finally:
        cursor.close()
        conn.close()


def insert_many(sql, values, which_db="pereriv"):
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.executemany(sql, values)
        conn.commit()
        return True
    except Error as error:
        raise error
    finally:
        cursor.close()
        conn.close()


# Update and return  effected row counts or None
def update(sql, values, which_db="pereriv"):
    # read database configuration
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount if cursor.rowcount > 0 else None
    except Error as error:
        raise error
    finally:
        cursor.close()
        conn.close()


# delete and return  effected row counts or None
def delete(sql, values, which_db="pereriv"):
    # read database configuration
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount if cursor.rowcount > 0 else None
    except Error as error:
        raise error
    finally:
        cursor.close()
        conn.close()


def update_to(table_name, entity, which_db="pereriv"):
    pk_field = "id"
    sql = f"update {table_name} set {','.join(key + '=%s' for key in entity.keys() if key != pk_field)} where {pk_field}=%s"
    values = tuple([value for key, value in entity.items() if key != pk_field]) + (entity[pk_field],)
    return update(sql, values, which_db)


def insert_into(table_name, entity, insert_ignore=False, which_db="pereriv"):
    pk_field_name = "id"
    parameter_placeholder = "%s"
    keys, values = [key for key in entity.keys() if key != pk_field_name], [value for key, value in entity.items() if
                                                                            key != pk_field_name]
    ignore = 'ignore' if insert_ignore else ''
    sql = f"insert {ignore} into {table_name} ({','.join(keys)}) values ({','.join(parameter_placeholder for key in keys)})"
    values = tuple(values)
    return insert(sql, values, which_db)


def insert_into_many(table_name, entity: list, insert_ignore=False, which_db="pereriv"):
    pk_field_name = "id"
    parameter_placeholder = "%s"
    keys = [key for key in entity[0].keys() if key != pk_field_name]
    values = [tuple([value for key, value in val.items() if key != pk_field_name]) for val in entity]
    ignore = 'ignore' if insert_ignore else ''
    sql = f"insert {ignore} into {table_name} ({','.join(keys)}) values ({','.join(parameter_placeholder for key in keys)})"
    return insert_many(sql, values, which_db)


def insert_raw(sql, which_db="pereriv"):
    return insert(sql, None, which_db)


def fetch_row(table_name, fields_values, which_fields=None, which_db="pereriv"):
    keys, values = fields_values.keys(), tuple(fields_values.values())
    sql = f"""select {','.join(which_fields) if which_fields is not None else '*'} from {table_name} 
    where {' and '.join(f'{key}=%s' for key in keys)}"""
    return fetch_or_none(sql, values, which_db)


def delete_from(table_name, field_name, field_value, which_db="pereriv"):
    sql = f"delete from {table_name} where {field_name} = %s"
    return delete(sql, (field_value,), which_db)


def fetch_all(table_name, which_fields=None, which_db="pereriv"):
    sql = f"select {','.join(which_fields) if which_fields is not None else '*'} from {table_name}"
    return fetch_or_none(sql, None, which_db)


def insert_many_update_dups(table_name,entities,which_db="pereriv"):
    pk_field_name = "id"
    parameter_placeholder = "%s"
    first_entity = entities[0]
    keys,values = [key for key in first_entity.keys() if key!=pk_field_name],[value for key, value in first_entity.items() if key != pk_field_name]
    sql = f"""insert into {table_name} ({','.join(keys)}) values ({','.join(parameter_placeholder for key in keys)}) ON DUPLICATE KEY UPDATE
    {','.join(f"{key}=Values({key})" for key in keys)}"""
    values = [tuple(list(d.values())) for d in entities]
    return insert_all(sql,values,which_db)


def insert_all(sql,values,which_db="pereriv"):
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.executemany(sql,values)
        last_rowid=None
        if cursor.lastrowid:
            last_rowid=cursor.lastrowid
        conn.commit()
        return last_rowid
    except Error as error:
        print(error)
        return error
    finally:
        cursor.close()
        conn.close()