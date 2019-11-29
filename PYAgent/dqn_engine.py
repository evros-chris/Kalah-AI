# game engine for dqn training
from kalah import Board
from kalah import Kalah


class KalahEnvManager():
    kalah = None
    dqn_side = None

    def __init__(self, device):
        self.device = device

    # reset the game to initial state
    def reset(self):
        board = Board(7, 7)
        self.kalah = Kalah(board)

    # give the initial state of the game to dqn agent
    # including: which side, game state, current reward
    def get_initial_state(self):
        # determine side
        # if dqn is South
        # state = initial state, reward = 0
        # if dqn is North
        # opAgent make moves util it is dqn's turn
        # state = current board, reward = current score
        # return side, state, reward
        pass

    # the dqn agent will make a move in the env
    # return next_state and reward back to the dqn agent
    def make_move(self, move):
        turn = self.kalah.makeMove(move)
        if turn == self.dqn_side:
            # still DQN make a move
            # return current board and current score
            pass
        else:
            # opAgent make moves util it is dqn's turn
            # return current board and current score
            pass

    # return whether the game is over
    def is_gameover(self):
        return self.kalah.gameOver()

    # check if the dqn agent wins the game
    def winner(self):
        pass
