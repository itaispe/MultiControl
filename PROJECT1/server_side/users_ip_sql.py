from sql_manage import ManageSQL
import pickle
import base64

ip_sql = ManageSQL('users_ip')


def see_all():
    ip_sql.open_db()
    query = 'SELECT * FROM {}'.format(ip_sql.table_name)
    ip_sql.curr.execute(query)
    lst = ip_sql.curr.fetchall()
    print(lst)
    ip_sql.close_db()


def create_table():
    ip_sql.create_table('id INTEGER PRIMARY KEY,AdminIP TEXT,IpList BLOB')


def insert_into_table(lst, admin_ip):
    ip_sql.open_db()
    sql = "SELECT COUNT(*) FROM {}".format(ip_sql.table_name)
    ip_sql.curr.execute(sql)
    id_count = int(ip_sql.curr.fetchall()[0][0]) + 1
    sql = 'SELECT AdminIP FROM {} WHERE AdminIP == "{}"'.format(ip_sql.table_name, admin_ip)
    ip_sql.curr.execute(sql)
    exist = ip_sql.curr.fetchall()
    if exist:
        sql = 'UPDATE {} SET IpList = "{}" WHERE AdminIP == "{}"'.format(ip_sql.table_name, lst, admin_ip)
        ip_sql.curr.execute(sql)
        ip_sql.commit()
    else:
        sql = 'INSERT INTO {} (id,AdminIP,IpList) VALUES ("{}","{}","{}")'.format(ip_sql.table_name, id_count,
                                                                                  admin_ip, lst)
        ip_sql.curr.execute(sql)
        ip_sql.commit()
    ip_sql.close_db()


def get_user_ip_list(admin_ip):
    ip_sql.open_db()
    sql = 'SELECT IpList FROM {} WHERE AdminIP == "{}"'.format(ip_sql.table_name, admin_ip)
    ip_sql.curr.execute(sql)
    lst = ip_sql.curr.fetchall()
    ip_sql.close_db()
    if lst:
        return lst[0][0]
    else:
        return None


if __name__ == '__main__':
    ip_sql.drop_table()
    create_table()
