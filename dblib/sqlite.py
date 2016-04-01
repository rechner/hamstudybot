import os, sys
import sqlite3

def getScriptPath():
    pathname = os.path.dirname(sys.argv[0])
    return os.path.abspath(pathname)

class Database:
    def __init__(self, db_file='store.db'):
        script_path = getScriptPath()
        os.chdir(script_path)
        file_path = os.path.abspath(db_file)
        self.connect_db(file_path)
        self.init_db()

    def connect_db(self, db_file):
        self.db = sqlite3.connect(db_file)
        self.db.row_factory = sqlite3.Row

    def init_db(self):
        self.db.execute("CREATE TABLE IF NOT EXISTS "
                        "_meta(key TEXT PRIMARY KEY, value TEXT);\n"
                        "CREATE TABLE polling IF NOT EXISTS "
                        "(chat_id INT, pool TEXT, "
                        "question_id TEXT, subelement TEXT, section TEXT);"
                        )
        self.db.commit()

    def __getitem__(self, key):
        return self.get_meta(key)

    def __setitem__(self, key, value):
        self.set_meta(key, value)

    def __contains__(self, key):
        try:
            self.get_meta(key)
            return True
        except KeyError:
            return False

    def __delitem__(self, key):
        self.db.execute("DELETE FROM _meta WHERE key = ?", (key,))

    def get_meta(self, key):
        cur = self.db.execute("SELECT * FROM _meta WHERE key = ?", (key,))
        result = cur.fetchone()
        if result is None:
            raise KeyError(key)
        return result['value']
        
    def set_meta(self, key, value):
        try:
            self.db.execute("INSERT INTO _meta(key, value) VALUES (?,?)",
                        (key, value))
        except sqlite3.IntegrityError:
            self.db.execute("UPDATE _meta SET value = ? WHERE key = ?", 
                        (value, key))

    def commit(self):
        self.db.commit()
        

