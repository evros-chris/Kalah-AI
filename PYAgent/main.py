from sys import stdin

from agent import Move
from agent import RandomAgent
from kalah import Board
from kalah import Kalah
from kalah import Side
from protocol import MoveTurn
from protocol import MsgType
from protocol import Protocol


# Sends a message to the game engine.
# @param msg The message.
def sendMsg(msg):
    print(msg, flush=True)


#  * Receives a message from the game engine. Messages are terminated by
#  * a '\n' character.
#  * @return The message.
#  * @throws IOException if there has been an I/O error.
def recvMsg():
    message = stdin.readline()
    return message


if __name__ == "__main__":
    with open("log.txt", "w") as w:
        board = Board(7, 7)
        kalah = Kalah(board)
        side = None
        while 1:
            message = recvMsg()
            w.write("received: " + message)
            msg_type = Protocol().getMsgType(message)
            w.write("msg type: " + str(msg_type) + '\n')
            if msg_type == MsgType.END:
                # game over
                w.write("Game Over")
                break
            elif msg_type == MsgType.START:
                if Protocol().interpretStartMsg(message):
                    # South, start the game
                    side = Side.SOUTH
                    w.write("our side: " + str(side) + '\n')
                    # choose randomly
                    possible_moves = [1, 2, 3, 4, 5, 6, 7]
                    move_hole = RandomAgent().random_move(possible_moves)
                    choice = Protocol().createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice)
                else:
                    side = Side.NORTH
            else:
                move_turn = Protocol().interpretStateMsg(message, kalah.board)
                if not move_turn.end and move_turn.again:
                    # our turn, make a move
                    # get all legal moves
                    # possible_moves = [1,2,3,4,5,6,7]
                    possible_moves = RandomAgent().getPossibleMoves(
                        side, kalah
                    )
                    # choose randomly
                    move_hole = RandomAgent().random_move(possible_moves)
                    choice = Protocol().createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice)
