import sqlite3
#DATABASE


class dataFunc:
    def __init__(self):
        self.name = 'youtube_url.sqlite'

    def count_links_and_print(self):
        conn = sqlite3.connect('youtube_url.sqlite', timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM Youtube
                                    ''')
        return cursor.fetchone()

    def insert_into_table(self,pos, url):
        conn = sqlite3.connect('youtube_url.sqlite', timeout=10.0)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Youtube
                               (ID INTEGER NOT NULL PRIMARY KEY,
                               URL           TEXT NOT NULL);
                               ''')
        exec_str = "INSERT INTO Youtube (URL) VALUES ('{}');".format(str(url))
        print(exec_str)
        cursor.execute(exec_str)
        conn.commit()
        conn.close()
        return url + ' added to table at position: ' + str(pos)

    def select_url_between_values(self, low_val, high_val=None):
        if not high_val:
            items2 = []
            conn = sqlite3.connect('youtube_url.sqlite')
            cursor = conn.cursor()
            exec_select = "SELECT ID, URL FROM Youtube \
                                  WHERE ID={}".format(int(low_val))
            data = cursor.execute(exec_select)
            for item in data:
                items2.append(item)
            return items2
        else:
            items = []
            conn = sqlite3.connect('youtube_url.sqlite')
            cursor = conn.cursor()
            exec_select = "SELECT ID, URL FROM Youtube \
                      WHERE ID BETWEEN {} and {} ORDER BY ID".format(str(low_val), str(high_val))
            data = cursor.execute(exec_select)
            for item in data:
                items.append(item)
            return items