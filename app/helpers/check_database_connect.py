from fastapi_sqlalchemy import db


def check_database_connect():
    is_database_connect = True
    output = 'Connect Database is ok'
    try:
        with db():
            db.session.execute('SELECT 1')  # to check database we will execute raw query
    except Exception as e:
        output = str(e)
        is_database_connect = False

    return is_database_connect, output
