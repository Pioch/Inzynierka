import wntr
import matplotlib.pyplot as plt
import detection
import Data_base
import random
import timeit
import math
import wntr.network.controls as controls
inp_file = 'networks/Net3.inp'

i = 0
j = 1
los = random.randrange(0, 9)
wn = wntr.network.WaterNetworkModel(inp_file)
nodes_names = wn.node_name_list
junctions_names = wn.junction_name_list
links_names = wn.link_name_list
pipes_names = wn.pipe_name_list
source = random.choice(junctions_names)
leak = random.choice(pipes_names)
simulation_time = 3*3600
source_start_time = 0
leak_start_time = 3600
to_close = []
closed = {}
link_controls = []
open_link_controls = []
cords_x_all = []
cords_y_all = []
cords = []
teams = []
start_teams_cords = []
teams_cords = []
pipes_length ={}
leaks = []
sources = []
sim = wntr.sim.EpanetSimulator(wn)
wn.options.quality.mode = 'CHEMICAL'

wn.options.time.hydraulic_timestep = 1800
wn.options.time.report_timestep = 1800
wn.options.time.pattern_timestep = 1800

start_time = timeit.default_timer()

Data_base.create_db(wn, links_names, nodes_names)

class teams_class:
    def __init__(self, start_cords, team_cords):
        self.start_cords = start_cords
        self.cords = team_cords
        self.sent = False

class leaks_class:
    def __init__(self, name, diameter, start_time, end_time):
        self.name = name
        self.diameter = diameter
        self.start_time = start_time
        self.end_time = end_time

class sources_class:
    def __init__(self, name, start_time):
        self.name = name
        self.start_time = start_time

for n in nodes_names:
    get_node=wn.get_node("%s" % n)
    cords_x_all.append(get_node.coordinates[0])
    cords_y_all.append(get_node.coordinates[1])
cords.append(min(cords_x_all))
cords.append(max(cords_x_all))
cords.append(min(cords_y_all))
cords.append(max(cords_y_all))
max_distance = math.sqrt((cords[1] ** 2) + (cords[3] ** 2))
links_amount = len(links_names)
teams_groups = int(links_amount / 55)

if teams_groups == 0:
    teams_groups = 1

square_amount = int(teams_groups / 4)
len = 0

if teams_groups % 4 == 1:
    start_teams_cords.append([(1 / 2) * cords[1], (1 / 2) * cords[3]])
    start_teams_cords.append([(1 / 2) * cords[1], (1 / 2) * cords[3]])

if teams_groups % 4 == 2:
    start_teams_cords.append([(1 / 2) * cords[1], (1 / 2) * cords[3]])
    start_teams_cords.append([(1 / 2) * cords[1], (1 / 2) * cords[3]])
    start_teams_cords.append([(1 / 2) * cords[1], (1 / 2) * cords[3]])
    start_teams_cords.append([(1 / 2) * cords[1], (1 / 2) * cords[3]])

if teams_groups % 4 == 3:
    start_teams_cords.append([(1 / 3) * cords[1], (1 / 3) * cords[3]])
    start_teams_cords.append([(1 / 3) * cords[1], (1 / 3) * cords[3]])
    start_teams_cords.append([(1 - (1 / 3)) * cords[1], (1 / 3) * cords[3]])
    start_teams_cords.append([(1 - (1 / 3)) * cords[1], (1 / 3) * cords[3]])
    start_teams_cords.append([(1 / 2) * cords[1], (2 / 3) * cords[3]])
    start_teams_cords.append([(1 / 2) * cords[1], (2 / 3) * cords[3]])

