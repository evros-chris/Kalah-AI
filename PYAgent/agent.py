class Move:
    # The side of the board the player making the move is playing on.
    side = None
    # The hole from which seeds are picked at the beginning of the move and
    # distributed. It has to be >= 1.
    hole = None


    #  @param side The side of the board the player making the move is playing
    #        on.
    #  @param hole The hole from which seeds are picked at the beginning of
    #          the move and distributed. It has to be >= 1.
    #  @throws IllegalArgumentException if the hole number is not >= 1.
    def __init__(self, side, hole):
        if hole < 1:
            raise ValueError("Hole numbers must be >= 1, but " + hole + " was given.")
        self.side = side
        self.hole = hole

    
    # @return The side of the board the player making the move is playing on.
    def getSide(self):
        return side


    #  @return The hole from which seeds are picked at the beginning of the
    #          move and distributed. It will be >= 1.
    def getHole(self):
        return hole


from random import choice
class random_agent():
    
    def random_move(self, possible_moves):
        return choice(possible_moves)