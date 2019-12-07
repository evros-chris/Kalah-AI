from sys import stdin

from kalah import Move
from agent import getPossibleMoves
from kalah import Board
from kalah import Kalah
from kalah import Side
from protocol import MoveTurn
from protocol import MsgType
import agent
import protocol

import torch
import dqn
import copy


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
    strategy = dqn.EpsilonGreedyStrategy(1, 1, 0)
    agent = dqn.Agent(strategy=strategy, num_actions=7, device='cpu')

    policy_net = dqn.DQN(2, 7)
    policy_net.load_state_dict(torch.load("dqn_model", map_location=torch.device('cpu')))
    policy_net.eval()

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
                        state[0] = state[0][1:]
                        state[1] = state[1][1:]
                    else:
                        state_0 = copy.deepcopy(state[0][1:])
                        state[0] = state[1][1:]
                        state[1] = state_0
                    state = torch.Tensor(state)
                    move_hole = agent.select_action_valid(state, policy_net, side, kalah)
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
                    state[0] = state[0][1:]
                    state[1] = state[1][1:]
                else:
                    state_0 = copy.deepcopy(state[0][1:])
                    state[0] = state[1][1:]
                    state[1] = state_0
                state = torch.Tensor(state)
                move_hole = agent.select_action_valid(state, policy_net, side, kalah)
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
                        state[0] = state[0][1:]
                        state[1] = state[1][1:]
                    else:
                        state_0 = copy.deepcopy(state[0][1:])
                        state[0] = state[1][1:]
                        state[1] = state_0
                    state = torch.Tensor(state)
                    move_hole = agent.select_action_valid(state, policy_net, side, kalah)
                    choice = protocol.createMoveMsg(move_hole)
                    sendMsg(choice)
                    w.write("msg sent: " + choice + "\n")
