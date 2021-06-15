'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
    
'''
import math
import tempfile

import pydotplus

## Added imports
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from colors import color, red, blue
from collections import Counter

from pm4py.visualization.common.utils import human_readable_stat
from pm4py.util import exec_utils
from pm4py.visualization.parameters import Parameters

## Function for creating a legend per output
def create_legenda(legends):
    legenda=""
    legends = set(map(tuple, legends))
    for legend in legends:
        legenda += f"""{ color('  ', 'white', legend[0]) + " " + legend[1]}\n"""
    return legenda
   
def get_corr_hex(num):
    """
    Gets correspondence between a number
    and an hexadecimal string

    Parameters
    -------------
    num
        Number

    Returns
    -------------
    hex_string
        Hexadecimal string
    """
    if num < 10:
        return str(int(num))
    elif num < 11:
        return "A"
    elif num < 12:
        return "B"
    elif num < 13:
        return "C"
    elif num < 14:
        return "D"
    elif num < 15:
        return "E"
    elif num < 16:
        return "F"


def transform_to_hex(graycolor):
    """
    Transform color to hexadecimal representation

    Parameters
    -------------
    graycolor
        Gray color (int from 0 to 255)

    Returns
    -------------
    hex_string
        Hexadecimal color
    """
    left0 = graycolor / 16
    right0 = graycolor % 16

    left00 = get_corr_hex(left0)
    right00 = get_corr_hex(right0)

    return "#" + left00 + right00 + left00 + right00 + left00 + right00


def transform_to_hex_2(color):
    """
    Transform color to hexadecimal representation

    Parameters
    -------------
    color
        Gray color (int from 0 to 255)

    Returns
    -------------
    hex_string
        Hexadecimal color
    """
    color = 255 - color
    color2 = 255 - color

    left0 = color / 16
    right0 = color % 16

    left1 = color2 / 16
    right1 = color2 % 16

    left0 = get_corr_hex(left0)
    right0 = get_corr_hex(right0)
    left1 = get_corr_hex(left1)
    right1 = get_corr_hex(right1)

    return "#" + left0 + right0 + left1 + right1 + left1 + right1


def apply(heu_net, parameters=None):
    """
    Gets a representation of an Heuristics Net

    Parameters
    -------------
    heu_net
        Heuristics net
    parameters
        Possible parameters of the algorithm, including:
            - Parameters.FORMAT

    Returns
    ------------
    gviz
        Representation of the Heuristics Net
    """
    if parameters is None:
        parameters = {}
        
    ## Added new parameters     
    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")
    rules = exec_utils.get_param_value(Parameters.RULES, parameters, "")
    unique_list = exec_utils.get_param_value(Parameters.UNIQUE, parameters, "")
    perc_rules = exec_utils.get_param_value(Parameters.MIN_PERC_RULES, parameters, 0.5)
    perc_conf = exec_utils.get_param_value(Parameters.MIN_PERC_CONF, parameters, 0.75)
    vis_option = exec_utils.get_param_value(Parameters.VISUALIZATION_OPTION, parameters, "basic")
    detail_option = exec_utils.get_param_value(Parameters.DETAILS_OPTION, parameters, "type")

    image_format = exec_utils.get_param_value(Parameters.FORMAT, parameters, "png")

    graph = pydotplus.Dot(strict=True)
    graph.obj_dict['attributes']['bgcolor'] = 'transparent'

    corr_nodes = {}
    corr_nodes_names = {}
    is_frequency = False
    ## Added variables
    legenda = ""
    legends = []
    
    ##Added code
    ## Setting display parameters such as font size and colour
    fontsize = 36
    color1 = "#66CDAA"
    color1_fade = "#AEE3D8" 
    color2 = "#9ACD32"
    color2_fade = "#E8F05F"
    color3 = "#ffa500"
    color3_fade= "#ffe0b5"
    color_other = "#B8B8B8"

    ## Added code
    node_output = []
    max_occ = 1
    total = heu_net.nodes
    
    ## Added code
    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        node_output.append(node)
        node_occ = node.node_occ
        if node_occ > max_occ:
            max_occ = node_occ
            
    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        node_occ = node.node_occ
        graycolor = transform_to_hex_2(max(255 - math.log(node_occ) * 9, 0))
        if node.node_type == "frequency":
            is_frequency = True
            ## Added code
            ############# Extension 'guidelines' ################
            if vis_option == "guidelines":
                if node_name in rules:
                    if rules.get(node_name)[2] == 'yes':
                        n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                   label=node_name + " (" + str(node_occ) + ")", fillcolor=color2, fontname = 'arial')
                        legends.append([color2,  'guideline'])
                    else:
                        n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                   label=node_name + " (" + str(node_occ) + ")", fillcolor=color_other, fontname = 'arial')
                        legends.append([color_other,  'other activity'])
                else:
                    n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                   label=node_name + " (" + str(node_occ) + ")", fillcolor=color_other, fontname = 'arial')
                    legends.append([color_other,  'other activity'])
                legenda = create_legenda(legends)
            ############# Option business rules ################
            elif vis_option == "business_rules":
                if node_name in rules:
                    n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                  label=node_name + " (" + str(node_occ) + ")", fillcolor=color2, fontname = 'arial', fontsize=fontsize)
                    legends.append([color2,  'guideline'])
                        
                else:
                    n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                label=node_name + " (" + str(node_occ) + ")", fillcolor=color_other, fontname = 'arial', fontsize=fontsize)
                    legends.append([color_other,  'possible business rule']) 
                legenda = create_legenda(legends)
             ########### Option conformance ################   
            elif vis_option == "conformance":
                if node_name in rules:
                    if rules.get(node_name)[2] == 'yes':
                        if rules.get(node_name)[0] ==  1:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                           label=node_name + " " + rules.get(node_name)[5] +" (" + str(node_occ) + ")", fillcolor=color1, fontname = 'arial', fontsize=fontsize)
                                legend_name = rules.get(node_name)[1]
                                legends.append([color1,  legend_name])
                        else:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                           label=node_name + " " + rules.get(node_name)[5] + " (" + str(node_occ) + ")", fillcolor=color2, fontname = 'arial', fontsize=fontsize)
                                legend_name = rules.get(node_name)[1]
                                legends.append([color2,  legend_name])
                legenda = create_legenda(legends)
            ############# Option detail ################
            elif vis_option == "detail":
                if detail_option == 'recommended':
                    if node_name in rules:
                            if rules.get(node_name)[2] == 'yes':
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                           label=node_name + " " + rules.get(node_name)[5] +" (" + str(node_occ) + ")", fillcolor=color3, fontname = 'arial', fontsize=fontsize)
                                legend_name = rules.get(node_name)[3]
                                legends.append([color3,  legend_name])
                            else:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled, dashed",
                                           label=node_name + " " + rules.get(node_name)[5] +" (" + str(node_occ) + ")", fillcolor=color3_fade, fontname = 'arial', fontsize=fontsize)
                                legend_name = rules.get(node_name)[3]
                                legends.append([color3_fade,  legend_name])
                    legenda = create_legenda(legends)
                elif detail_option == 'type':
                    if node_name in rules:
                        if rules.get(node_name)[2] == 'yes':
                            if rules.get(node_name)[0] ==  1:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                           label=node_name + " " + rules.get(node_name)[5] +" (" + str(node_occ) + ")", fillcolor=color1, fontname = 'arial', fontsize=fontsize)
                                legend_name = rules.get(node_name)[1]
                                legends.append([color1,  legend_name])
                            else:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                           label=node_name + " " + rules.get(node_name)[5] + " (" + str(node_occ) + ")", fillcolor=color2, fontname = 'arial', fontsize=fontsize)
                                legend_name = rules.get(node_name)[1]
                                legends.append([color2,  legend_name]) 
                    legenda = create_legenda(legends)
                elif detail_option == 'combined':   
                    if node_name in rules:
                        if rules.get(node_name)[0] == 1:
                            if rules.get(node_name)[2] == 'no':
                                n = pydotplus.Node(name=node_name, shape="box", style="filled, dashed",
                                       label=node_name + " " + rules.get(node_name)[5] + " (" + str(node_occ) + ")", fillcolor=color1_fade, fontname = 'arial', fontsize=fontsize)
                                legends.append([color1_fade,  str(rules.get(node_name)[1] + ", " + rules.get(node_name)[3])])
                            else:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                       label=node_name + " " + rules.get(node_name)[5] + " (" + str(node_occ) + ")", fillcolor=color1, fontname = 'arial', fontsize=fontsize)
                                legends.append([color1,  str(rules.get(node_name)[1] + ", " + rules.get(node_name)[3])])
                        elif rules.get(node_name)[0] == 2:
                            if rules.get(node_name)[2] == 'no':
                                n = pydotplus.Node(name=node_name, shape="box", style="filled, dashed",
                                       label=node_name + " " + rules.get(node_name)[5] + " (" + str(node_occ) + ")", fillcolor=color2_fade, fontname = 'arial', fontsize=fontsize)
                                legends.append([color2_fade,  str(rules.get(node_name)[1] + ", " + rules.get(node_name)[3])])
                            else:
                                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                       label=node_name + " " + rules.get(node_name)[5] + " (" + str(node_occ) + ")", fillcolor=color2, fontname = 'arial', fontsize=fontsize)
                                legends.append([color2,  str(rules.get(node_name)[1] + ", " + rules.get(node_name)[3])])
                        else:
                            pass
                    legenda = create_legenda(legends)           
            else:
                n = pydotplus.Node(name=node_name, shape="box", style="filled",
                                   label=node_name + " (" + str(node_occ) + ")", fillcolor=graycolor)
        corr_nodes[node] = n
        corr_nodes_names[node_name] = n
        graph.add_node(n)
        
    # gets max arc value
    max_arc_value = -1
    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    max_arc_value = max(max_arc_value, edge.repr_value)


    for node_name in heu_net.nodes:
        node = heu_net.nodes[node_name]
        for other_node in node.output_connections:
            if other_node in corr_nodes:
                for edge in node.output_connections[other_node]:
                    this_pen_width = 1.0 + math.log(1 + edge.repr_value) / 11.0
                    repr_value = str(edge.repr_value)
                    if edge.net_name:
                        if node.node_type == "frequency":
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                               label=edge.net_name + " (" + repr_value + ")",
                                               color=edge.get_color(),
                                               fontcolor=edge.get_font_color(),
                                               penwidth=edge.get_penwidth(this_pen_width))
                        else:
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                               label=edge.net_name + " (" + human_readable_stat(repr_value) + ")",
                                               color=edge.get_color(),
                                               fontcolor=edge.get_font_color(),
                                               penwidth=edge.get_penwidth(this_pen_width))
                    else:
                        if node.node_type == "frequency":
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node], label=repr_value,
                                               color=edge.get_color(),
                                               fontcolor=edge.get_font_color(),
                                               penwidth=edge.get_penwidth(this_pen_width))
                        else:
                            e = pydotplus.Edge(src=corr_nodes[node], dst=corr_nodes[other_node],
                                               label=human_readable_stat(repr_value),
                                               color=edge.get_color(),
                                               fontcolor=edge.get_font_color(),
                                               penwidth=edge.get_penwidth(this_pen_width))

                    graph.add_edge(e)

    for index, sa_list in enumerate(heu_net.start_activities):
        effective_sa_list = [n for n in sa_list if n in corr_nodes_names]
        if effective_sa_list:
            start_i = pydotplus.Node(name="start_" + str(index), label="@@S", color=heu_net.default_edges_color[index],
                                     fontsize="8", fontcolor="#32CD32", fillcolor="#32CD32",
                                     style="filled")
            graph.add_node(start_i)
            for node_name in effective_sa_list:
                sa = corr_nodes_names[node_name]
                if type(heu_net.start_activities[index]) is dict:
                    if is_frequency:
                        occ = heu_net.start_activities[index][node_name]
                        this_pen_width = 1.0 + math.log(1 + occ) / 11.0
                        if heu_net.net_name[index]:
                            e = pydotplus.Edge(src=start_i, dst=sa,
                                               label=heu_net.net_name[index] + " (" + str(occ) + ")",
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                        else:
                            e = pydotplus.Edge(src=start_i, dst=sa, label=str(occ),
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                    else:
                        e = pydotplus.Edge(src=start_i, dst=sa, label=heu_net.net_name[index],
                                           color=heu_net.default_edges_color[index],
                                           fontcolor=heu_net.default_edges_color[index])
                else:
                    e = pydotplus.Edge(src=start_i, dst=sa, label=heu_net.net_name[index],
                                       color=heu_net.default_edges_color[index],
                                       fontcolor=heu_net.default_edges_color[index])
                graph.add_edge(e)

    for index, ea_list in enumerate(heu_net.end_activities):
        effective_ea_list = [n for n in ea_list if n in corr_nodes_names]
        if effective_ea_list:
            end_i = pydotplus.Node(name="end_" + str(index), label="@@E", color="#",
                                   fillcolor="#FFA500", fontcolor="#FFA500", fontsize="8",
                                   style="filled")
            graph.add_node(end_i)
            for node_name in effective_ea_list:
                ea = corr_nodes_names[node_name]
                if type(heu_net.end_activities[index]) is dict:
                    if is_frequency:
                        occ = heu_net.end_activities[index][node_name]
                        this_pen_width = 1.0 + math.log(1 + occ) / 11.0
                        if heu_net.net_name[index]:
                            e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index] + " (" + str(occ) + ")",
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                        else:
                            e = pydotplus.Edge(src=ea, dst=end_i, label=str(occ),
                                               color=heu_net.default_edges_color[index],
                                               fontcolor=heu_net.default_edges_color[index], penwidth=this_pen_width)
                    else:
                        e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index],
                                           color=heu_net.default_edges_color[index],
                                           fontcolor=heu_net.default_edges_color[index])
                else:
                    e = pydotplus.Edge(src=ea, dst=end_i, label=heu_net.net_name[index],
                                       color=heu_net.default_edges_color[index],
                                       fontcolor=heu_net.default_edges_color[index])
                graph.add_edge(e)

    file_name = tempfile.NamedTemporaryFile(suffix='.' + image_format)
    file_name.close()
    graph.write(file_name.name, format=image_format)
    #Added code to display legend with output:
    legenda = print(legenda)
    return file_name, legenda
