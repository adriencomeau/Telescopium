/*
  MMA8452Q Basic Example Code
  Nathan Seidle
  SparkFun Electronics
  November 5, 2012

  License: This code is public domain but you buy me a beer if you use this and we meet someday (Beerware license).

  This example code shows how to read the X/Y/Z accelerations and basic functions of the MMA5842. It leaves out
  all the neat features this IC is capable of (tap, orientation, and inerrupts) and just displays X/Y/Z. See
  the advanced example code to see more features.

  Hardware setup:
  MMA8452 Breakout ------------ Arduino
  3.3V --------------------- 3.3V
  SDA -------^^(330)^^------- A4
  SCL -------^^(330)^^------- A5
  GND ---------------------- GND

  The MMA8452 is 3.3V so we recommend using 330 or 1k resistors between a 5V Arduino and the MMA8452 breakout.

  The MMA8452 has built in pull-up resistors for I2C so you do not need additional pull-ups.
add a comment
*/

#include <Wire.h> // Used for I2C

// The SparkFun breakout board defaults to 1, set to 0 if SA0 jumper on the bottom of the board is set
#define MMA8452_ADDRESS 0x1C  // 0x1D if SA0 is high, 0x1C if low

//Define a few of the registers that we will be accessing on the MMA8452
#define OUT_X_MSB 0x01
#define XYZ_DATA_CFG  0x0E
#define WHO_AM_I   0x0D
#define CTRL_REG1  0x2A

#define GSCALE 2 // Sets full-scale range to +/-2, 4, or 8g. Used to calc real g values.

float pi;
double accelGatPark[3];
float tolleranceDegrees;
float deltaAngle;
int isParked;
int openPinValue;
int mountSupplied;
int forceMountOn;

int openPin = 8;
int relayPin = 9;
int parkPin = 10;
int notParkedPin = 11;


double accelG[3];  // Stores the real accel value in g's

void setup()
{
  pinMode(openPin, INPUT);
  pinMode(relayPin, OUTPUT);
  pinMode(parkPin, OUTPUT);
  pinMode(notParkedPin, OUTPUT);

  digitalWrite(relayPin, LOW);
  digitalWrite(parkPin, LOW);
  digitalWrite(notParkedPin, LOW);

  Serial.begin(19200);
  Serial.flush();
  Serial.println("MMA8452 Basic Example");

  Wire.begin(); //Join the bus as a master

  initMMA8452(); //Test and intialize the MMA8452

  pi = 2 * asin(1.0);

  accelGatPark[0] = (double)  0.785;  // Stores the real accel value in g's
  accelGatPark[1] = (double)  0.06;  // Stores the real accel value in g's
  accelGatPark[2] = (double) - 0.615; // Stores the real accel value in g's
  double len;
  len = sqrt(pow(accelGatPark[0], 2) + pow(accelGatPark[1], 2) + pow(accelGatPark[2], 2));
  accelGatPark[0] = accelGatPark[0] / len;
  accelGatPark[1] = accelGatPark[1] / len;
  accelGatPark[2] = accelGatPark[2] / len;

  tolleranceDegrees = 4;

  accelG[0] = 0;
  accelG[1] = 0;
  accelG[2] = 0;

}

void loop()
{
  double len;
  int accelCount[3];  // Stores the 12-bit signed value
  readAccelData(accelCount);  // Read the x/y/z adc values


  String cmd;

  if (Serial.available() > 0) {
    cmd = Serial.readStringUntil('#');
    if (cmd == "ForceMountOn") forceMountOn = true;
    if (cmd == "Normal") forceMountOn = false;

  }


  openPinValue = digitalRead(openPin);

  // Now we'll calculate the accleration value into actual g's
  double a = 0.9;
  for (int i = 0 ; i < 3 ; i++)
  {
    accelG[i] = a * accelG[i] + (1 - a) * ((double) accelCount[i] / ((1 << 12) / (2 * GSCALE))); // get actual g value, this depends on scale being set

  }

  len = sqrt(pow(accelG[0], 2) + pow(accelG[1], 2) + pow(accelG[2], 2));
  accelG[0] = accelG[0] / len;
  accelG[1] = accelG[1] / len;
  accelG[2] = accelG[2] / len;

  deltaAngle = (180 / pi) * acos(accelG[0] * accelGatPark[0] + accelG[1] * accelGatPark[1] + accelG[2] * accelGatPark[2]);

  if (isParked == 1){
  if  (deltaAngle > tolleranceDegrees + 2) {
      isParked = 0;
      digitalWrite(parkPin, LOW);
      digitalWrite(notParkedPin, HIGH);
    }
  }
  if (isParked == 0){
  if  (deltaAngle < tolleranceDegrees - 2) {
      isParked = 1;
      digitalWrite(parkPin, HIGH);
      digitalWrite(notParkedPin, LOW);
    }

  }

  //  if (deltaAngle < tolleranceDegrees)
  //  {
  //    isParked = 1;
  //    digitalWrite(parkPin, HIGH);
  //    digitalWrite(notParkedPin, LOW);
  //  }
  //  else
  //  {
  //    isParked = 0;
  //    digitalWrite(parkPin, LOW);
  //    digitalWrite(notParkedPin, HIGH);
  //  }


  if (forceMountOn == true)
  {
    mountSupplied = 1;
    digitalWrite(relayPin, HIGH);
  }
  else {
    if (isParked == 0 and openPinValue == 0)
    {
      mountSupplied = 0;
      digitalWrite(relayPin, LOW);
    }
    else
    {
      mountSupplied = 1;
      digitalWrite(relayPin, HIGH);
    }
  }
  // Print out values
  for (int i = 0 ; i < 3 ; i++)
  {
    Serial.print(accelG[i], 4); // Print g values
    Serial.print("\t");  // tabs in between axes
  }
  Serial.print(deltaAngle);
  Serial.print("\t");  // tabs in between axes
  if (isParked)
  {
    Serial.print( "Parked\t" );
  }
  else
  {
    Serial.print( "Not Parked\t" );
  }
  if (openPinValue)
  {
    Serial.print( "Open\t" );
  }
  else
  {
    Serial.print( "Not Open\t" );
  }
  if (mountSupplied)
  {
    Serial.print( "Mount Supplied\t" );
  }
  else
  {
    Serial.print( "Mount cut off\t" );
  }
  if (forceMountOn)
  {
    Serial.print( "ForceMountOn Active\t" );
  }
  else
  {
    Serial.print( "ForceMountOn Not Active\t" );
  }  Serial.print("\t");  // tabs in between axes
  Serial.println();

  delay(100);  // Delay here for visibility
}

