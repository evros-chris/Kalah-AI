from sys import stdin

from PyEnv.agent import RandomAgent
from PyEnv.kalah import Board, Kalah, Side
from PyEnv.protocol import MsgType
import PyEnv.agent as agent
import PyEnv.protocol as protocol

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
            msg_type = protocol.getMsgType(message)
            w.write("msg type: " + str(msg_type) + '\n')
            if msg_type == MsgType.END:
                # game over
                w.write("Game Over")
                break
            elif msg_type == MsgType.START:
                if protocol.interpretStartMsg(message):
                    # South, start the game
                    side = Side.SOUTH
                    w.write("our side: " + str(side) + '\n')
                    # choose randomly
                    possible_moves = [1, 2, 3, 4, 5, 6, 7]
                    move_hole = RandomAgent().random_move(possible_moves)
                    choice = protocol.createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice + "\n")
                else:
                    side = Side.NORTH
            else:
                move_turn = protocol.interpretStateMsg(message, kalah.board)
                if not move_turn.end and move_turn.again:
                    # our turn, make a move
                    # get all legal moves
                    # possible_moves = [1,2,3,4,5,6,7]
                    possible_moves = agent.getPossibleMoves(
                        side, kalah
                    )
                    # choose randomly
                    move_hole = RandomAgent().random_move(possible_moves)
                    choice = protocol.createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice + "\n")
