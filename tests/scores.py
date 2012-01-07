

def score(category, points = True):
    def wrapped(func):
            func.category = category
            func.points = points
            return func
    return wrapped

class Project(object):
    
    def __init__(self, name, points):
        self.name = name
        self.points = points
        self.categories = {}
        self.lcategories = []
        
    def add_category(self, cid, name, points):
        self.categories[cid] = (name, points)
        self.lcategories.append(cid)
    

PROJ_1A = Project("Project 1a", 50)    
PROJ_1B = Project("Project 1b", 100)    
PROJ_1C = Project("Project 1c", 100)    

PROJECTS = [PROJ_1A, PROJ_1B, PROJ_1C]

PROJ_1A.add_category("BASIC_CONNECTION", "Basic Connection", 50)

PROJ_1B.add_category("CONNECTION_REGISTRATION", "Connection Registration", 40)
PROJ_1B.add_category("PRIVMSG_NOTICE", "PRIVMSG and NOTICE", 30)
PROJ_1B.add_category("PING_PONG", "PING and PONG", 2.5)
PROJ_1B.add_category("MOTD", "MOTD", 5)    
PROJ_1B.add_category("LUSERS", "LUSERS", 10)
PROJ_1B.add_category("WHOIS", "WHOIS", 10)
PROJ_1B.add_category("ERR_UNKNOWN", "ERR_UNKNOWN", 2.5)
    
PROJ_1C.add_category("CHANNEL_JOIN", "JOIN", 15)
PROJ_1C.add_category("CHANNEL_PRIVMSG_NOTICE", "PRIVMSG and NOTICE to channels", 15)
PROJ_1C.add_category("CHANNEL_PART", "PART", 10)
PROJ_1C.add_category("CHANNEL_TOPIC", "TOPIC", 10)
PROJ_1C.add_category("MODES", "User and channel modes", 25)
PROJ_1C.add_category("AWAY", "AWAY", 5)
PROJ_1C.add_category("NAMES", "NAMES", 5)
PROJ_1C.add_category("LIST", "LIST", 5)
PROJ_1C.add_category("WHO", "WHO", 5)
PROJ_1C.add_category("UPDATE_1B", "UPDATE_1B", 5)