void readAccelData(int *destination)
{
  byte rawData[6];  // x/y/z accel register data stored here

  readRegisters(OUT_X_MSB, 6, rawData);  // Read the six raw data registers into data array

  // Loop to calculate 12-bit ADC and g value for each axis
  for (int i = 0; i < 3 ; i++)
  {
    int gCount = (rawData[i * 2] << 8) | rawData[(i * 2) + 1]; //Combine the two 8 bit registers into one 12-bit number
    gCount >>= 4; //The registers are left align, here we right align the 12-bit integer

    // If the number is negative, we have to make it so manually (no 12-bit data type)
    if (rawData[i * 2] > 0x7F)
    {
      gCount = ~gCount + 1;
      gCount *= -1;  // Transform into negative 2's complement #
    }

    destination[i] = gCount; //Record this gCount into the 3 int array
  }
}

// Initialize the MMA8452 registers
// See the many application notes for more info on setting all of these registers:
// http://www.freescale.com/webapp/sps/site/prod_summary.jsp?code=MMA8452Q
void initMMA8452()
{
  byte c = readRegister(WHO_AM_I);  // Read WHO_AM_I register
  if (c == 0x2A) // WHO_AM_I should always be 0x2A
  {
    Serial.println("MMA8452Q is online...");
  }
  else
  {
    Serial.print("Could not connect to MMA8452Q: 0x");
    Serial.println(c, HEX);
    while (1) ; // Loop forever if communication doesn't happen
  }

  MMA8452Standby();  // Must be in standby to change registers

  // Set up the full scale range to 2, 4, or 8g.
  byte fsr = GSCALE;
  if (fsr > 8) fsr = 8; //Easy error check
  fsr >>= 2; // Neat trick, see page 22. 00 = 2G, 01 = 4A, 10 = 8G
  writeRegister(XYZ_DATA_CFG, fsr);

  //The default data rate is 800Hz and we don't modify it in this example code

  MMA8452Active();  // Set to active to start reading
}

// Sets the MMA8452 to standby mode. It must be in standby to change most register settings
void MMA8452Standby()
{
  byte c = readRegister(CTRL_REG1);
  writeRegister(CTRL_REG1, c & ~(0x01)); //Clear the active bit to go into standby
}

// Sets the MMA8452 to active mode. Needs to be in this mode to output data
void MMA8452Active()
{
  byte c = readRegister(CTRL_REG1);
  writeRegister(CTRL_REG1, c | 0x01); //Set the active bit to begin detection
}

// Read bytesToRead sequentially, starting at addressToRead into the dest byte array
void readRegisters(byte addressToRead, int bytesToRead, byte * dest)
{
  Wire.beginTransmission(MMA8452_ADDRESS);
  Wire.write(addressToRead);
  Wire.endTransmission(false); //endTransmission but keep the connection active

  Wire.requestFrom(MMA8452_ADDRESS, bytesToRead); //Ask for bytes, once done, bus is released by default

  while (Wire.available() < bytesToRead); //Hang out until we get the # of bytes we expect

  for (int x = 0 ; x < bytesToRead ; x++)
    dest[x] = Wire.read();
}

// Read a single byte from addressToRead and return it as a byte
byte readRegister(byte addressToRead)
{
  Wire.beginTransmission(MMA8452_ADDRESS);
  Wire.write(addressToRead);
  Wire.endTransmission(false); //endTransmission but keep the connection active

  Wire.requestFrom(MMA8452_ADDRESS, 1); //Ask for 1 byte, once done, bus is released by default

  while (!Wire.available()) ; //Wait for the data to come back
  return Wire.read(); //Return this one byte
}

// Writes a single byte (dataToWrite) into addressToWrite
void writeRegister(byte addressToWrite, byte dataToWrite)
{
  Wire.beginTransmission(MMA8452_ADDRESS);
  Wire.write(addressToWrite);
  Wire.write(dataToWrite);
  Wire.endTransmission(); //Stop transmitting
}

