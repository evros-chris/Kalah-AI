package ManKalah;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.EOFException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.io.Writer;

public class Player {
  private String name;
  private int playerNumber;
  private Process agent;
  private Writer agentInput;
  private Reader agentOutput;
  private TimeoutReader readerThread = null;
  private Side side;
  private int moveCount = 0;
  private long overallResponseTime = 0L;

  public Player(int playerNumber, String name, Process agent, Side initialSide) {
    this.playerNumber = playerNumber;
    this.name = name;
    this.agent = agent;
    this.side = initialSide;
    this.agentOutput = new BufferedReader(new InputStreamReader(agent.getInputStream()));
    this.agentInput = new BufferedWriter(new OutputStreamWriter(agent.getOutputStream()));
  }

  public String getName() {
    return this.name;
  }

  public Side getSide() {
    return this.side;
  }

  public int getPlayerNumber() {
    return this.playerNumber;
  }

  public void changeSide() {
    this.side = this.side.opposite();
  }

  public int getMoveCount() {
    return this.moveCount;
  }

  public void incrementMoveCount() {
    this.moveCount++;
  }

  public long getOverallResponseTime() {
    return this.overallResponseTime;
  }

  public void incrementOverallResponseTime(long additionalResponseTime) {
    this.overallResponseTime += additionalResponseTime;
  }

  public void startReaderThread() {
    if (this.readerThread != null) {
      throw new IllegalStateException("Method called twice.");
    }
    this.readerThread = new TimeoutReader(this);
    this.readerThread.start();
  }

  public TimeoutReader getReaderThread() {
    return this.readerThread;
  }

  public void sendMsg(String msg) throws IOException {
    this.agentInput.write(msg);
    this.agentInput.flush();
  }

  public String recvMsg() throws IOException {
    int newCharacter;
    StringBuilder message = new StringBuilder();

    do {
      newCharacter = this.agentOutput.read();
      if (newCharacter == -1)
        throw new EOFException("Agent input ended unexpectedly.");
      message.append((char) newCharacter);
    } while ((char) newCharacter != '\n');

    return message.toString();
  }
}
