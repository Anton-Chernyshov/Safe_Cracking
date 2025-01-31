


int Puzzle1Pin = A3;




void setup() {
	Serial.begin(9600);
}

void loop() {


	float Voltage1 = analogRead(Puzzle1Pin) * (5.0 / 1023.0);

	if (Voltage1 > 2.25 && Voltage1 < 2.45) { // checks if the voltage is between 3.1 and 3.5 ( 3.3V is the standard voltage for a logic 1)
		Serial.println("1");
	}
	else {
		Serial.println("0");
	}

	
	}
delay(50);
	// output in the form of 1,0
}