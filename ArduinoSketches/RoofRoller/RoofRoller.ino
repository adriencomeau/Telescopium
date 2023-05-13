/*

*/

const int openingRelay              = 10;
const int openedLED = 9;
const int closingRelay = 8;
const int closedLED = 7;
const int openPin = 5;
const int parkPin = 6;

const int openingState = 1;
const int openState = 2;
const int closingState = 3;
const int closedState = 4;
const int abortedState = 5;
const int scopeOutOfParkState = 6;

int roofState = closedState;

int hasLeftPark;

void setup() {

  // set up the switch pin as an input
  pinMode(openingRelay, OUTPUT);
  pinMode(openedLED, OUTPUT);
  pinMode(closingRelay, OUTPUT);
  pinMode(closedLED, OUTPUT);
  pinMode(openPin, OUTPUT);
  pinMode(parkPin, INPUT);

  digitalWrite(openingRelay, LOW);
  digitalWrite(openedLED, LOW);
  digitalWrite(openPin, LOW);
  digitalWrite(closingRelay, LOW);
  digitalWrite(closedLED, LOW);

  int openedSensor = analogRead(A1);
  if (openedSensor < 512) {
    roofState = openState;
    digitalWrite(openedLED, HIGH);
    digitalWrite(openPin, HIGH);
  }

  int closedSensor = analogRead(A3);
  if (closedSensor < 512) {
    roofState = closedState;
    digitalWrite(closedLED, HIGH);
  }

  Serial.begin(9600);
  Serial.flush();


}

void loop() {

  String cmd;

  if (Serial.available() > 0) {
    cmd = Serial.readStringUntil('#');
    if (cmd == "IDENT") identify();    
    if (cmd == "OPENROOF") openroof();
    if (cmd == "CLOSEROOF") closeroof();
    if (cmd == "QUERYROOF") queryroof();
  }
  //int openButton = analogRead(A0);
  //if (openButton > 512) openroof();

  //int closeButton = analogRead(A2);
  //if (closeButton > 512) closeroof();

}

void identify() {
  Serial.println("RoofRoller");
}

void queryroof() {
  if (roofState == openState)		          Serial.println("is Open");
  if (roofState == openingState)	        Serial.println("is Opening");
  if (roofState == closingState)	        Serial.println("is Closing");
  if (roofState == closedState)		        Serial.println("is Closed");
  if (roofState == abortedState)          Serial.println("is Aborted");
  if (roofState == scopeOutOfParkState)   Serial.println("is Aborted");
}