while square_amount > 0:
    start_teams_cords.append([(1 / (4 * square_amount)) * cords[1], (1 / (4 * square_amount)) * cords[3]])
    start_teams_cords.append([(1 / (4 * square_amount)) * cords[1], (1 / (4 * square_amount)) * cords[3]])
    start_teams_cords.append([(1 / (4 * square_amount)) * cords[1], (1 - (1 / (4 * square_amount))) * cords[3]])
    start_teams_cords.append([(1 / (4 * square_amount)) * cords[1], (1 - (1 / (4 * square_amount))) * cords[3]])
    start_teams_cords.append([(1 / (1 - (4 * square_amount))) * cords[1], (1 / (4 * square_amount)) * cords[3]])
    start_teams_cords.append([(1 / (1 - (4 * square_amount))) * cords[1], (1 / (4 * square_amount)) * cords[3]])
    start_teams_cords.append([(1 / (1 - (4 * square_amount))) * cords[1], (1 - (1 / (4 * square_amount))) * cords[3]])
    start_teams_cords.append([(1 / (1 - (4 * square_amount))) * cords[1], (1 - (1 / (4 * square_amount))) * cords[3]])
    square_amount -= 1

while len < teams_groups*2:
    teams.append(teams_class(start_teams_cords[len], start_teams_cords[len]))
    len +=1

for p in pipes_names:
    pipe = wn.get_link("%s" % p)
    pipes_length[p] = pipe.length

leaks.append(leaks_class(leak, 0.15, 0, 4*3600))
sources.append(sources_class(source, 0))
sources.append(sources_class(120, 3*3600))

for s in sources:
    source_pattern = wntr.network.elements.Pattern.binary_pattern('%s_SourcePattern' % s.name, start_time=s.start_time, end_time=s.start_time + 4 * 3600, duration=4 * 3600, step_size=wn.options.time.pattern_timestep)
    wn.add_pattern('%s_SourcePattern' % s.name, source_pattern)
    wn.add_source('%s_Source' % s.name, "%s" % s.name, 'SETPOINT', 1000, '%s_SourcePattern' % s.name)

# source_pattern = wntr.network.elements.Pattern.binary_pattern('SourcePattern', start_time=source_start_time, end_time=source_start_time + 4*3600, duration=4*3600, step_size=wn.options.time.pattern_timestep)
# wn.add_pattern('SourcePattern', source_pattern)
# wn.add_source('Source1', "%s" % a, 'SETPOINT', 1000, 'SourcePattern')

for l in leaks:
    wn.split_pipe('%s' % l.name, '%s_b' % l.name, '%s_leak_node' % l.name)
    leak_node = wn.get_node('%s_leak_node' % l.name)
    leak_node.add_leak(wn, area=0.15, start_time=l.start_time, end_time=l.start_time + 4 * 3600)
    ln = wn.get_node("%s_leak_node" % l.name)


# wn.split_pipe('%s' % leak, '%s_b' % leak, '%s_leak_node' % leak)
# leak_node = wn.get_node('%s_leak_node' % leak)
# leak_node.add_leak(wn, area=0.15, start_time=leak_start_time, end_time=4*3600)
# ln=wn.get_node("%s_leak_node" % leak)


while(i<=simulation_time/1800):
    for l in leaks:
        ln = wn.get_node("%s_leak_node" % l.name)
        if i == l.start_time / 1800:
            ln.leak_status = True

    wn.options.time.duration = 1800*(i+1)
    res = sim.run_sim()
    to_close.append(detection.detection(wn, res, i, nodes_names, pipes_names, pipes_length, link_controls))
    closed = detection.close(wn, to_close, i, link_controls, max_distance, teams, closed)
    j = detection.open(wn, closed, i, open_link_controls, j, sources)
    Data_base.update_db(wn, res, i)
    CHEM = res.node['quality'].loc[wn.options.time.duration,:]
    STAT=res.link["status"].loc[wn.options.time.duration, :]
    VEL=res.link["velocity"].loc[wn.options.time.duration, :]
    wntr.graphics.plot_network(wn, node_attribute=CHEM, link_attribute=STAT, node_size=20, link_range=[0, 1], node_range=[0, 1000], title='Chemical concentration at time: %s' % wn.options.time.duration)
    plt.figure() #cos tu nie dziala w Pycharm community
    plt.show() #cos tu nie dziala w Pycharm community
    #detection.open(wn, closed, i, res)
    #wykrywanie_zatrucia.przypisanie(wn, res, i, nodes_names)
    i += 1
    #print(res.node["quality"].loc[i*1800, :])
print(leak)
print(source)
print(to_close)
print(closed)
print('\nExecution time         : ' + str(timeit.default_timer() - start_time))
print(link_controls)
print(1)






