from random import choice
import copy
from kalah import Move, Side
import sys


def getPossibleMoves(side, kalah):
    choice_list = []
    for i in range(1, 8):
        move = Move(side, i)
        if kalah.isLegalMove(move):
            choice_list.append(i)
    return choice_list


class RandomAgent():
    def random_move(self, possible_moves):
        return choice(possible_moves)


class MiniMaxAgent():
    @staticmethod
    def minimax(kalah, mySide, activeSide, depth, alpha, beta):
        if depth == 0 or kalah.gameOver():
            nodeValue = kalah.board.getSeedsInStore(mySide) - \
                kalah.board.getSeedsInStore(mySide.opposite())
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
                    value, hole = MiniMaxAgent.minimax(newKalah, mySide, new_activeSide, depth - 1, alpha, beta)
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
                value, hole = MiniMaxAgent.minimax(newKalah, mySide.opposite(), activeSide, depth-1, alpha, beta)
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
                    value, hole = MiniMaxAgent.minimax(newKalah, mySide, new_activeSide, depth-1, alpha, beta)
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
                value, hole = MiniMaxAgent.minimax(newKalah, mySide.opposite(), activeSide, depth-1, alpha, beta)
                if value < bestValue:
                    bestValue = value
                    # bestHole = -1
                if bestValue < beta:
                    beta = bestValue
        return value, bestHole
