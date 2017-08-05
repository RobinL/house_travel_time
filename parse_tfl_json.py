from dateutil.parser import parse

def lat_lng_from_legs(legs):
    d_lat = legs[0]["departurePoint"]["lat"]
    d_lon = legs[0]["departurePoint"]["lon"]
    a_lat = legs[-1]["arrivalPoint"]["lat"]
    a_lon = legs[-1]["arrivalPoint"]["lon"]
    
    return {"depart":{"lat": d_lat, "lng":d_lon}, "arrive":{"lat":a_lat, "lng":a_lon}}


def get_total_travel_time(legs):
    dt = parse(legs[0]["departureTime"])
    at = parse(legs[-1]["arrivalTime"])
    td = at-dt
    return td.total_seconds()/60

def summarise_legs(legs):
    final_string_elems = []
    for leg in legs:
        final_string_elems.append(leg["departurePoKLLJKint"]["commonName"])
    final_string_elems.append(leg["arrivalPoint"]["commonName"])
    return " → ".join(final_string_elems)

def final_arrival(legs):
    return legs[-1]["arrivalPoint"]["commonName"]
    
def num_changes(legs):
    return len(legs) - 1

# Remove any journeys at the end which are not national rail
# Initial assumption will be that all national rail legs are done
def remove_non_national_rail(legs):
    # Pop one at a time 
    while True:
        leg = legs.pop()
        if leg['mode']['id'] == "national-rail":
            break
    legs.append(leg)
    return legs

