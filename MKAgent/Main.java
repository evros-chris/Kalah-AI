package MKAgent;
import java.io.BufferedReader;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;

/**
 * The main application class. It also provides methods for communication
 * with the game engine.
 */
public class Main
{
    /**
     * Input from the game engine.
     */
    private static Reader input = new BufferedReader(new InputStreamReader(System.in));

    /**
     * Sends a message to the game engine.
     * @param msg The message.
     */
    public static void sendMsg (String msg)
    {
    	System.out.print(msg);
    	System.out.flush();
    }

    /**
     * Receives a message from the game engine. Messages are terminated by
     * a '\n' character.
     * @return The message.
     * @throws IOException if there has been an I/O error.
     */
    public static String recvMsg() throws IOException
    {
    	StringBuilder message = new StringBuilder();
    	int newCharacter;

    	do
    	{
    		newCharacter = input.read();
    		if (newCharacter == -1)
    			throw new EOFException("Input ended unexpectedly.");
    		message.append((char)newCharacter);
    	} while((char)newCharacter != '\n');

		return message.toString();
    }

	public static valueHolePair minimax(Board board, Side mySide, Side playSide, int depth, int alpha, int beta) throws CloneNotSupportedException
	{
		if (depth == 0 || Kalah.gameOver(board))
		{
			int nodeValue = seedsInMyStore(board, mySide) - seedsInOpStore(board, mySide);
			return new valueHolePair(nodeValue, 0);
		}
		Board newBoard;
		Move newMove;
		Side newPlaySide;
		valueHolePair valueHole;
		int bestValue;
		int bestHole;
		// if both stores are empty, then this is the first move
		boolean isFirstMove = ((board.getSeedsInStore(Side.SOUTH) + board.getSeedsInStore(Side.NORTH)) == 0) ? true : false;
		// if south south store has 1, and north store has 0, then it is move 2 and player can swap
		boolean isSecondMove = (board.getSeedsInStore(Side.SOUTH) == 1 && board.getSeedsInStore(Side.NORTH) == 0) ? true : false;
		if (mySide == playSide)
		{
			bestValue = Integer.MIN_VALUE;
			bestHole = 0;
	
			for (int i = 1; i <= 7; i++)
			{
				newMove = new Move(playSide, i);
				newBoard = board.clone();
				if (Kalah.isLegalMove(newBoard, newMove))
				{
					newPlaySide = Kalah.makeMove(newBoard, newMove);
					// if first move, then the player does not have an extra move
					if (isFirstMove)
						newPlaySide = mySide.opposite();
					valueHole = minimax(newBoard, mySide, newPlaySide, depth - 1, alpha, beta);
					if (valueHole.getValue() > bestValue)
					{
						bestValue = valueHole.getValue();
						bestHole = i;
					}
					if (bestValue > alpha)
						alpha = bestValue;
					if (alpha >= beta)
						break;
				}
			}
			if (isSecondMove && alpha < beta)
			{
				newBoard = board.clone();
				valueHole = minimax(newBoard, mySide.opposite(), playSide, depth - 1, alpha, beta);
				if (valueHole.getValue() > bestValue)
				{
					bestValue = valueHole.getValue();
					bestHole = -1;
				}
				if (bestValue > alpha)
					alpha = bestValue;
			}
		}
		else
		{
			bestValue = Integer.MAX_VALUE;
			bestHole = 0;
			
			for (int i = 1; i <= 7; i++)
			{
				newMove = new Move(playSide, i);
				newBoard = board.clone();
				if (Kalah.isLegalMove(newBoard, newMove))
				{
					newPlaySide = Kalah.makeMove(newBoard, newMove);
					valueHole = minimax(newBoard, mySide, newPlaySide, depth - 1, alpha, beta);
					if (valueHole.getValue() < bestValue)
					{
						bestValue = valueHole.getValue();
						bestHole = i;
					}
					if (bestValue < beta)
						beta = bestValue;
					if (beta <= alpha)
						break;
				}
			}
			if (isSecondMove && beta > alpha)
			{
				newBoard = board.clone();
				valueHole = minimax(newBoard, mySide.opposite(), playSide, depth - 1, alpha, beta);
				if (valueHole.getValue() < bestValue)
				{
					bestValue = valueHole.getValue();
					bestHole = -1;
				}
				if (bestValue < beta)
					beta = bestValue;
			}
		}
		return new valueHolePair(bestValue, bestHole);
	}

	// heuristic 1
	public static int seedsInMyStore(Board board, Side side)
	{	
		return board.getSeedsInStore(side);
	}

	// heuristic 2
	public static int seedsInOpStore(Board board, Side side)
	{	
		return board.getSeedsInStore(side.opposite());
		
	}

	/* heuristic 3
	public static int seedsInMySide(Board board, Side side)
	{
		int total = 0;
		for (int i = 1; i <= 7; i++)
		{
			//total += board.getSeeds(side, i);
		}
		return total;
	}*/
	
	/**
	 * The main method, invoked when the program is started.
	 * @param args Command line arguments.
	 */
	public static void main(String[] args) throws Exception
	{
		// TODO: implement
		Board board = new Board(7,7);
		Kalah kalah = new Kalah(board);
		Side side = null;
		String message;
		MsgType msgType;		
		int moveHole;
		String moveMessage;
		Protocol.MoveTurn moveTurn;
		Move move;

		while (true)
		{
			message = recvMsg();
			msgType = Protocol.getMessageType(message);
			
			if (msgType == MsgType.END)
			{
				break;
			}
			else if (msgType == MsgType.START)
			{
				if (Protocol.interpretStartMsg(message))
				{
					side = Side.SOUTH;
					moveHole = moveHole = minimax(kalah.getBoard(), side, side, 8, Integer.MIN_VALUE, Integer.MAX_VALUE).getHole();
					if (moveHole == -1)
						moveMessage = Protocol.createSwapMsg();
					else					
						moveMessage = Protocol.createMoveMsg(moveHole);
					sendMsg(moveMessage);
				}
				else
				{
					side = Side.NORTH;
				}
			}
			else if (msgType == MsgType.STATE)
			{
				moveTurn = Protocol.interpretStateMsg(message, kalah.getBoard());
				if (moveTurn.move == -1)
					side = side.opposite();
				if (moveTurn.again && !moveTurn.end)
				{
					moveHole = minimax(kalah.getBoard(), side, side, 8, Integer.MIN_VALUE, Integer.MAX_VALUE).getHole();
					if (moveHole == -1)
						moveMessage = Protocol.createSwapMsg();					
					else					
						moveMessage = Protocol.createMoveMsg(moveHole);
					sendMsg(moveMessage);
				}
			}		
		}

	}
}
