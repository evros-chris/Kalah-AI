import enum
class Side(enum.Enum):
    NORTH = 0
    SOUTH = 1


    def opposite(self):
        if self == NORTH:
            return SOUTH
        elif self == SOUTH:
            return NORTH
        else:
            raise ValueError("side not defined")


class Board:
    NORTH_ROW = 0
    SOUTH_ROW = 1

    holes = 7

    board = []


    def indexOfSide(self, side):
        if side == Side.NORTH:
            return self.NORTH_ROW
        elif side == Side.SOUTH: 
            return self.SOUTH_ROW
        else:
            raise ValueError("side not defined")


    def __init__ (self, holes=7, seeds=7, from_original=False, original=None):
        if ~from_original:
            if holes < 1:
                raise ValueError("There has to be at least one hole, but " + holes + " were requested.")
            if seeds < 0:
                raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

            self.holes = holes
            
            north_board = []
            south_board = []
            for i in range(holes+1):
                north_board.append(seeds)
                south_board.append(seeds)

            self.board.append(north_board)
            self.board.append(south_board)
        else:
            if original == None:
                raise ValueError("no original board provided")
            self.holes = original.holes
            north_board = []
            south_board = []
            for i in range(holes+1):
                north_board[i] = original.board[self.NORTH_ROW][i]
                south_board[i] = original.board[self.SOUTH_ROW][i]
            self.board.append(north_board)
            self.board.append(south_board)


    def clone(self):
        return Board(self, from_original=True, original=self)


    def getNoOfHoles(self):
        return self.holes


    def getSeeds(self, side, hole):
        if hole < 1 or hole > self.holes:
            raise ValueError("Hole number must be between 1 and " + str(len(board[self.NORTH_ROW]) - 1) + " but was " + hole + ".")

        return self.board[self.indexOfSide(side)][hole]


    def setSeeds(self, side, hole, seeds):
        if hole < 1 or hole > self.holes:
            raise ValueError("Hole number must be between 1 and " + str(len(board[self.NORTH_ROW])- 1) + " but was " + hole + ".")
        if seeds < 0:
            raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

        self.board[self.indexOfSide(side)][hole] = seeds
        # self.setChanged()


    def addSeeds(self, side, hole, seeds):
        if hole < 1 or hole > self.holes:
            raise ValueError("Hole number must be between 1 and " + str(len(board[self.NORTH_ROW]) - 1) + " but was " + hole + ".")
        if seeds < 0:
            raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

        self.board[self.indexOfSide(side)][hole] += seeds
        # self.setChanged()


    def getSeedsOp(self, side, hole):
        if hole < 1 or hole > self.holes:
            raise ValueError("Hole number must be between 1 and " + holes + " but was " + hole + ".")

        return self.board[1-self.indexOfSide(side)][holes+1-hole]
    

    def setSeedsOp(self, side, hole, seeds):
        if hole < 1 or hole > self.holes:
            raise ValueError("Hole number must be between 1 and " + str(len(board[self.NORTH_ROW]) - 1) + " but was " + hole + ".")
        if seeds < 0:
            raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

        self.board[1-self.indexOfSide(side)][self.holes+1-hole] = seeds
        # self.setChanged()

    
    def addSeedsOp(self, side, hole, seeds):
        if hole < 1 or hole > holes:
            raise ValueError("Hole number must be between 1 and " + str(len(board[self.NORTH_ROW]) - 1) + " but was " + hole + ".")
        if seeds < 0:
            raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

        self.board[1-self.indexOfSide(side)][holes+1-hole] += seeds
        # self.setChanged()


    def getSeedsInStore(self, side):
        return self.board[self.indexOfSide(side)][0]


    def setSeedsInStore(self, side, seeds):
        if seeds < 0:
            raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

        self.board[self.indexOfSide(side)][0] = seeds
        # self.setChanged()


    def addSeedsToStore(self, side, seeds):
        if seeds < 0:
            raise ValueError("There has to be a non-negative number of seeds, but " + seeds + " were requested.")

        self.board[self.indexOfSide(side)][0] += seeds
        # self.setChanged()


    def toString(self):
        boardString = []

        boardString.append(self.board[self.NORTH_ROW][0] + "  --")
        for i in range(self.holes, 0, -1):
            boardString.append("  " + self.board[self.NORTH_ROW][i])
        boardString.append("\n")
        for i in range(1, self.holes+1):
            boardString.append(self.board[self.SOUTH_ROW][i] + "  ");
        boardString.append("--  " + self.board[self.SOUTH_ROW][0] + "\n")

        return str(boardString)


