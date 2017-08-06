import requests
import json

import pandas as pd 
from mylibrary.connections import conn

from functools import lru_cache

import parse_tfl_json


def get_london_icscodes():
    sql = """
    select nlc, icscode, station_name from tt_h.all_stations where in_london = true
    """
    london_icscodes = list(pd.read_sql(sql, conn).loc[:, "icscode"])
    return london_icscodes

def get_cycle_info(icscode, tfl_dest):
    sql = """
    select * from tt_h.cycle_times_in_london 
    where icscode = '{}' and destination = '{}'
    """.format(icscode, tfl_dest)
    
    df = pd.read_sql(sql, conn)
    
    minutes = df.loc[df.index[0], "cycle_minutes"]
    miles = df.loc[df.index[0], "cycle_miles"]
    
    return {"minutes": minutes, "miles":miles}
    

def remove_journeys_not_arriving_clondon(journeys):
    new_journeys = []
    london_ics = get_london_icscodes()
    for journey in journeys:
        lastleg = journey["legs"][-1]
        ics = lastleg["arrivalPoint"]["icsCode"]
        if (ics in london_ics): 
            new_journeys.append(journey)
    return new_journeys

def add_cycle_and_total_time(journeys, tfl_dest):
    for journey in journeys:
        legs = journey["legs"]
        icscode = journey["legs"][-1]["arrivalPoint"]["icsCode"]
        
        times = get_cycle_info(icscode, tfl_dest)
        journey["cycle_minutes"] = times["minutes"]
        journey["cycle_miles"] = times["miles"]
        natrail_journey_minutes = parse_tfl_json.get_total_travel_time(legs) 
        journey["total_time"] = journey["cycle_minutes"] + natrail_journey_minutes
    return journeys

