from agent import RandomAgent
from kalah import Board
from kalah import Kalah
from kalah import Side
import protocol

board = Board(7, 7)
kalah = Kalah(board)
message = "CHANGE;1;0,9,9,9,9,8,8,1,8,7,7,7,7,0,8,1;YOU\n"
msg_type = protocol.getMsgType(message)
move_turn = protocol.interpretStateMsg(message, kalah.board)
if not move_turn.end and move_turn.again:
    # possible_moves = [1,2,3,4,5,6,7]
    possible_moves = RandomAgent().getPossibleMoves(Side.SOUTH, kalah)
    print(possible_moves)
    move_hole = RandomAgent().random_move(possible_moves)
    choice = protocol.createMoveMsg(move_hole)
    print(choice)
