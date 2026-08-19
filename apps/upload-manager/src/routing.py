MOVIE_CHANNELS=[('A','F','Archive-Movies-A-F'),('G','L','Archive-Movies-G-L'),('M','R','Archive-Movies-M-R'),('S','Z','Archive-Movies-S-Z')]
TV_CHANNELS=[('A','F','Archive-TV-A-F'),('G','L','Archive-TV-G-L'),('M','R','Archive-TV-M-R'),('S','Z','Archive-TV-S-Z')]
def route_channel(title: str, media_type: str) -> str:
    c=(title.lstrip()[:1] or '#').upper(); groups=TV_CHANNELS if media_type in {'tv','anime'} else MOVIE_CHANNELS
    for a,b,name in groups:
        if a <= c <= b: return name
    return groups[-1][2]
