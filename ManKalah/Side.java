package ManKalah;

public enum Side
{
  NORTH, SOUTH;
  
  public Side opposite() {
    switch (this) {
      case null:
        return SOUTH;
      case SOUTH: return NORTH;
    }  return NORTH;
  }
}
