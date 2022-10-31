
__all__ = ['MessageType', 'SpiderCommand', 'SpiderStatus', 'BowlStatus', 'MakeSpiderCommandMessage', 'MakeSpiderStatusMessage', 'MakeBowlStatusMessage']

###################################################
# The types of messages sent between spider and skull
class MessageType:
    SPIDER_COMMAND = "SPIDER_COMMAND"
    SPIDER_STATUS = "SPIDER_STATUS"
    BOWL_STATUS = "BOWL_STATUS"
    
    def __init__(self):
        pass

###################################################
# Messages telling the spider what to do
class SpiderCommand:
    SLEEP = "SLEEP"
    WAKEUP = "WAKEUP"
    ASK_CANDY = "ASK_CANDY"
    DELIVER_CANDY = "DELIVER_CANDY"
    PRESENT_CANDY = "PRESENT_CANDY"
    GO_HOME = "GO_HOME"
    
    def __init__(self):
        pass
    
###################################################
# Messages notifying listeners what the spider is doing
class SpiderStatus:
    SLEEPING = "SLEEPING"
    AWAKE = "AWAKE"
    CANDY_QUESTION = "CANDY_QUESTION"
    CANDY_QUESTION_DONE = "CANDY_QUESTION_DONE"
    DELIVERING_CANDY = "DELIVERING_CANDY"
    PRESENTING_CANDY = "PRESENTING_CANDY"
    WALKING_HOME = "WALKING_HOME"
    
    def __init__(self):
        pass
    
###################################################
# Messages notifying listeners about the status of the bowl
class BowlStatus:
    UNOCCUPIED = "UNOCCUPIED"
    OCCUPIED = "OCCUPIED"
    
    def __init__(self):
        pass


def MakeSpiderCommandMessage( cmd : SpiderCommand ):
    return str(MessageType.SPIDER_COMMAND) + ":" + str(cmd)

def MakeSpiderStatusMessage( status : SpiderStatus ):
    return str(MessageType.SPIDER_STATUS) + ":" + str(status)

def MakeBowlStatusMessage( status : BowlStatus ):
    return str(MessageType.BOWL_STATUS) + ":" + str(status)
