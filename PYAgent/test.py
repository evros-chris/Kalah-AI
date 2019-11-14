from kalah import Kalah
from kalah import Board
from protocol import Protocol
from agent import random_agent
from kalah import Side

board = Board(7, 7)
kalah = Kalah(board)
message = "CHANGE;1;0,9,9,9,9,8,8,1,8,7,7,7,7,0,8,1;YOU\n"
msg_type = Protocol().getMsgType(message)
move_turn = Protocol().interpretStateMsg(message, kalah.board)
if ~move_turn.end and move_turn.again:
    # possible_moves = [1,2,3,4,5,6,7]
    possible_moves = random_agent().getPossibleMoves(Side.SOUTH, kalah)
    print(possible_moves)
    move_hole = random_agent().random_move(possible_moves)
    choice = Protocol().createMoveMsg(move_hole)
    print(choice)
