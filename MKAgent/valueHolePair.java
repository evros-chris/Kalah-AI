package MKAgent;

public class valueHolePair {
	private double value;
	private int hole;

	public valueHolePair(double myValue, int myHole) {
		this.value = myValue;
		this.hole = myHole;
	}

	public double getValue() {
		return value;
	}

	public int getHole() {
		return hole;
	}
}
