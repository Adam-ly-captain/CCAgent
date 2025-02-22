import pymysql
from cca.parse_config import get_db_config


def db_connect() -> pymysql.Connection:
    config_dict = get_db_config()
    conn = pymysql.connect(
        host=config_dict['host'],
        port=config_dict['port'],
        user=config_dict['user'],
        password=config_dict['password'],
        database=config_dict['database'],
    )
    
    return conn


def db_query(sql: str) -> list[tuple]:
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return result


def db_transactions(sql: str) -> bool:
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    
    return True


def insert_app_log(application_name: str) -> bool:
    if not application_name:
        return False
    
    sql = f"""
    INSERT INTO `app_operation_log` (`app_name`, `create_time`)
    VALUES ('{application_name}', CURRENT_TIMESTAMP)
    """
    return db_transactions(sql)


def query_last_app_log_id() -> int | None:
    sql = """
    SELECT `id`
    FROM `app_operation_log`
    ORDER BY `create_time` DESC
    LIMIT 1
    """
    result = db_query(sql)
    return result[0][0] if result else None


def query_last_app_name() -> str | None:
    sql = """
    SELECT `app_name`
    FROM `app_operation_log`
    ORDER BY `create_time` DESC
    LIMIT 1
    """
    result = db_query(sql)
    return result[0][0] if result else None
    


def batch_insert_ui_control(app_log_id: int = -1, coordinates: list[tuple] = None) -> bool:
    if app_log_id <= 0 or not coordinates:
        return False
    
    sql = f"""
    INSERT INTO ui_control (`id`, `app_log_id`, `left`, `top`, `right`, `bottom`, `label`)
    VALUES {','.join([f"({coord[0]} ,{app_log_id}, {coord[1]}, {coord[2]}, {coord[3]}, {coord[4]}, '{coord[5]}')" for coord in coordinates])}
    """
    return db_transactions(sql)


def query_ui_control(app_log_id: int = -1) -> list[tuple]:
    if app_log_id <= 0:
        return []
    
    sql = f"""
    SELECT `id`, `left`, `top`, `right`, `bottom`, `label`
    FROM ui_control
    WHERE `app_log_id` = {app_log_id}
    """
    return db_query(sql)


def query_ui_control_by_cid(app_log_id: int = -1, cid: int = -1) -> tuple:
    if app_log_id <= 0 or cid <= 0:
        return ()
    
    sql = f"""
    SELECT `id`, `left`, `top`, `right`, `bottom`, `label`
    FROM `ui_control`
    WHERE `app_log_id` = {app_log_id} AND `id` = {cid}
    """
    result = db_query(sql)
    return result[0] if result else ()


def delete_ui_control_by_app_log_id(app_log_id: int = -1) -> bool:
    if app_log_id <= 0:
        return False
    
    sql = f"""
    DELETE FROM `ui_control`
    WHERE `app_log_id` = {app_log_id}
    """
    return db_transactions(sql)