from agent import Move
class Kalah:
    board = []


    def __init__(self, board):
        if board == None:
            raise TypeError
        self.board = board


    def getBoard(self):
        return self.board


    def isLegalMove(self, move):
        return isLegalMove(board, move)


    def makeMove(self, move):
        return makeMove(board, move)

    
    def gameOver(self):
        return gameOver(board)

    
    def isLegalMove(self, board, move):
        # check if the hole is existent and non-empty:
        return (move.getHole() <= board.getNoOfHoles()) \
                and (board.getSeeds(move.getSide(), move.getHole()) != 0)

    
    def makeMove(self, board, move):
        # from the documentation:
        #   "1. The counters are lifted from this hole and sown in anti-clockwise direction, starting
        #       with the next hole. The player's own kalahah is included in the sowing, but the
        #       opponent's kalahah is skipped.
        #    2. outcome:
        #     	1. if the last counter is put into the player's kalahah, the player is allowed to
        #     	   move again (such a move is called a Kalah-move);
        #     	2. if the last counter is put in an empty hole on the player's side of the board
        #     	   and the opposite hole is non-empty,
        #     	   a capture takes place: all stones in the opposite opponents pit and the last
        #     	   stone of the sowing are put into the player's store and the turn is over;
        #     	3. if the last counter is put anywhere else, the turn is over directly.
        #    3. game end:
        #     	The game ends whenever a move leaves no counters on one player's side, in
        #     	which case the other player captures all remaining counters. The player who
        #     	collects the most counters is the winner."



        # pick seeds:
        seedsToSow = board.getSeeds(move.getSide(), move.getHole())
        board.setSeeds(move.getSide(), move.getHole(), 0)

        holes = board.getNoOfHoles()
        receivingPits = 2*holes + 1;  # sow into: all holes + 1 store
        rounds = seedsToSow / receivingPits;  # sowing rounds
        extra = seedsToSow % receivingPits;  # seeds for the last partial round
        # the first "extra" number of holes get "rounds"+1 seeds, the
        #    remaining ones get "rounds" seeds 

        # sow the seeds of the full rounds (if any):
        if rounds != 0:
            for hole in range(1, holes+1):
                board.addSeeds(Side.NORTH, hole, rounds)
                board.addSeeds(Side.SOUTH, hole, rounds)
            board.addSeedsToStore(move.getSide(), rounds)

        # sow the extra seeds (last round):
        sowSide = move.getSide()
        sowHole = move.getHole()  # 0 means store
        while extra > 0:
            # go to next pit:
            sowHole += 1
            if sowHole == 1:  # last pit was a store
                sowSide = sowSide.opposite()
            if sowHole > holes:
                if sowSide == move.getSide():
                    sowHole = 0;  # sow to the store now
                    board.addSeedsToStore(sowSide, 1)
                    continue
                else:
                    sowSide = sowSide.opposite()
                    sowHole = 1
            # sow to hole:
            board.addSeeds(sowSide, sowHole, 1)
            extra -= 1

        # capture:
        # last seed was sown on the moving player's side ...
        # ... not into the store ...
        # ... but into an empty hole (so now there's 1 seed) ...
        # ... and the opposite hole is non-empty
        if sowSide == move.getSide() \
            and sowHole > 0  \
            and board.getSeeds(sowSide, sowHole) == 1 \
            and board.getSeedsOp(sowSide, sowHole) > 0:
            board.addSeedsToStore(move.getSide(), 1 + board.getSeedsOp(move.getSide(), sowHole))
            board.setSeeds(move.getSide(), sowHole, 0)
            board.setSeedsOp(move.getSide(), sowHole, 0)

        # game over?
        finishedSide = None
        if holesEmpty(board, move.getSide()):
            finishedSide = move.getSide()
        elif holesEmpty(board, move.getSide().opposite()):
            finishedSide = move.getSide().opposite()
            #  note: it is possible that both sides are finished, but then
            #    there are no seeds to collect anyway 
        if finishedSide != None:
            # collect the remaining seeds:
            seeds = 0;
            collectingSide = finishedSide.opposite()
            for hole in range(1, holes+1):
                seeds += board.getSeeds(collectingSide, hole)
                board.setSeeds(collectingSide, hole, 0)
            board.addSeedsToStore(collectingSide, seeds)

        board.notifyObservers(move)

        # who's turn is it?
        if sowHole == 0:  # the store (implies (sowSide == move.getSide()))
            return move.getSide()  # move again
        else:
            return move.getSide().opposite()


    def holesEmpty (self, board, side):
        for hole in range(1, board.getNoOfHoles()+1):
            if board.getSeeds(side, hole) != 0:
                return False
        return True

    
    def gameOver(self, board):
        #  The game is over if one of the agents can't make another move.

        return holesEmpty(board, Side.NORTH) or holesEmpty(board, Side.SOUTH)


    def getPossibleMoves(self, side):
        choice_list = []
        for i in range(1, 8):
            move = Move(side, i)
            if self.isLegalMove(move):
                choice_list.append(i)
        return choice_list