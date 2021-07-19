import sqlite3


class ManageSQL:
    def __init__(self,table_name):
        self.db_file = 'multi_control.db'
        self.table_name = table_name
        self.conn = None
        self.curr = None

    def open_db(self):
        self.conn = sqlite3.connect(self.db_file)

        self.curr = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def create_table(self,cols_str):
        self.open_db()
        sql_com = 'CREATE TABLE {} ({})'.format(self.table_name,cols_str)
        self.curr.execute(sql_com)
        self.commit()
        self.close_db()

    def drop_table(self):
        self.open_db()
        sql_com = 'DROP TABLE {}'.format(self.table_name)
        self.curr.execute(sql_com)
        self.commit()
        self.close_db()