import sqlite3

def create_report(sent, i):
    con = sqlite3.connect('woda.db')

    # dostęp do kolumn przez indeksy i przez nazwy
    con.row_factory = sqlite3.Row

    # utworzenie obiektu kursora
    cur = con.cursor()

    cur.executescript("""
                CREATE TABLE IF NOT EXISTS reports (
                    simulation_time DECIMAL NOT NULL,
            		link varchar(250) NOT NULL
                )""")

    cur.execute('INSERT INTO reports VALUES(?, ?);', (1800*i, "%s" % sent[1800*i]))

    con.commit()