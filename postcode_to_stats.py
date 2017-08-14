from mylibrary.connections import cursor, conn
import pandas as pd
from google import get_drive_info


def format_pc(pc):
    pc = pc.upper()
    if len(pc) == 6:
        pc = " ".join([pc[:3], pc[3:7]])
    return pc

def pc_to_lat_lng(pc):
    
    sql = """
    select * from tt_h.all_postcodes
    where postcode = '{}'
    """
    
    df = pd.read_sql(sql.format(format_pc(pc)), conn)
    if len(df) != 1:
        print("Found {} records when tried to lookup that postcode".format(len(df)))
    row = df.iloc[0]
    lat = row["lat"]
    lng = row["lng"]
    return {"lat": lat, "lng":lng, "pc":pc}

def get_distance_crow_flies(source_lat, source_lng, dest_lat, dest_lng):

    sql = """
        select st_distance(
            ST_Transform(ST_SetSRID(ST_MakePoint({source_lng}, {source_lat}), 4326), 27700),
            ST_Transform(ST_SetSRID(ST_MakePoint({dest_lng}, {dest_lat}), 4326), 27700)
        ) as distance
    
    """
    
    cursor.execute(sql.format(**locals()))
    
    distance_meters = cursor.fetchone()[0]
    return {"distance_crowflies_km":  distance_meters/1000,
            "distance_crowflies_mi": distance_meters/1609.34}

def get_stations_in_buffer(lat, lng, buffer_size_m = 5000):

    sql =    """
    select * from tt_h.parsed_rail_journeys_one_row_per_station_view as prj
    where  st_contains(st_buffer(st_transform(ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326), 27700), {buffer_size_m}), prj.geom)
    """

    df = pd.read_sql(sql.format(**locals()), conn)
    return df
    
def get_stations_around_pc(pc):
    pc = format_pc(pc)
    lat_lng = pc_to_lat_lng(pc)
    df = get_stations_in_buffer(lat_lng["lat"], lat_lng["lng"])
    return df



# Assume can cycle to station at 10mph rather than doing a google maps lookup

def add_cycle_to_station(df, pc):
    for r in df.iterrows():
        index = r[0]
        row = r[1]
        
        dest_lat = row["depart_lat"]
        dest_lng = row["depart_lng"]
        
        dep_lat_lng = pc_to_lat_lng(pc)
        dep_lat = dep_lat_lng["lat"]
        dep_lng = dep_lat_lng["lng"]
        
        distance = get_distance_crow_flies(dep_lat, dep_lng, dest_lat, dest_lng)
        df.loc[index, "home_to_station_crowflies_miles"] = distance["distance_crowflies_mi"]
        df.loc[index, "home_to_station_crowflies_minutes"] = (distance["distance_crowflies_mi"]/10)*60
    return df

def pc_to_102pf(pc):
    df = get_stations_around_pc(pc)
    df = add_cycle_to_station(df, pc)
    df["total_minutes"] = df["home_to_station_crowflies_minutes"] + df["total_journeytime_cw"]
    df = df.sort_values("total_minutes")
    row = df.iloc[0]
    
    return {
        "total_time": row["total_minutes"], 
        "cycle_time_home": row["home_to_station_crowflies_minutes"],
        "train_time": row["natrail_journey_minutes_pf"],
        "cycle_time_london": row["total_journeytime_pf"] - row["natrail_journey_minutes_pf"],
        "route": row["natrail_journey_summary_cw"]
    }

def get_stats(pc):
    pc = format_pc(pc)
    pc_no_space = pc.replace(" ", "")

    stats = pc_to_102pf(pc)
    abingdon = get_drive_info(origin_pc = pc_no_space, dest_pc = "OX145FP")
    stats["abingdon_drive_time"] = abingdon["minutes"]

    newport = get_drive_info(origin_pc = pc_no_space, dest_pc = "CB113QY")
    stats["newport_drive_time"] = newport["minutes"]
    
    chelmsford = get_drive_info(origin_pc = pc_no_space, dest_pc = "CM25LB")
    stats["chelmsford_drive_time"] = chelmsford["minutes"]
    stats["pc"] = pc
    
    return stats
    

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

 # use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('google_secret.json', scope)
client = gspread.authorize(creds)
gc = gspread.authorize(creds)
gc_sheet = client.open("Houses").worksheet("auto")
gc_rows_in_use = client.open("Houses").worksheet("rows_in_use")

def stats_to_sheets(stats):
    new_row_index = int(gc_rows_in_use.cell(1,1).value) + 1
    gc_sheet.insert_row(list(stats.values()), new_row_index)
    print("successfully wrote stats to row {}".format(new_row_index))

def pc_to_stats_in_sheets(pc):
    stats = get_stats(pc)
    stats_to_sheets(stats)
    


