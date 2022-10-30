
__all__ = ['MessageType', 'SpiderCommand', 'SpiderStatus', 'BowlStatus']

###################################################
# The types of messages sent between spider and skull
class MessageType:
    SPIDER_COMMAND = "SPIDERCOMMAND"
    SPIDER_STATUS = "SPIDERSTATUS"
    
    def __init__(self):
        pass

###################################################
# Messages telling the spider what to do
class SpiderCommand:
    SLEEP = "SLEEP"
    WAKEUP = "WAKEUP"
    AWAKE = "AWAKE"
    WALKOUT = "WALKOUT"
    PRESENTCANDY = "PRESENTCANDY"
    WALKHOME = "WALKHOME"
    
    def __init__(self):
        pass
    
###################################################
# Messages notifying listeners what the spider is doing
class SpiderStatus:
    SLEEPING = "SLEEPING"
    
    def __init__(self):
        pass
    
    
###################################################
# Messages notifying listeners about the status of the bowl
class BowlStatus:
    UNOCCUPIED = "UNOCCUPIED"
    OCCUPIED = "OCCUPIED"
    
    def __init__(self):
        pass
