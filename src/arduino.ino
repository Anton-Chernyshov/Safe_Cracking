


int Puzzle1Pin = A1;
int Puzzle2Pin = A2;



void setup() {
	Serial.begin(9600);
}

void loop() {


	unsigned float Voltage1 = analogRead(Puzzle1Pin) * (5.0 / 1023.0);
	unsigned float Voltage2 = analogRead(Puzzle2Pin) * (5.0 / 1023.0);

	if (Voltage1 > 3.1 && Voltage1 < 3.5) { // checks if the voltage is between 3.1 and 3.5 ( 3.3V is the standard voltage for a logic 1)
		Serial.print("1");
	}
	else {
		Serial.print("0");
	}

	Serial.print(","); // sep 

	if (Voltage2 > 3.1 && Voltage2 < 3.5) { // checks if the voltage is between 3.1 and 3.5 ( 3.3V is the standard voltage for a logic 1)
		Serial.print("1");
	}
	else {
		Serial.print("0");
	}
	Serial.println();
	// output in the form of 1,0
}