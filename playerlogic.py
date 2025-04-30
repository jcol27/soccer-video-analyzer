class Player:
    def __init__(self, playerName):
        self.playerName = playerName
    
    def serialize(self):
        return self.playerName
