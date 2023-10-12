from geopy.distance import distance as _distance

def distance(coords1, coords2):
    return _distance(coords1, coords2).miles
