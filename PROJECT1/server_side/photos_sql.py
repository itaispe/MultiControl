import sql_manage

photos_sql = sql_manage.ManageSQL('photos_sql')


def create_table():
    photos_sql.create_table('id INTEGER PRIMARY KEY, time INTEGER, name TEXT, comp_num INTEGER,photo BLOB ')


def insert_new_photo(time, name, comp_num, photo):
    photos_sql.open_db()
    sql = "SELECT COUNT(*) FROM {}".format(photos_sql.table_name)
    photos_sql.curr.execute(sql)
    id_count = int(photos_sql.curr.fetchall()[0][0]) + 1
    sql_com = """ INSERT INTO {} (id,time,name,comp_num,photo) VALUES(?,?,?,?) """
    data_tup = (id_count,time, name, comp_num, photo)
    photos_sql.curr.execute(sql_com, data_tup)
    photos_sql.commit()
    photos_sql.close_db()


