class Location(object):
    owner = str
    name = str
    pos_x = float
    pos_y = float
    pos_z = float
    shape = str
    radius = float
    region = str

    def __init__(self, **kwargs):
        """ populate player-data """
        for (k, v) in kwargs.iteritems():
            setattr(self, k, v)
