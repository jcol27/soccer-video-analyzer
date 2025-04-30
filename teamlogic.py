from playerlogic import *
from matchlogic import *

class Team:
    def __init__(self, name, players, matches):
        self.name = name
        self.players = []
        self.matches = []

        # Read team stored players
        for player in players:
            player = Player(player)
            self.players.append(player)
        
        # Read team stored matches
        self.matches = matches


    def to_dict(self):
        return {
            "name": self.name,
            "players": self.players,
            "matches": [m.to_dict() for m in self.matches]
        }

    @classmethod
    def from_dict(cls, name, data):
        name = name,
        players = data.get("players", [])
        matches_data = data.get("matches", [])
        matches = [Match.from_dict(m) for m in matches_data]
        return cls(name=name, players=players, matches=matches)