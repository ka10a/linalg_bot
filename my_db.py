import sqlite3


def create_db():
    conn = sqlite3.connect('alg.db')
    cur = conn.cursor()
    query = '''
            CREATE TABLE IF NOT EXISTS History (
                chat_id INTEGER,
                request_type VARCHAR(30) NOT NULL,
                first_matrix VARCHAR(1000) NOT NULL,
                second_matrix VARCHAR(1000),
                answer VARCHAR(1000) NOT NULL,
                request_date VARCHAR(30),
                PRIMARY KEY (chat_id, request_date)
            )
            '''
    cur.execute(query)
    conn.commit()
    conn.close()


def insert_into_db(values_dict):
    conn = sqlite3.connect('alg.db')
    cur = conn.cursor()
    query = '''
            SELECT COUNT(*) FROM History
            WHERE chat_id={}
            '''
    cur.execute(query.format(values_dict['chat_id']))
    rows = cur.fetchall()

    if int(rows[0][0]) == 10:
        query10 = '''
                  DELETE FROM History
                  WHERE chat_id={} AND request_date=(
                  SELECT MIN(request_date) FROM History
                  WHERE chat_id={})
                  '''
        cur.execute(query10.format(
            values_dict['chat_id'],
            values_dict['chat_id']
        ))

    if values_dict['second_matrix'] == "NULL":
        query = '''
                INSERT INTO History (
                chat_id,
                request_type,
                first_matrix,
                second_matrix,
                answer,
                request_date) 
                VALUES (
                {},
                "{}",
                "{}",
                {},
                "{}",
                "{}"
                )
                '''.format(
            values_dict['chat_id'],
            values_dict['request_type'],
            values_dict['first_matrix'],
            values_dict['second_matrix'],
            values_dict['answer'],
            values_dict['request_date']
        )
    else:
        query = '''
                INSERT INTO History (
                chat_id,
                request_type,
                first_matrix,
                second_matrix,
                answer,
                request_date) 
                VALUES (
                {},
                "{}",
                "{}",
                "{}",
                "{}",
                "{}"
                )
                '''.format(
            values_dict['chat_id'],
            values_dict['request_type'],
            values_dict['first_matrix'],
            values_dict['second_matrix'],
            values_dict['answer'],
            values_dict['request_date']
        )

    cur.execute(query)
    conn.commit()
    conn.close()


def select_from_db(find_dict):
    conn = sqlite3.connect('alg.db')
    cur = conn.cursor()
    if find_dict['second_matrix'] == "NULL":
        query = '''
                        SELECT answer, request_date FROM History
                        WHERE
                        chat_id = {} AND
                        request_type = "{}" AND
                        first_matrix = "{}" AND
                        second_matrix IS NULL
                    '''.format(
            find_dict['chat_id'],
            find_dict['request_type'],
            find_dict['first_matrix']
        )
    else:
        query = '''SELECT answer, request_date FROM History
                    WHERE
                    chat_id = {} AND
                    request_type = "{}" AND
                    first_matrix = "{}" AND
                    second_matrix = "{}"
                    '''.format(
            find_dict['chat_id'],
            find_dict['request_type'],
            find_dict['first_matrix'],
            find_dict['second_matrix']
        )
    rows = cur.execute(query).fetchall()
    conn.close()
    return rows


def select_history(n, find_dict):
    conn = sqlite3.connect('alg.db')
    cur = conn.cursor()
    query = '''
            SELECT * FROM History
            WHERE chat_id = {}
            ORDER BY request_date DESC
            '''
    cur.execute(query.format(find_dict['chat_id']))
    rows = cur.fetchall()
    conn.close()
    return rows[:n]


def update_date(chat_id, old_date, new_date):
    conn = sqlite3.connect('alg.db')
    cur = conn.cursor()
    query = '''
            UPDATE History
            SET request_date="{}"
            WHERE
            chat_id = {} AND
            request_date = "{}"
            '''
    cur.execute(query.format(
        new_date,
        chat_id,
        old_date
    ))
    conn.commit()
    conn.close()


def select_all():
    conn = sqlite3.connect('alg.db')
    cur = conn.cursor()
    query = '''SELECT * FROM HISTORY'''
    rows = cur.execute(query).fetchall()
    conn.close()
    return rows
