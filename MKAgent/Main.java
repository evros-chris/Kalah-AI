package MKAgent;

import java.io.BufferedReader;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;

/**
 * The main application class. It also provides methods for communication with
 * the game engine.
 */
public class Main {
	/**
	 * Input from the game engine.
	 */
	private static Reader input = new BufferedReader(new InputStreamReader(System.in));

	/**
	 * Sends a message to the game engine.
	 * 
	 * @param msg The message.
	 */
	public static void sendMsg(String msg) {
		System.out.print(msg);
		System.out.flush();
	}

	/**
	 * Receives a message from the game engine. Messages are terminated by a '\n'
	 * character.
	 * 
	 * @return The message.
	 * @throws IOException if there has been an I/O error.
	 */
	public static String recvMsg() throws IOException {
		StringBuilder message = new StringBuilder();
		int newCharacter;

		do {
			newCharacter = input.read();
			if (newCharacter == -1)
				throw new EOFException("Input ended unexpectedly.");
			message.append((char) newCharacter);
		} while ((char) newCharacter != '\n');

		return message.toString();
	}

	public static valueHolePair minimax(Board board, Side mySide, Side playSide, int depth, double alpha, double beta,
			boolean swapPlayed) throws Exception {
		if (depth == 0 || Kalah.gameOver(board)) {
			return new valueHolePair(evaluationFunction(board, mySide, playSide), 0);
		}
		Board newBoard;
		Move newMove;
		Side newPlaySide;
		valueHolePair valueHole;
		double bestValue;
		int bestHole;

		int[] moves = new int[7];
		for (int i = 0; i < 7; i++) {
			moves[i] = i + 1;
		}

		// find move evaluations with look ahead of 1
		double[] moveValues = new double[7];
		for (int i = 0; i < 7; i++) {
			newBoard = board.clone();
			newMove = new Move(playSide, i + 1);
			if (Kalah.isLegalMove(newBoard, newMove)) {
				newPlaySide = Kalah.makeMove(newBoard, newMove);
				if (newPlaySide == mySide)
					moveValues[i] = minimax(newBoard, mySide, newPlaySide, 0, alpha, beta, swapPlayed).getValue() + 10;
				else
					moveValues[i] = minimax(newBoard, mySide, newPlaySide, 0, alpha, beta, swapPlayed).getValue();
			}
		}

		double tempValue;
		int tempMove;
		// sort moves according to their evaluations
		for (int i = 0; i < 7 - 1; i++)
			for (int j = 0; j < 7 - i - 1; j++)
				if (moveValues[j] < moveValues[j + 1]) {
					tempValue = moveValues[j];
					moveValues[j] = moveValues[j + 1];
					moveValues[j + 1] = tempValue;
					tempMove = moves[j];
					moves[j] = moves[j + 1];
					moves[j + 1] = tempMove;
				}

		// if both stores are empty, then this is the first move
		boolean isFirstMove = ((board.getSeedsInStore(Side.SOUTH) + board.getSeedsInStore(Side.NORTH)) == 0) ? true
				: false;
		// if south south store has 1, and north store has 0 and swap has not been
		// played, then it is move 2 and player can swap
		boolean swapAvailable = (board.getSeedsInStore(Side.SOUTH) == 1 && board.getSeedsInStore(Side.NORTH) == 0
				&& !swapPlayed) ? true : false;

		int currentMove;

		if (mySide == playSide) {
			bestValue = Integer.MIN_VALUE;
			bestHole = 0;

			for (int i = 1; i <= 7; i++) {
				// select moves with best value first
				currentMove = moves[i - 1];
				newMove = new Move(playSide, currentMove);
				newBoard = board.clone();
				if (Kalah.isLegalMove(newBoard, newMove)) {
					newPlaySide = Kalah.makeMove(newBoard, newMove);
					// if first move, then the player does not have an extra move
					if (isFirstMove)
						newPlaySide = mySide.opposite();
					valueHole = minimax(newBoard, mySide, newPlaySide, depth - 1, alpha, beta, swapPlayed);
					if (valueHole.getValue() > bestValue) {
						bestValue = valueHole.getValue();
						bestHole = currentMove;
					}
					if (valueHole.getValue() > alpha)
						alpha = valueHole.getValue();
					if (beta <= alpha)
						break;
				}
			}

			if (swapAvailable && alpha < beta) {
				newBoard = board.clone();
				valueHole = minimax(newBoard, mySide.opposite(), playSide, depth - 1, alpha, beta, swapPlayed);
				if (valueHole.getValue() > bestValue) {
					bestValue = valueHole.getValue();
					bestHole = -1;
				}
				if (bestValue > alpha)
					alpha = bestValue;
			}

		} else {
			bestValue = Integer.MAX_VALUE;
			bestHole = 0;

			for (int i = 1; i <= 7; i++) {
				// select moves with least value first
				currentMove = moves[7 - i];
				newMove = new Move(playSide, currentMove);
				newBoard = board.clone();
				if (Kalah.isLegalMove(newBoard, newMove)) {
					newPlaySide = Kalah.makeMove(newBoard, newMove);
					valueHole = minimax(newBoard, mySide, newPlaySide, depth - 1, alpha, beta, swapPlayed);
					if (valueHole.getValue() < bestValue) {
						bestValue = valueHole.getValue();
						bestHole = currentMove;
					}
					if (valueHole.getValue() < beta)
						beta = valueHole.getValue();
					if (beta <= alpha)
						break;
				}
			}

			if (swapAvailable && alpha < beta) {
				newBoard = board.clone();
				valueHole = minimax(newBoard, mySide.opposite(), playSide, depth - 1, alpha, beta, swapPlayed);
				if (valueHole.getValue() < bestValue) {
					bestValue = valueHole.getValue();
					bestHole = -1;
				}
				if (bestValue < beta)
					beta = bestValue;
			}

		}
		return new valueHolePair(bestValue, bestHole);
	}

