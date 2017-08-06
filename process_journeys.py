import requests
import json

import pandas as pd 
from mylibrary.connections import conn

from functools import lru_cache

import parse_tfl_json
from google import get_cycle_info


def get_london_icscodes():
    sql = """
    select nlc, icscode, station_name from tt_h.all_stations where in_london = true
    """
    london_icscodes = list(pd.read_sql(sql, conn).loc[:, "icscode"])
    return london_icscodes



@lru_cache(maxsize=None)
def get_cycle_time_mem(origin_lat, origin_lng, dest_pc):
    return get_cycle_info(origin_lat = origin_lat, origin_lng = origin_lng, dest_pc= dest_pc)

def remove_nonlondon_journeys(journeys):
    new_journeys = []
    london_ics = get_london_icscodes()
    for journey in journeys:
        lastleg = journey["legs"][-1]
        ics = lastleg["arrivalPoint"]["icsCode"]
        if (ics in london_ics): 
            new_journeys.append(journey)
    return journeys

def add_cycle_and_total_time(journeys, tfl_dest):
    for journey in journeys:
        legs = journey["legs"]
        lat = journey["legs"][-1]["arrivalPoint"]["lat"]
        lng = journey["legs"][-1]["arrivalPoint"]["lon"]
        times = get_cycle_time_mem(lat, lng, tfl_dest)
        journey["cycle_minutes"] = times["minutes"]
        journey["cycle_miles"] = times["miles"]
        natrail_journey_minutes = parse_tfl_json.get_total_travel_time(legs) 
        journey["total_time"] = journey["cycle_minutes"] + natrail_journey_minutes
    return journeys

