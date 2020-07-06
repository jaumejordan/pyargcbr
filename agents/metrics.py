from datetime import datetime
from time import mktime


def do_dist(a: str, b: str):
    ra, rb = None, None
    # int ?
    try:
        ra = int(a)
        rb = int(b)
    except ValueError:
        pass
    # float ?
    try:
        ra = float(a)
        rb = float(b)
    except ValueError:
        pass
    # datetime ?
    try:
        datetime_format = '%m/%d/%y %H:%M:%S'
        ra = mktime(datetime.strptime(a, datetime_format).timetuple())
        rb = mktime(datetime.strptime(b, datetime_format).timetuple())
    except ValueError:
        pass

    if ra and rb:
        return abs(ra - rb)

    # Just two str
    return levenshtein_distance(a, b)


def levenshtein_distance(x: str, y: str):
    current_row = [0] * (len(x) + 1)
    previous_row = [0] * (len(x) + 1)
    for i in range(1, len(x) + 1):
        current_row[i] = current_row[i - 1] + 1

    for j in range(1, len(y) + 1):
        previous_row, current_row = current_row, previous_row
        current_row[0] = previous_row[0] + 1
        for i in range(1, len(x) + 1):
            current_row[i] = min(current_row[i - 1] + 1,
                                 previous_row[i] + 1,
                                 previous_row[i - 1] + (x[i - 1] != y[j - 1]))

    return current_row[len(x)]
