# game engine for dqn training
from kalah import Board
from kalah import Kalah
from kalah import Side
from agent import RandomAgent
from agent import Move
import torch
import copy


class KalahEnvManager():
    kalah = None
    dqn_side = None
    op_side = None

    def __init__(self, device, side=Side.SOUTH):
        self.device = device
        self.dqn_side = side
        self.op_side = side.opposite()

    # reset the game to initial state
    def reset(self):
        self.kalah = Kalah(Board(7, 7))

    # give the initial state of the game to dqn agent
    # including: which side, game state, current reward
    def get_initial_state(self):
        # determine side
        # if dqn is South
        if self.dqn_side == Side.SOUTH:
            # state = initial state, reward = 0
            state = copy.deepcopy(self.kalah.getBoard().board)
            state[0] = state[0][1:]
            state[1] = state[1][:-1]
            state = torch.Tensor(state)
            reward = 0
        else:
            # if dqn is North
            possible_moves = RandomAgent().getPossibleMoves(
                        Side.SOUTH, self.kalah
                    )
            # choose randomly
            move = RandomAgent().random_move(possible_moves)
            move = Move(self.op_side, move)
            turn = self.kalah.makeMove(move)
            while turn!=self.dqn_side:
                # opAgent make moves util it is dqn's turn
                possible_moves = RandomAgent().getPossibleMoves(
                        Side.SOUTH, self.kalah
                    )
                # choose randomly
                move = RandomAgent().random_move(possible_moves)
                move = Move(self.op_side, move)
                turn = self.kalah.makeMove(move)
            # state = current board, reward = current score
            state = copy.deepcopy(self.kalah.getBoard().board)
            state[0] = state[0][1:]
            state[1] = state[1][:-1]
            state = torch.Tensor(state)
            reward = self.kalah.board.getSeedsInStore(self.dqn_side) - self.kalah.board.getSeedsInStore(self.op_side) 
        # return side, state, reward
        return self.dqn_side, state, reward
        

    # the dqn agent will make a move in the env
    # return next_state and reward back to the dqn agent
    def make_move(self, move):
        turn = self.kalah.makeMove(move)
        if turn == self.dqn_side:
            # still DQN make a move
            # return current board and current score
            state = copy.deepcopy(self.kalah.getBoard().board)
            state[0] = state[0][1:]
            state[1] = state[1][:-1]
            state = torch.Tensor(state)
            reward = self.kalah.board.getSeedsInStore(self.dqn_side) - self.kalah.board.getSeedsInStore(self.op_side)
        else:
            # opAgent make moves util it is dqn's turn
            possible_moves = RandomAgent().getPossibleMoves(
                        self.op_side, self.kalah
                    )
            # choose randomly
            move = RandomAgent().random_move(possible_moves)
            move = Move(self.op_side, move)
            turn = self.kalah.makeMove(move)
            while turn!=self.dqn_side:
                # opAgent make moves util it is dqn's turn
                possible_moves = RandomAgent().getPossibleMoves(
                        self.op_side, self.kalah
                    )
                # choose randomly
                move = RandomAgent().random_move(possible_moves)
                move = Move(self.op_side, move)
                turn = self.kalah.makeMove(move)
            # state = current board, reward = current score
            state = copy.deepcopy(self.kalah.getBoard().board)
            state[0] = state[0][1:]
            state[1] = state[1][:-1]
            state = torch.Tensor(state)
            reward = self.kalah.board.getSeedsInStore(self.dqn_side) - self.kalah.board.getSeedsInStore(self.op_side)
            # return current board and current score
            return state, reward
            

    # return whether the game is over
    def is_gameover(self):
        return self.kalah.gameOver()

    # check if the dqn agent wins the game
    def winner(self):
        final_score = self.kalah.board.getSeedsInStore(self.dqn_side) - self.kalah.board.getSeedsInStore(self.op_side)
        if final_score > 0:
            return True, final_score
        else:
            return False, final_score
