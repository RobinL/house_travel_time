from mylibrary.secrets import app_id, app_key
def get_attempt(pc, times, dates):

    attempt = {
        "to": pc,
        "id": app_id,
        "key": app_key,
        "time": times[0],
        "date": dates[0],
        "nationalsearch": True}
                      
    param_dicts = []
    param_dicts.append(attempt)

    d1 = attempt.copy()
    d1["time"] =times[1]
    d1["date"] = dates[1]
    param_dicts.append(d1)

    d2 = attempt.copy()
    d2["time"] =times[2]
    d2["date"] = dates[2]
    param_dicts.append(d2)

    return param_dicts