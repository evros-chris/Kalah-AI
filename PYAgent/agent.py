from random import choice


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
            raise ValueError("Hole numbers must be >= 1, but " + str(hole) + " was given.")
        self.side = side
        self.hole = hole

    
    # @return The side of the board the player making the move is playing on.
    def getSide(self):
        return self.side


    #  @return The hole from which seeds are picked at the beginning of the
    #          move and distributed. It will be >= 1.
    def getHole(self):
        return self.hole


class RandomAgent():
    def getPossibleMoves(self, side, kalah):
        choice_list = []
        for i in range(1, 8):
            move = Move(side, i)
            if kalah.isLegalMove(move):
                choice_list.append(i)
        return choice_list


    def random_move(self, possible_moves):
        return choice(possible_moves)
