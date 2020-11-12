import math
import wntr.network.controls as controls

def detection(wn, results, i, nodes_start, pipes_start, pipes_length, link_controls):
    nodes_list=wn.node_name_list
    nodes = nodes_start
    pipes_start=pipes_start
    links = wn.link_name_list
    pumps = wn.pump_name_list
    quality = {}
    velocity = {}
    flowrate={}
    nodes_links = {}
    to_close = []
    vel = []
    s = 0
    z = 0
    time_to_close = 1800

    """Wykrywanie wycieku"""
    if nodes_list != nodes:
        for node_l in nodes_list:
            if node_l not in nodes:
                leak_node = node_l
                leak_node2 = wn.get_node("%s" % leak_node)
                nod_links = wn.get_links_for_node("%s" % leak_node)
                lin = wn.get_link("%s" % nod_links[0])
                if lin.initial_status == 1 and nod_links[0] not in to_close and leak_node2.leak_status == True and nod_links[0] not in link_controls:
                    to_close.append(nod_links[0])
                    z += 1
                    print("wykryto wyciek")
                    print(lin)

    """Wykrywanie zatrucia"""

    for n in nodes:
        nodes_links[n] = wn.get_links_for_node(n)
        quality[n]=results.node["quality"].loc[1800*(i+1), n]
        for l in links:
            velocity[l] = results.link["velocity"].loc[1800*(i+1), l]
            flowrate[l] = results.link["flowrate"].loc[1800*(i+1), l]
    for n in nodes:
        for nl in nodes_links[n]:
            link = wn.get_link("%s" % nl)
            nll = []
            nll.append(link.end_node_name)
            nll.append(link.start_node_name)
            nll.remove(n)
            if (link.end_node_name == n and flowrate[nl] > 0) or (link.start_node_name == n and flowrate[nl] < 0):
                vel.append([n, [nl, velocity[nl]]])

            if quality[n] > 2:
                if nl in pumps and link.initial_status == 1 and nl not in to_close and nl not in link_controls:
                    to_close.append(nl)
                    s += 1

                second_links = []
                second_nodes = []
                second_links.append(nodes_links[n])
                for node_l in nodes_links[n]:
                    if node_l in pipes_start:
                        get_node_l = wn.get_link("%s" % node_l)
                        second_nodes.append(get_node_l.end_node_name)
                        second_nodes.append(get_node_l.start_node_name)
                        second_nodes.remove(n)
                        if second_nodes[0] in nodes:
                            second_links.append(nodes_links[second_nodes[0]])
                for pump in pumps:
                    if pump in second_links and pump not in to_close and pump not in link_controls:
                        to_close.append(pump)

                if nll[0] in nodes and nl in pipes_start and ((link.end_node_name == n and flowrate[nl] < 0) or (link.start_node_name == n and flowrate[nl] > 0)):

                    if i == 0:
                        if math.fabs(time_to_close * 2 * velocity[nl]) < pipes_length[nl] and quality[nll[0]] <= 2:
                            if link.initial_status == 1 and nl not in to_close and nl not in link_controls:
                                to_close.append(nl)
                                print("pierwszy if  " + nl)
                                z += 1
                    if i > 0:
                        if math.fabs(time_to_close * velocity[nl]) < pipes_length[nl] and quality[nll[0]] <= 2:
                            if link.initial_status == 1 and nl not in to_close and nl not in link_controls:
                                to_close.append(nl)
                                print("pierwszy if  " + nl)
                                z += 1

                    """Zamykanie doplywow"""
                    if math.fabs(time_to_close * velocity[nl]) >= pipes_length[nl] and quality[nll[0]] <= 2:
                        node_linksb = nodes_links[n]
                        node_linksb.remove(nl)
                        for nlb in node_linksb:
                            linkb = wn.get_link("%s" % nlb)
                            if (linkb.end_node_name == n and flowrate[nlb] > 0.1) or (linkb.start_node_name == n and flowrate[nlb] < -0.1) and linkb.diameter > 0.4 and linkb.initial_status ==1:
                                if nlb not in to_close:
                                    to_close.append(nlb)
                                    print("dopływ " + nlb)
                                    z += 1

                        """Zamykanie przewodow o jeden wezel dalej od wykrycia"""
                        node_links2 = nodes_links[nll[0]]
                        node_links2.remove(nl)
                        for nl2 in node_links2:
                            link2 = wn.get_link("%s" % nl2)
                            next_node = []
                            next_node.append(link2.start_node_name)
                            next_node.append(link2.end_node_name)
                            next_node.remove(nll[0])
                            if nl2 in pipes_start and next_node[0] in nodes:
                                if math.fabs((pipes_length[nl] / velocity[nl] + pipes_length[nl2] / velocity[nl2]) > time_to_close) and quality[next_node[0]] <= 2 and ((link2.end_node_name == nll[0] and flowrate[nl2] < 0) or (link2.start_node_name == nll[0] and flowrate[nl2] > 0)) and link2.initial_status == 1:
                                    if nl2 not in to_close and nl2 not in link_controls:
                                        to_close.append(nl2)
                                        print("drugi if b " + nl2)

                                if math.fabs((pipes_length[nl] / velocity[nl] + pipes_length[nl2] / velocity[nl2]) <= time_to_close):
                                    node_links3 = nodes_links[next_node[0]]
                                    if nl2 in node_links3:
                                        node_links3.remove(nl2)
                                    for nl3 in node_links3:
                                        far_node = []
                                        link3 = wn.get_link("%s" % nl3)
                                        far_node.append(link3.end_node_name)
                                        far_node.append(link3.start_node_name)
                                        far_node.remove(next_node[0])
                                        if nl3 in pipes_start and far_node[0] in nodes:
                                            """Zamykanie przewodow o dwa wezly dalej od wykrycia"""
                                            if math.fabs(pipes_length[nl] / velocity[nl] + pipes_length[nl2] / velocity[nl2] + pipes_length[nl3] / velocity[nl3]) >= time_to_close and quality[far_node[0]] <= 2 and ((link3.end_node_name == next_node[0] and flowrate[nl3] < 0) or (link3.start_node_name == next_node[0] and flowrate[nl3] > 0)) and  link3.initial_status == 1:
                                                if nl3 not in to_close and nl3 not in link_controls:
                                                    to_close.append(nl3)
                                                    print("trzeci if  " + nl3)

    for tc in to_close:
        if tc not in pipes_start:
            to_close.remove(tc)
    return to_close, (i+1) * 1800


