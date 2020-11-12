import sqlite3
import numpy as num

def create_db(wn, links_names, nodes_names):

    links_list=links_names
    nodes_list=nodes_names

    # utworzenie połączenia z bazą przechowywaną na dysku
    # lub w pamięci (':memory:')
    con = sqlite3.connect('woda.db')

    # dostęp do kolumn przez indeksy i przez nazwy
    con.row_factory = sqlite3.Row

    # utworzenie obiektu kursora
    cur = con.cursor()
    # tworzenie tabel
   #\ cur.execute("DROP TABLE IF EXISTS links;")

    cur.executescript("""
        DROP TABLE IF EXISTS links;
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY ASC,
            link_name varchar(250) NOT NULL,
            link_type varchar(250) NOT NULL,
            start_node varchar(250) NOT NULL,
            end_node varchar(250) NOT NULL
    			)""")

    cur.executescript("""
        DROP TABLE IF EXISTS nodes;
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY ASC,
            node_name varchar(250) NOT NULL,
            node_type varchar(250) NOT NULL
        )""")

    cur.executescript("""
        DROP TABLE IF EXISTS pipes;
        CREATE TABLE IF NOT EXISTS pipes (
            id INTEGER PRIMARY KEY ASC,
    		pipe_name varchar(250) NOT NULL,
    		start_node varchar(250) NOT NULL,
            end_node varchar(250) NOT NULL,
            pipe_length DECIMAL,
            pipe_diameter DECIMAL,
            pipe_status varchar(250) NOT NULL,
    		FOREIGN KEY(start_node) REFERENCES links(start_node),
    		FOREIGN KEY(end_node) REFERENCES links(end_node),
            FOREIGN KEY(pipe_name) REFERENCES links(name_links)
        )""")

    cur.executescript("""
        DROP TABLE IF EXISTS pumps;
        CREATE TABLE IF NOT EXISTS pumps (
            id INTEGER PRIMARY KEY ASC,
    		pump_name varchar(250) NOT NULL,
    		start_node varchar(250) NOT NULL,
            end_node varchar(250) NOT NULL,
            pump_status varchar(250) NOT NULL,
    		FOREIGN KEY(start_node) REFERENCES links(start_node),
    		FOREIGN KEY(end_node) REFERENCES links(end_node),
            FOREIGN KEY(pump_name) REFERENCES links(name_links)
        )""")

    cur.executescript("""
        DROP TABLE IF EXISTS junctions;
        CREATE TABLE IF NOT EXISTS junctions (
            id INTEGER PRIMARY KEY ASC,
    		junction_name archar(250) NOT NULL,
            FOREIGN KEY(junction_name) REFERENCES nodes(name_nodes)
        )""")

    cur.executescript("""
        DROP TABLE IF EXISTS tanks;
        CREATE TABLE IF NOT EXISTS tanks (
            id INTEGER PRIMARY KEY ASC,
    		tank_name varchar(250) NOT NULL,
    		max_level DECIMAL NOT NULL,
            actual_level DECIMAL NOT NULL,           
            FOREIGN KEY(tank_name) REFERENCES nodes(name_nodes)
        )""")

    # cur.execute('DELETE FROM links')
    # cur.execute('DELETE FROM nodes')
    # cur.execute('DELETE FROM pipes')
    # cur.execute('DELETE FROM pumps')
    # cur.execute('DELETE FROM junctions')
    # cur.execute('DELETE FROM tanks')

    cur.execute('DROP TABLE IF EXISTS pipes_simulation')
    cur.execute('DROP TABLE IF EXISTS pumps_simulation')
    cur.execute('DROP TABLE IF EXISTS junctions_simulation')
    cur.execute('DROP TABLE IF EXISTS tanks_simulation')

    for l in links_list:
        link=wn.get_link("%s" % l)
        cur.execute('INSERT INTO links VALUES(?, ?, ?, ?, ?);', (None, '%s' % l, '%s' % link.link_type, '%s' % link.start_node, '%s' % link.end_node))

    for n in nodes_list:
        node=wn.get_node("%s" % n)
        cur.execute('INSERT INTO nodes VALUES(?, ?, ?);', (None, '%s' % n, '%s' % node.node_type))

    cur.execute('SELECT link_name, start_node, end_node FROM links Where link_type=?', ('Pipe',))
    pipes_data=cur.fetchall()

    p=0
    while p<len(pipes_data):
        pipe=wn.get_link("%s" % pipes_data[p]["link_name"])
        cur.execute('INSERT INTO pipes VALUES(?, ?, ?, ?, ?, ?, ?);', (None, pipes_data[p]['link_name'], pipes_data[p]['start_node'], pipes_data[p]['end_node'], round(pipe.length, 3), round(pipe.diameter, 3), pipe.initial_status))
        p+=1

    cur.execute('SELECT link_name, start_node, end_node FROM links WHERE link_type=?', ('Pump',))
    pumps_data=cur.fetchall()

    pp=0
    while pp<len(pumps_data):
        pump = wn.get_link("%s" % pumps_data[pp]["link_name"])
        cur.execute('INSERT INTO pumps VALUES(?, ?, ?, ?, ?)', (None, pumps_data[pp]['link_name'], pumps_data[pp]['start_node'], pumps_data[pp]['end_node'], pump.initial_status))
        pp+=1

    cur.execute('SELECT node_name FROM nodes WHERE node_type=?', ('Junction',))
    junctions_data=cur.fetchall()

    j=0
    while j<len(junctions_data):
        cur.execute('INSERT INTO junctions VALUES(?, ?)', (None, junctions_data[j]['node_name']))
        j+=1

    cur.execute('SELECT node_name FROM nodes WHERE node_type=?', ('Tank',))
    tanks_data=cur.fetchall()

    t=0
    while t<len(tanks_data):
        tank=wn.get_node("%s" % tanks_data[t]["node_name"])
        cur.execute('INSERT INTO tanks VALUES(?, ?, ?, ?)', (None, tanks_data[t]['node_name'], round(tank.max_level, 3), round(tank.level, 3)))
        t+=1

    con.commit()


