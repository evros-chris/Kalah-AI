import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
import copy
import sys
import math
from PyEnv.kalah import Side, Move
import random
from collections import namedtuple


class EpsilonGreedyStrategy():
    def __init__(self, start, end, decay):
        # starting, ending, decay values of epsilon
        self.start = start
        self.end = end
        self.decay = decay

    # exponential decay
    def get_exploration_rate(self, current_step):
        return self.end + (self.start - self.end) * \
            math.exp(-1. * current_step * self.decay)

# Experience
Experience = namedtuple(
    'Experience',
    ('state', 'score'),
)

class ReplayMemory():
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.exp_count = 0

    def exp_save(self, experience):
        if len(self.memory) < self.capacity:
            self.memory.append(experience)
        else:
            self.memory[self.exp_count % self.capacity] = experience
        self.exp_count += 1

    # randomly pick batch_size experience from replay memory
    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

def extract_tensors(experiences):
    # convert batch of experiences to experience of batches
    # e.g. experience(1,1,1,1), experience(2,2,2,2) -> experience(1,2),(1,2),(1,2),(1,2)
    batch = Experience(*zip(*experiences))

    states = torch.cat(batch.state)
    scores = torch.cat(batch.score)

    return (states, scores)

class MLP(nn.Module):
    def __init__(self, rows, cols):
        super().__init__()

        # input is the board matrix
        self.fc1 = nn.Linear(in_features=rows * cols, out_features=64)
        self.linear1_dropout = nn.Dropout(p=0.2)
        self.fc2 = nn.Linear(in_features=64, out_features=128)
        self.linear2_dropout = nn.Dropout(p=0.2)
        self.fc3 = nn.Linear(in_features=128, out_features=256)
        self.linear3_dropout = nn.Dropout(p=0.2)
        self.fc4 = nn.Linear(in_features=256, out_features=128)
        self.linear4_dropout = nn.Dropout(p=0.2)
        self.fc5 = nn.Linear(in_features=128, out_features=64)
        self.linear5_dropout = nn.Dropout(p=0.2)
        self.out = nn.Linear(in_features=64, out_features=1)

    def forward(self, start_point):
        t = start_point.flatten(start_dim=1)
        t = F.relu(self.linear1_dropout(self.fc1(t)))
        t = F.relu(self.linear2_dropout(self.fc2(t)))
        t = F.relu(self.linear3_dropout(self.fc3(t)))
        t = F.relu(self.linear4_dropout(self.fc4(t)))
        t = F.relu(self.linear5_dropout(self.fc5(t)))
        t = torch.sigmoid(self.out(t))
        return t

class QValues():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def get_current(value_net, states):
        return value_net(states.to(QValues.device))

class MiniMaxAgent():
    
    @staticmethod
    def get_score(kalah, value_net, side):
        state = copy.deepcopy(kalah.board.board)
        if side == Side.SOUTH:
            state[0] = state[0]
            state[1] = state[1]
        else:
            state_0 = copy.deepcopy(state[0])
            state[0] = state[1]
            state[1] = state_0
        state = torch.Tensor(state)
        state = torch.unsqueeze(state, 0)
        score = QValues.get_current(value_net, state)
        return score
    
    @staticmethod
    def minimax_dl(kalah, mySide, activeSide, depth, alpha, beta, val_net, eps):
        if kalah.gameOver():
            nodeValue = kalah.board.getSeedsInStore(mySide) - \
                kalah.board.getSeedsInStore(mySide.opposite())
            return nodeValue, 0
        elif depth == 0:    
            # original_h = kalah.board.getSeedsInStore(mySide) - \
            #     kalah.board.getSeedsInStore(mySide.opposite())
            # nn_h = MiniMaxAgent.get_score(kalah, val_net, mySide)
            # nodeValue = original_h * eps + nn_h * (1-eps)
            nodeValue = MiniMaxAgent.get_score(kalah, val_net, mySide)
            return nodeValue, 0
        
        # if both stores are empty, then this is the first move
        isFirstMove = True if (kalah.board.getSeedsInStore(Side.SOUTH) + kalah.board.getSeedsInStore(Side.NORTH)) == 0 else False
        # if south south store has 1, and north store has 0, then it is move 2 and player can swap
        isSecondMove = True if kalah.board.getSeedsInStore(Side.SOUTH) == 1 and kalah.board.getSeedsInStore(Side.NORTH) == 0 else False
        
        if mySide == activeSide:
            # max node
            bestValue = -sys.maxsize
            bestHole = 0
            for i in range(1, 8):
                newMove = Move(activeSide, i)
                newKalah = copy.deepcopy(kalah)
                newBoard = newKalah.board
                if kalah.isLegalMove(newMove, newBoard):
                    new_activeSide = kalah.makeMove(newMove, newBoard)
                    # if first move, then the player does not have an extra move
                    if isFirstMove:
                        new_activeSide = mySide.opposite()
                    value, hole = MiniMaxAgent.minimax_dl(newKalah, mySide, new_activeSide, depth-1, alpha, beta, val_net, eps)
                    if value > bestValue:
                        bestValue = value
                        bestHole = i
                    if bestValue > alpha:
                        alpha = bestValue
                    if alpha >= beta:
                        break
            if isSecondMove and alpha < beta:
                newKalah = copy.deepcopy(kalah)
                newBoard = newKalah.board
                value, hole = MiniMaxAgent.minimax_dl(newKalah, mySide.opposite(), activeSide, depth-1, alpha, beta, val_net, eps)
                if value > bestValue:
                    bestValue = value
                    # bestHole = -1
                if bestValue > alpha:
                    alpha = bestValue
        else:
            # min node
            bestValue = sys.maxsize
            bestHole = 0
            for i in range(1, 8):
                newMove = Move(activeSide, i);
                newKalah = copy.deepcopy(kalah)
                newBoard = newKalah.board
                if kalah.isLegalMove(newMove, newBoard):
                    new_activeSide = kalah.makeMove(newMove, newBoard)
                    value, hole = MiniMaxAgent.minimax_dl(newKalah, mySide, new_activeSide, depth-1, alpha, beta, val_net, eps)
                    if value < bestValue:
                        bestValue = value
                        bestHole = i
                    if bestValue < beta:
                        beta = bestValue
                    if beta <= alpha:
                        break
            if isSecondMove and beta > alpha:
                newKalah = copy.deepcopy(kalah)
                newBoard = newKalah.board
                value, hole = MiniMaxAgent.minimax_dl(newKalah, mySide.opposite(), activeSide, depth-1, alpha, beta, val_net, eps)
                if value < bestValue:
                    bestValue = value
                    # bestHole = -1
                if bestValue < beta:
                    beta = bestValue
        return bestValue, bestHole