def close(wn, to_close, i, link_controls, max_distance, teams, closed):
    for team in teams:
        team.sent = False
    closed_list = []
    leak_links = []
    teams_distance = {}
    tc=to_close[i]
    for l in tc[0]:

        distance = []
        link = wn.get_link("%s" % l)
        start_link_node = link.end_node_name
        end_link_node = link.start_node_name
        get_link_node1 = wn.get_node("%s" % start_link_node)
        get_link_node2 = wn.get_node("%s" % end_link_node)
        x_cord1 = get_link_node1.coordinates[0]
        y_cord1 = get_link_node1.coordinates[1]
        x_cord2 = get_link_node2.coordinates[0]
        y_cord2 = get_link_node2.coordinates[1]

        x_avr = (x_cord1 + x_cord2) / 2
        y_avr = (y_cord1 + y_cord2) / 2

        for team in teams:
            distance.append(math.sqrt((team.cords[0]-x_avr)**2 + (team.cords[1]-y_avr)**2))

        teams_distance[l] = distance

        if get_link_node1.leak_status == False and get_link_node2.leak_status == False:
            for d in distance:
                id = distance.index(d)
                if d <= max_distance / (len(teams) / 2) and teams[id].sent == False and l not in link_controls:
                    act = controls.ControlAction(link, 'status', 0)
                    cond = controls.SimTimeCondition(wn, '=', tc[1] + 1800)
                    ctrl = controls.Control(cond, act, name="control_%s" % l)
                    wn.add_control("Control_%s" % l, ctrl)
                    closed_list.append(l)
                    link_controls.append(l)
                    teams[id].sent = True
                    teams[id].cords = [x_avr, y_avr]

        if get_link_node1.leak_status == True or get_link_node2.leak_status == True:
                leak_links.append(l)
    for l in leak_links:
        for team in teams:
            if team.sent == False and teams_distance[l][teams.index(team)] <= max_distance / (len(teams) / 2) and l not in link_controls:
                link = wn.get_link("%s" % l)
                start_link_node = link.end_node_name
                end_link_node = link.start_node_name
                get_link_node1 = wn.get_node("%s" % start_link_node)
                get_link_node2 = wn.get_node("%s" % end_link_node)
                x_cord1 = get_link_node1.coordinates[0]
                y_cord1 = get_link_node1.coordinates[1]
                x_cord2 = get_link_node2.coordinates[0]
                y_cord2 = get_link_node2.coordinates[1]

                x_avr = (x_cord1 + x_cord2) / 2
                y_avr = (y_cord1 + y_cord2) / 2

                act = controls.ControlAction(link, 'status', 0)
                cond = controls.SimTimeCondition(wn, '=', tc[1] + 1800)
                ctrl = controls.Control(cond, act, name="control_%s" % l)
                wn.add_control("Control_%s" % l, ctrl)
                closed_list.append(l)
                link_controls.append(l)
                team.sent = True
                team.cords = [x_avr, y_avr]


    print(closed_list)
    closed[(1+i)*1800] = closed_list

    for team in teams:
        if team.sent == False:
           team.cords = team.start_cords

    return closed


def open(wn, closed, i, open_link_controls, j, sources):
    sources_list = wn.source_name_list
    if i >= 9:
        if len(closed[(i - 8) * 1800]) == 0 and len(closed[(i - 7) * 1800]) == 0 and len(closed[(i - 6) * 1800]) == 0 and len(closed[(i - 5) * 1800]) == 0 and len(closed[(i - 4) * 1800]) == 0 and len(closed[(i - 3) * 1800]) == 0 and len(closed[(i - 2) * 1800]) == 0 and len(closed[(i - 1) * 1800]) == 0 and len(closed[i * 1800]) == 0:
            for s in sources:
                if "%s_Source" % s.name in sources_list and i * 1800 - s.start_time >= 6 * 1800:
                    wn.remove_source("%s_Source" % s.name)

                for l in closed[j * 1800]:
                    if l not in open_link_controls:
                        link = wn.get_link("%s" % l)
                        act = controls.ControlAction(link, 'status', 1)
                        cond = controls.SimTimeCondition(wn, '=', (i + 3) * 1800)
                        ctrl = controls.Control(cond, act, name="open_control_%s" % l)
                        wn.add_control("Open_Control_%s" % l, ctrl)
                        open_link_controls.append(l)
                j += 1


    return j

# if i >= 4:
#     if len(closed[(i - 3) * 1800]) == 0 and len(closed[(i - 2) * 1800]) == 0 and len(closed[(i - 1) * 1800]) == 0: