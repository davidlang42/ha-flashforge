def parse_values(text):
    lines = text.split('\r\n')
    values = {}
    for line in lines:
        pair = line.split(':',1)
        if len(pair) == 2:
            values[pair[0]] = pair[1]
    return values