import enum
class MsgType(enum.Enum):
    START = 0
    STATE = 1
    END = 2


class MoveTurn:
    end = False
    again = False
    move = -2


class InvalidMessageException(Exception):
    def __init__(self, exmsg):
        super().__init__(exmsg)


from kalah import Side
from kalah import Board
class Protocol:
    def createMoveMsg(self, hole):
        return "MOVE;" + str(hole)
    

    def createSwapMsg(self):
        return "SWAP"


    def getMsgType(self, msg):
        if msg.startswith("START;"):
            return MsgType.START;
        elif msg.startswith("CHANGE;"):
            return MsgType.STATE;
        elif msg == "END\n":
            return MsgType.END
        else:
            raise InvalidMessageException("Could not determine message type.")


    def interpretStartMsg(self, msg):
        if msg[len(msg) -1] != '\n':
            raise InvalidMessageException("Message not terminated with 0x0A character.")

        position = msg[6: len(msg)-1]
        if position == "South":
            # South starts the game
            return True
        elif position == "North":
            return False
        else:
            raise InvalidMessageException("Illegal position parameter: " + position)

    
    def interpretStateMsg(self, msg, board):
        moveTurn = MoveTurn()

        if msg[len(msg)-1] != '\n':
            raise InvalidMessageException("Message not terminated with 0x0A character.")

        msgParts = msg.split(";")
        if len(msgParts) != 4:
            raise InvalidMessageException("Missing arguments.")

        # msgParts[0] is "CHANGE"

        # 1st argument: the move (or swap)
        if msgParts[1] == "SWAP":
            moveTurn.move = -1;
        else:
            try:
                moveTurn.move = int(msgParts[1])
            except Exception as e:
                raise InvalidMessageException("Illegal value for move parameter" + str(e))

        # 2nd argument: the board
        boardParts = msgParts[2].split(",")
        # if len(boardParts) % 2 != 0:
        #     raise ValueError("Malformed board: odd number of entries.")
        if 2*(board.getNoOfHoles()+1) != len(boardParts):
            raise InvalidMessageException('Board dimensions in message (" \
                    + str(len(boardParts)) + " entries) are not as expected (" \
                    + 2*(board.getNoOfHoles()+1) + " entries).')
        try:
            # holes on the north side:
            for i in range (board.getNoOfHoles()):
                board.setSeeds(Side.NORTH, i+1, int(boardParts[i]))
            # northern store:
            board.setSeedsInStore(Side.NORTH, int(boardParts[board.getNoOfHoles()]))
			# holes on the south side:
            for i in range(board.getNoOfHoles()):
                board.setSeeds(Side.SOUTH, i+1, int(boardParts[i+board.getNoOfHoles()+1]))
            # southern store:
            board.setSeedsInStore(Side.SOUTH, int(boardParts[2*board.getNoOfHoles()+1]))
        except Exception as e:
            raise InvalidMessageException("Illegal value for seed count: " + str(e))

        # 3rd argument: who's turn?
        moveTurn.end = False
        if msgParts[3] == "YOU\n":
            moveTurn.again = True
        elif msgParts[3] == "OPP\n":
            moveTurn.again = False
        elif msgParts[3] == "END\n":
            moveTurn.end = True
            moveTurn.again = False
        else:
            raise InvalidMessageException("Illegal value for turn parameter: " + msgParts[3])

        return moveTurn