	// evaluation function
	public static double evaluationFunction(Board board, Side mySide, Side playSide) throws Exception {
		if (playSide == mySide)
			return seedsInMyStore(board, mySide) * 1 - seedsInOpStore(board, mySide) * 0.57
					+ seedsInMySide(board, mySide) * 0.19 - seedsInOpSide(board, mySide) * 0
					+ noOfNonEmptyPits(board, mySide) * 0.37 + seedsInLeftMostPit(board, mySide) * 0.20 + 5;
		else
			return seedsInMyStore(board, mySide) * 1 - seedsInOpStore(board, mySide) * 0.57
					+ seedsInMySide(board, mySide) * 0.19 - seedsInOpSide(board, mySide) * 0
					+ noOfNonEmptyPits(board, mySide) * 0.37 + seedsInLeftMostPit(board, mySide) * 0.20;
		// return seedsInMyStore(board, mySide) - seedsInOpStore(board, mySide);
	}

	// heuristic 1
	public static int seedsInMyStore(Board board, Side side) {
		return board.getSeedsInStore(side);
	}

	// heuristic 2
	public static int seedsInOpStore(Board board, Side side) {
		return board.getSeedsInStore(side.opposite());
	}

	// heuristic 3
	public static int seedsInMySide(Board board, Side side) {
		int total = 0;
		for (int i = 1; i <= 7; i++) {
			total += board.getSeeds(side, i);
		}
		return total;
	}

	// heuristic 4
	public static int seedsInOpSide(Board board, Side side) {
		int total = 0;
		for (int i = 1; i <= 7; i++) {
			total += board.getSeeds(side.opposite(), i);
		}
		return total;
	}

	// heuristic 5
	public static int seedsInLeftMostPit(Board board, Side side) {
		return board.getSeeds(side, 1);
	}

	// heuristic 6
	public static int noOfNonEmptyPits(Board board, Side side) {
		int total = 0;
		for (int i = 1; i <= 7; i++) {
			if (board.getSeeds(side, i) != 0)
				total++;
		}
		return total;
	}

	/**
	 * The main method, invoked when the program is started.
	 * 
	 * @param args Command line arguments.
	 */
	public static void main(String[] args) throws Exception {
		Board board = new Board(7, 7);
		Kalah kalah = new Kalah(board);
		Side side = null;
		String message;
		MsgType msgType;
		int moveHole;
		String moveMessage;
		Protocol.MoveTurn moveTurn;
		Move move;
		boolean swapPlayed = false;

		while (true) {
			message = recvMsg();
			msgType = Protocol.getMessageType(message);

			if (msgType == MsgType.END) {
				break;
			} else if (msgType == MsgType.START) {
				if (Protocol.interpretStartMsg(message)) {
					side = Side.SOUTH;
					moveHole = minimax(kalah.getBoard(), side, side, 12, Integer.MIN_VALUE, Integer.MAX_VALUE,
							swapPlayed).getHole();
					if (moveHole == -1) {
						moveMessage = Protocol.createSwapMsg();
						side = side.opposite();
					} else
						moveMessage = Protocol.createMoveMsg(moveHole);
					sendMsg(moveMessage);
				} else {
					side = Side.NORTH;
				}
			} else if (msgType == MsgType.STATE) {
				moveTurn = Protocol.interpretStateMsg(message, kalah.getBoard());
				if (moveTurn.move == -1) {
					side = side.opposite();
					swapPlayed = true;
				}
				if (moveTurn.again && !moveTurn.end) {
					moveHole = minimax(kalah.getBoard(), side, side, 12, Integer.MIN_VALUE, Integer.MAX_VALUE,
							swapPlayed).getHole();
					if (moveHole == -1) {
						moveMessage = Protocol.createSwapMsg();
						side = side.opposite();
						swapPlayed = true;
					} else
						moveMessage = Protocol.createMoveMsg(moveHole);
					sendMsg(moveMessage);
				}
			}
		}
	}
}