def update_db(wn, results, i):
    con = sqlite3.connect('woda.db')

    # dostęp do kolumn przez indeksy i przez nazwy
    con.row_factory = sqlite3.Row

    # utworzenie obiektu kursora
    cur = con.cursor()


    cur.executescript("""
            CREATE TABLE IF NOT EXISTS pipes_simulation (
                simulation_time DECIMAL NOT NULL,
        		pipe_name varchar(250) NOT NULL,
                pipe_status varchar(250) NOT NULL,
        		velocity DECIMAL,
        		pipe_headloss DECIMAL NOT NULL,
        		pipe_flowrate DECIMAL NOT NULL,
                FOREIGN KEY(pipe_name) REFERENCES links(name_links)
            )""")

    cur.executescript("""
            CREATE TABLE IF NOT EXISTS pumps_simulation (
                simulation_time DECIMAL NOT NULL,
        		pump_name varchar(250) NOT NULL,
                pump_status varchar(250) NOT NULL,
        		pump_headloss DECIMAL NOT NULL,
        		pump_flowrate DECIMAL NOT NULL,
                FOREIGN KEY(pump_name) REFERENCES links(name_links)
            )""")

    cur.executescript("""
            CREATE TABLE IF NOT EXISTS junctions_simulation (
                simulation_time DECIMAL NOT NULL,
        		junction_name archar(250) NOT NULL,
                chemical_concenentraction DECIMAL NOT NULL,
        		demand DECIMAL NOT NULL,
        		pressure DECIMAL NOT NULL,
        		head DECIMAL NOT NULL,
                FOREIGN KEY(junction_name) REFERENCES nodes(name_nodes)
            )""")

    cur.executescript("""
            CREATE TABLE IF NOT EXISTS tanks_simulation (
                simulation_time DECIMAL NOT NULL,
        		tank_name varchar(250) NOT NULL,
                actual_level DECIMAL NOT NULL,           
                FOREIGN KEY(tank_name) REFERENCES nodes(name_nodes)
            )""")

    cur.execute('SELECT pipe_name FROM pipes')
    pipes_update=cur.fetchall()
    pu=0
    while pu<len(pipes_update):
        p_name=pipes_update[pu]['pipe_name']
        p_status = str(results.link["status"].loc[1800*(i+1), "%s" % p_name])
        p_velocity=float(results.link["velocity"].loc[1800*(i+1), "%s" % p_name])
        p_headloss=float(results.link["headloss"].loc[1800*(i+1), "%s" % p_name])
        p_flowrate=float(results.link["flowrate"].loc[1800*(i+1), "%s" % p_name])
        cur.execute('INSERT INTO pipes_simulation VALUES(?, ?, ?, ?, ?, ?);', ((i+1)*1800, p_name, p_status, round(p_velocity, 3), round(p_headloss, 3), round(p_flowrate, 3)))
        pu+=1

    cur.execute('SELECT pump_name FROM pumps')
    pumps_update = cur.fetchall()

    ppu=0
    while ppu<len(pumps_update):
        pp_name=pumps_update[ppu]['pump_name']
        pp_status = str(results.link["status"].loc[1800*(i+1), "%s" % pp_name])
        pp_headloss=float(results.link["headloss"].loc[1800*(i+1), "%s" % pp_name])
        pp_flowrate=float(results.link["flowrate"].loc[1800*(i+1), "%s" % pp_name])
        cur.execute('INSERT INTO pumps_simulation VALUES(?, ?, ?, ?, ?);', ((i+1)*1800, pp_name, pp_status, round(pp_headloss, 3), round(pp_flowrate, 3)))
        ppu+=1

    cur.execute('SELECT junction_name FROM junctions')
    junctions_update=cur.fetchall()

    ju=0
    while ju<len(junctions_update):
        j_name=junctions_update[ju]['junction_name']
        j_concentration=float(results.node["quality"].loc[1800*(i+1), "%s" % j_name])
        j_demand=float(results.node["demand"].loc[1800*(i+1), "%s" % j_name])
        j_pressure=float(results.node["pressure"].loc[1800*(i+1), "%s" % j_name])
        j_head=float(results.node["head"].loc[1800*(i+1), "%s" % j_name])
        cur.execute('INSERT INTO junctions_simulation VALUES(?, ?, ?, ?, ?, ?);', ((i+1)*1800, j_name, round(j_concentration, 3), round(j_demand, 3), round(j_pressure, 3), round(j_head, 3)))
        ju+=1

    cur.execute('SELECT tank_name FROM tanks')
    tanks_update=cur.fetchall()

    tu=0
    while tu<len(tanks_update):
        t_name=tanks_update[tu]['tank_name']
        tank_u=wn.get_node("%s" % t_name)
        cur.execute('INSERT INTO tanks_simulation VALUES(?, ?, ?)', ((i+1)*1800, t_name, round(tank_u.level, 3)))
        tu+=1

    con.commit()
    cur.execute('SELECT velocity FROM pipes_simulation WHERE simulation_time=?', ((i+1)*1800,))
    pip=cur.fetchall()
    # srednia_predkosc=0
    #
    # for pi in pip:
    #     srednia_predkosc+=pi['velocity']
    # srednia_predkosc=srednia_predkosc/len(pip)
    # print(srednia_predkosc)







