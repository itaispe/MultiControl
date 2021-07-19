from sql_manage import ManageSQL

admins_sql = ManageSQL('admins_sql')


def see_all():
    admins_sql.open_db()
    query = 'SELECT * FROM {}'.format(admins_sql.table_name)
    admins_sql.curr.execute(query)
    lst = admins_sql.curr.fetchall()
    print(lst)
    admins_sql.close_db()


def create_table():
    admins_sql.create_table('id INTEGER PRIMARY KEY,username TEXT, password TEXT')


def insert_into_table(username, password):
    admins_sql.open_db()
    sql = "SELECT COUNT(*) FROM {}".format(admins_sql.table_name)
    admins_sql.curr.execute(sql)
    id_count = int(admins_sql.curr.fetchall()[0][0]) + 1
    sql_com = 'INSERT INTO {} (id,username,password) VALUES ("{}","{}","{}")'.format(admins_sql.table_name,
                                                                                     id_count, username,
                                                                                     password)
    admins_sql.curr.execute(sql_com)
    admins_sql.commit()
    admins_sql.close_db()


def check_password(username, password):
    admins_sql.open_db()
    sql_com = 'SELECT password FROM {} WHERE username == "{}"'.format(admins_sql.table_name, username)
    admins_sql.curr.execute(sql_com)
    db_pass = ''
    lst = admins_sql.curr.fetchall()
    if lst:
        db_pass = lst[0][0]
    admins_sql.close_db()
    return db_pass == password


def check_new_username(username):
    good = True
    admins_sql.open_db()
    sql_com = 'SELECT username FROM {}'.format(admins_sql.table_name)
    admins_sql.curr.execute(sql_com)
    users_lst = admins_sql.curr.fetchall()
    print(users_lst)
    for i in users_lst:
        if i[0] == username:
            good = False
    admins_sql.close_db()
    return good


def get_user_object(username):
    admins_sql.open_db()
    sql_com = 'SELECT object FROM {} WHERE username == "{}"'.format(admins_sql.table_name, username)
    admins_sql.curr.execute(sql_com)
    obj = admins_sql.curr.fetchall()[0][0]
    admins_sql.close_db()
    return obj


def main():
    see_all()


if __name__ == '__main__':
    main()
