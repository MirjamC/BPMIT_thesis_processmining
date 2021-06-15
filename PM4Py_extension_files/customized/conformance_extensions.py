import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as convertor
from pm4py.util import constants
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner 
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
import importlib
import numpy as np
import os

## Prepare the log based on the chosen extensions
## Create the additional output

def prepare_guidelines(guidelines):
    guidelines = guidelines[['event', 'type', 'type_name', 'recommended', 'recommended_name', 'interchangeable_nr', ]]
    ## Add a mark to events that are part of multiple options
    marks = ['±', '†', '¶']
    nrs = set(guidelines[guidelines.duplicated(subset=['interchangeable_nr'],keep=False)]['interchangeable_nr'].tolist())
    nrs = list(nrs)
    idx = 0
    guidelines['suffix'] = ''

    while idx < len(nrs):
        guidelines['suffix'] = np.where(guidelines['interchangeable_nr'] == nrs[idx], marks[idx], guidelines['suffix'])
        #print(marks[idx])
        idx += 1
    
    guidelines_dict = guidelines.set_index('event').T.to_dict('list')
    return guidelines_dict
    
def prepare_log(raw_log, guidelines, option, suboption='', min_perc = 0):
    missing = []
    output = ""
    df_guidelines = pd.DataFrame.from_dict(guidelines, orient='index').reset_index()
    df_guidelines = df_guidelines.rename(columns = {'index': 'concept:name'})
    df_guidelines = df_guidelines[['concept:name']]
    if option == 'guidelines':
        events = raw_log['concept:name'].unique()
        eventlist = []
        guidelist = []
        for guideline in guidelines.keys():
                if guidelines.get(guideline)[2] == 'yes':
                    guidelist.append(guideline)
                    if guideline in events:
                        eventlist.append(guideline)
        events_nr = len(set(eventlist))
        guides_nr = len(guidelist)
        conformance = round((events_nr / guides_nr) * 100, 0)
        output = "Number of guideline activities in logfiles: " + str(events_nr) + ", total number of guidelines: " + str(guides_nr) + " (" + str(conformance) + "%)" 
    if option == 'detail':
        if suboption == 'type':
            eventlist = []
            events = raw_log['concept:name'].unique()
            for guideline in guidelines.keys():
                if guidelines.get(guideline)[2] == 'yes':
                    eventlist.append(guideline)
                    if guideline not in events:
                        missing.append([guideline + " " + guidelines.get(guideline)[5], guidelines.get(guideline)[1], guidelines.get(guideline)[5]])   
            df_guidelines = df_guidelines[df_guidelines['concept:name'].isin(eventlist)]
            log = raw_log.merge(df_guidelines, on = 'concept:name', how = 'inner')
            output = pd.DataFrame(missing, columns = ['event', 'type', 'interchangeable'])
        elif suboption == 'recommended' or suboption == 'combined':
            events = raw_log['concept:name'].unique()
            for guideline in guidelines.keys():
                if guideline not in events:
                    missing.append([guideline + " " + guidelines.get(guideline)[5], guidelines.get(guideline)[1], guidelines.get(guideline)[3], guidelines.get(guideline)[5]])   
            log = raw_log.merge(df_guidelines, on = 'concept:name', how = 'inner')
            output = pd.DataFrame(missing, columns = ['event', 'type', 'recommended', 'interchangeable'])   
        output['interchangeable'] = output['interchangeable'].apply(lambda x: 'no' if x == '' else 'yes')
    elif option == 'conformance':
        eventlist = []
        log = raw_log.merge(df_guidelines, on = 'concept:name', how = 'inner')
        events = log['concept:name'].unique()
        cases = log['case:concept:name'].nunique()
        for event in events:
            if guidelines.get(event)[2] == 'yes': 
                event_occ = log[log['concept:name'] == event]['case:concept:name'].nunique()
                if event_occ/cases >= min_perc:
                    eventlist.append(event)
        log = log[log['concept:name'].isin(eventlist)]   
    elif option == 'business_rule':
        eventlist = []
        events = raw_log['concept:name'].unique()
        cases = raw_log['case:concept:name'].nunique()
        for event in events:
            event_occ = raw_log[raw_log['concept:name'] == event]['case:concept:name'].nunique()
            if event_occ/cases >= min_perc:
                eventlist.append(event)
        log = raw_log[raw_log['concept:name'].isin(eventlist)]    
    elif option == 'basic' or option == 'guidelines':
        log = raw_log
    else:
        log = raw_log
    return log, output


## Run the heuristic miner from PM4Py with additional options    
def heu_ext(raw_log, guidelines, option, suboption='', dependency_thresh=0, min_perc = 0):
    guidelines = prepare_guidelines(guidelines)
    dependency_thresh = 0
    log = prepare_log(raw_log, guidelines, option, suboption, min_perc)
    log_output = convertor.apply(log[0], parameters={constants.PARAMETER_CONSTANT_CASEID_KEY: "case:concept:name",
                                                      constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "concept:name",
                                                      constants.PARAMETER_CONSTANT_TIMESTAMP_KEY: "time:timestamp"})
    heu_net_plav = heuristics_miner.apply_heu(log_output, parameters={"dependency_thresh": 0})
    if option == 'detail':
        gviz = hn_visualizer.apply(heu_net_plav, parameters={"visualization_option": "detail", "rules": guidelines, "detail_option":suboption })
    elif option == 'conformance':
        gviz = hn_visualizer.apply(heu_net_plav, parameters={"min_perc_conf": min_perc, "visualization_option": option, "rules": guidelines})
    elif option == 'guidelines':
        gviz = hn_visualizer.apply(heu_net_plav, parameters={"visualization_option": "guidelines", "rules": guidelines})
    elif option == 'business_rule':
        gviz = hn_visualizer.apply(heu_net_plav, parameters={"visualization_option": "guidelines", "rules": guidelines})
    elif option == 'basic':
        gviz = hn_visualizer.apply(heu_net_plav) 
    traces = []
    cases = log[0]['case:concept:name'].unique()
    for case in cases:
        trace = ""
        df_case = log[0][log[0]['case:concept:name'] == case]
        for index, row in df_case.iterrows():
            event = row['concept:name']
            trace = trace + ", " + event 
        traces.append(trace) 
    traces_unique = set(traces)
    trace_output = "Aantal traces: " + str(len(traces_unique))
    return gviz[0], log[1], trace_output
    