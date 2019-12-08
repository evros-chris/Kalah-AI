from sys import stdin

from PyEnv.kalah import Move, Board, Kalah, Side
from PyEnv.agent import getPossibleMoves
from PyEnv.protocol import MoveTurn
from PyEnv.protocol import MsgType
import PyEnv.protocol as protocol

import torch
import PyAlpha.neural_nets as alpha
import copy
import sys


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

    value_net = alpha.MLP(2, 8)
    value_net.load_state_dict(torch.load("model/max_score", map_location=torch.device('cpu')))
    value_net.eval()

    minimax_depth = 5
    eps = 0.35

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
                    # possible_moves = [1, 2, 3, 4, 5, 6, 7]
                    # move_hole = RandomAgent().random_move(possible_moves)
                    # dqn makes a move
                    state = copy.deepcopy(kalah.getBoard().board)
                    if side == Side.SOUTH:
                        state[0] = state[0]
                        state[1] = state[1]
                    else:
                        state_0 = copy.deepcopy(state[0])
                        state[0] = state[1]
                        state[1] = state_0
                    state = torch.Tensor(state)
                    value, move_hole = alpha.MiniMaxAgent.minimax_dl(
                        kalah, side, side, minimax_depth, -sys.maxsize, sys.maxsize, value_net, eps
                    )
                    choice = protocol.createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice + "\n")
                else:
                    side = Side.NORTH
            elif msg_type == MsgType.SWAP:
                side = side.opposite()
                w.write("our side: " + str(side) + '\n')
                state = copy.deepcopy(kalah.getBoard().board)
                if side == Side.SOUTH:
                    state[0] = state[0]
                    state[1] = state[1]
                else:
                    state_0 = copy.deepcopy(state[0])
                    state[0] = state[1]
                    state[1] = state_0
                state = torch.Tensor(state)
                value, move_hole = alpha.MiniMaxAgent.minimax_dl(
                        kalah, side, side, minimax_depth, -sys.maxsize, sys.maxsize, value_net, eps
                    )
                choice = protocol.createMoveMsg(move_hole)
                sendMsg(choice)
                w.write("msg sent: " + choice + "\n")
            else:
                move_turn = protocol.interpretStateMsg(message, kalah.board)
                if not move_turn.end and move_turn.again:
                    # our turn, make a move
                    # get all legal moves
                    # possible_moves = [1,2,3,4,5,6,7]
                    # possible_moves = agent.getPossibleMoves(
                        # side, kalah
                    # )
                    # choose randomly
                    # move_hole = RandomAgent().random_move(possible_moves)
                    # choice = protocol.createMoveMsg(move_hole)
                    # dqn makes a move
                    state = copy.deepcopy(kalah.getBoard().board)
                    if side == Side.SOUTH:
                        state[0] = state[0]
                        state[1] = state[1]
                    else:
                        state_0 = copy.deepcopy(state[0])
                        state[0] = state[1]
                        state[1] = state_0
                    state = torch.Tensor(state)
                    value, move_hole = alpha.MiniMaxAgent.minimax_dl(
                        kalah, side, side, minimax_depth, -sys.maxsize, sys.maxsize, value_net, eps
                    )
                    if kalah.board.getSeedsInStore(side) + \
                kalah.board.getSeedsInStore(side.opposite()) > 65:
                        eps = 1
                        minimax_depth = 7
                    choice = protocol.createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice + "\n")