void openroof() {
  Serial.println("OPENROOF Ack"); // ack the open command
  String cmd;
  if (roofState == openState) {
    // ROOF WAS already OPEN
    digitalWrite(openingRelay, LOW);
    digitalWrite(openedLED, HIGH);
    digitalWrite(openPin, HIGH);
    digitalWrite(closingRelay, LOW);
    digitalWrite(closedLED, LOW);
  }
  else {
    hasLeftPark = digitalRead(parkPin);
    if (hasLeftPark == true)  {
      // OPEN COMMAND Rxed and SCOPE was NOT PARKED!!!
      digitalWrite(openingRelay, LOW);
      digitalWrite(openedLED, LOW);
      digitalWrite(openPin, LOW);
      digitalWrite(closingRelay, LOW);
      digitalWrite(closedLED, HIGH);
      roofState = closedState;
    }
    else {
      // INITIATE OPEN
      digitalWrite(openingRelay, HIGH);
      digitalWrite(openedLED, LOW);
      digitalWrite(openPin, LOW);
      digitalWrite(closingRelay, LOW);
      digitalWrite(closedLED, LOW);
      roofState = openingState;
      int openedSensor = analogRead(A1);
      boolean rxedAbortCommand = false;
      while ((openedSensor > 512) && (rxedAbortCommand == false) && not(hasLeftPark))
      {
        openedSensor = analogRead(A1);
        hasLeftPark = digitalRead(parkPin);
        if (Serial.available() > 0) {
          cmd = Serial.readStringUntil('#');
          if (cmd == "ABORT") rxedAbortCommand = true;
          if (cmd == "QUERYROOF") queryroof();
        }
      }
      if (rxedAbortCommand) {
        // OPENING ROOF WAS ABORTED by PC
        digitalWrite(openingRelay, LOW);
        digitalWrite(openedLED, LOW);
        digitalWrite(openPin, LOW);
        digitalWrite(closingRelay, LOW);
        digitalWrite(closedLED, LOW);
        roofState = abortedState;
        Serial.println("ABORT Ack"); // Ack the abort command
      }
      else if (hasLeftPark) {
        // SCOPE LEFT PARK While roof was opening!!!
        digitalWrite(openingRelay, LOW);
        digitalWrite(openedLED, HIGH);
        digitalWrite(openPin, LOW);
        digitalWrite(closingRelay, LOW);
        digitalWrite(closedLED, HIGH);
        roofState = scopeOutOfParkState;
      }
      else {
        // OPENING ROOF COMPLETED NORMALLY
        digitalWrite(openingRelay, LOW);
        digitalWrite(openedLED, HIGH);
        digitalWrite(openPin, HIGH);
        digitalWrite(closingRelay, LOW);
        digitalWrite(closedLED, LOW);
        roofState = openState;
      }
    }
  }
}
void closeroof() {
  //Serial.print("CLOSEROOF Ack#"); // ack the close command
  String cmd;
  if (roofState == closedState) {
    // ROOF WAS already CLOSED
    digitalWrite(openingRelay, LOW);
    digitalWrite(openedLED, LOW);
    digitalWrite(openPin, LOW);
    digitalWrite(closingRelay, LOW);
    digitalWrite(closedLED, HIGH);
    Serial.println("CLOSEROOF Ack"); // ack the close command
  }
  else {
    hasLeftPark = digitalRead(parkPin);
    if (hasLeftPark == true)  {
      // CLOSE COMMAND Rxed and SCOPE was NOT PARKED!!!
      digitalWrite(openingRelay, LOW);
      digitalWrite(openedLED, HIGH);
      digitalWrite(openPin, HIGH);
      digitalWrite(closingRelay, LOW);
      digitalWrite(closedLED, LOW);
      roofState = openState;
      Serial.println("SCOPE NOT PARKED"); // ack the close command
    }
    else {
      // INITIATE CLOSE
      digitalWrite(openingRelay, LOW);
      digitalWrite(openedLED, LOW);
      digitalWrite(openPin, LOW);
      digitalWrite(closingRelay, HIGH);
      digitalWrite(closedLED, LOW);
      roofState = closingState;
      Serial.println("CLOSEROOF Ack"); // ack the close command
      int closedSensor = analogRead(A3);
      boolean rxedAbortCommand = false;
      while ((closedSensor > 512) && (rxedAbortCommand == false) && not(hasLeftPark))
      {
        closedSensor = analogRead(A3);
        hasLeftPark = digitalRead(parkPin);
        if (Serial.available() > 0) {
          cmd = Serial.readStringUntil('#');
          if (cmd == "ABORT") rxedAbortCommand = true;
          if (cmd == "QUERYROOF") queryroof();
        }
      }
      if (rxedAbortCommand) {
        // CLOSING ROOF WAS ABORTED by PC
        digitalWrite(openingRelay, LOW);
        digitalWrite(openedLED, LOW);
        digitalWrite(openPin, LOW);
        digitalWrite(closingRelay, LOW);
        digitalWrite(closedLED, LOW);
        roofState = abortedState;
        Serial.println("ABORT Ack"); // Ack the abort command
      }
      else if (hasLeftPark) {
        // SCOPE LEFT PARK While roof was closing!!!
        digitalWrite(openingRelay, LOW);
        digitalWrite(openedLED, HIGH);
        digitalWrite(openPin, LOW);
        digitalWrite(closingRelay, LOW);
        digitalWrite(closedLED, HIGH);
        roofState = scopeOutOfParkState;
      }
      else {
        // CLOSING ROOF COMPLETED NORMALLY
        digitalWrite(openingRelay, LOW);
        digitalWrite(openedLED, LOW);
        digitalWrite(openPin, LOW);
        digitalWrite(closingRelay, LOW);
        digitalWrite(closedLED, HIGH);
        roofState = closedState;
      }
    }
  }
}
