#include <EEPROM.h>

#define PH_PROBE_PIN A8

#define X_STEP_PIN 2
#define X_DIR_PIN 3
#define X_ENABLE_PIN 5

#define Y_STEP_PIN 39
#define Y_DIR_PIN 41
#define Y_ENABLE_PIN 37

#define Z_STEP_PIN 38
#define Z_DIR_PIN 40
#define Z_ENABLE_PIN 36

#define Z_SUCK_STEP_PIN 32
#define Z_SUCK_DIR_PIN 34
#define Z_SUCK_ENABLE_PIN 30

#define Z_AIRDRY_STEP_PIN 33
#define Z_AIRDRY_DIR_PIN 35
#define Z_AIRDRY_ENABLE_PIN 31

#define Z_FLUSH_STEP_PIN 28
#define Z_FLUSH_DIR_PIN 29
#define Z_FLUSH_ENABLE_PIN 27

#define PUMP_1_STEP_PIN 14
#define PUMP_1_DIR_PIN 4
#define PUMP_1_ENABLE_PIN 15

#define PUMP_2_STEP_PIN 17
#define PUMP_2_DIR_PIN 16
#define PUMP_2_ENABLE_PIN 18

#define PUMP_3_STEP_PIN 22
#define PUMP_3_DIR_PIN 19
#define PUMP_3_ENABLE_PIN 23

#define PUMP_4_STEP_PIN 25
#define PUMP_4_DIR_PIN 26
#define PUMP_4_ENABLE_PIN 24

#define DC_PUMP_1_STEP_PIN 42
#define DC_PUMP_1_DIR_PIN 43

#define DC_PUMP_2_STEP_PIN 45
#define DC_PUMP_2_DIR_PIN 44

#define DC_PUMP_3_STEP_PIN 46
#define DC_PUMP_3_DIR_PIN 47

#define DC_PUMP_4_STEP_PIN 49
#define DC_PUMP_4_DIR_PIN 48

#define DC_PUMP_5_STEP_PIN 50
#define DC_PUMP_5_DIR_PIN 51

#define DC_PUMP_6_STEP_PIN 53
#define DC_PUMP_6_DIR_PIN 52

#define X_SWITCH 13
#define Y_SWITCH 12
#define Z_SWITCH 11
#define Z_SUCK_SWITCH 10
#define Z_FLUSH_SWITCH 9
#define Z_AIRDRY_SWITCH 8

#define POWER_RELAY 6

#define AIRDRY_DC 11 // blow
#define SUCK_DC 6 // suck
#define FLUSH_DC 5 // flush

int xSwitchState = 1;
int ySwitchState = 1;
int zSwitchState = 1;

int zSuckSwitchState = 1;
int zFlushSwitchState = 1;
int zAirdrySwitchState = 1;

long X_POS;
long Y_POS;
long Z_POS;
long Z_SUCK_POS;
long Z_FLUSH_POS;
long Z_AIRDRY_POS;

const long X_MAX = 11000;
const long Y_MAX = 11000;
const long Z_MAX = 11000;
const long Z_SUCK_MAX = 100000;
const long Z_FLUSH_MAX = 100000;
const long Z_AIRDRY_MAX = 100000;

// temporary array for use when parsing
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];

// variables to hold the parsed data
char selectionFromPC[numChars] = {
  0
};
long inputOneFromPC = 0;
long inputTwoFromPC = 0;

// total steps motors should move
long X_totalSteps = 0;
long Y_totalSteps = 0;
long Z_totalSteps = 0;
long PUMP1_totalSteps = 0;
long PUMP2_totalSteps = 0;
long PUMP3_totalSteps = 0;
long PUMP4_totalSteps = 0;
long Z_airdry_totalSteps = 0;
long Z_suck_totalSteps = 0;
long Z_flush_totalSteps = 0;
long DCPUMP1_totalSteps = 0;
long DCPUMP2_totalSteps = 0;
long DCPUMP3_totalSteps = 0;
long DCPUMP4_totalSteps = 0;
long DCPUMP5_totalSteps = 0;
long DCPUMP6_totalSteps = 0;

unsigned long previousXtime = micros();
unsigned long previousYtime = micros();
unsigned long previousZtime = micros();
unsigned long previousPump1time = micros();
unsigned long previousPump2time = micros();
unsigned long previousPump3time = micros();
unsigned long previousPump4time = micros();
unsigned long previousZairdrytime = micros();
unsigned long previousZsucktime = micros();
unsigned long previousZflushtime = micros();
unsigned long previousDCPump1time = micros();
unsigned long previousDCPump2time = micros();
unsigned long previousDCPump3time = micros();
unsigned long previousDCPump4time = micros();
unsigned long previousDCPump5time = micros();
unsigned long previousDCPump6time = micros();

long X_interval;
long Y_interval;
long Z_interval;
long pump1_interval;
long pump2_interval;
long pump3_interval;
long pump4_interval;
long Z_airdry_interval;
long Z_suck_interval;
long Z_flush_interval;
long dcpump1_HIGHinterval;
long dcpump2_HIGHinterval;
long dcpump3_HIGHinterval;
long dcpump4_HIGHinterval;
long dcpump5_HIGHinterval;
long dcpump6_HIGHinterval;
long dcpump1_LOWinterval;
long dcpump2_LOWinterval;
long dcpump3_LOWinterval;
long dcpump4_LOWinterval;
long dcpump5_LOWinterval;
long dcpump6_LOWinterval;

boolean newData = false;
boolean toDo = false;
boolean stepCorrection = false;

boolean HIGH1 = false;
boolean HIGH2 = false;
boolean HIGH3 = false;
boolean HIGH4 = false;
boolean HIGH5 = false;
boolean HIGH6 = false;

boolean xCommand = false;
boolean yCommand = false;
boolean zCommand = false;
boolean zSuckCommand = false;
boolean zFlushCommand = false;
boolean zAirdryCommand = false;
boolean pump1Command = false;
boolean pump2Command = false;
boolean pump3Command = false;
boolean pump4Command = false;
boolean DC1Command = false;
boolean DC2Command = false;
boolean DC3Command = false;
boolean DC4Command = false;
boolean DC5Command = false;
boolean DC6Command = false;

float PH_4 = 1.992;
float PH_7 = 1.477;

long PH_4_address = 5L;                    // EEPROM
long PH_7_address = 10L;                    // EEPROM

bool PHmeasure = false;
//====================================

void setup() {
  Serial.begin(115200);
  //Serial.println("Enter data in this style <Motor, Interval, Steps>  ");
  //Serial.println("Ex: <X_STEPPER, 1000, 10000>  ");
  //Serial.println();
  /*
  Stepper Motor Options: X_STEPPER, Y_STEPPER, Z_STEPPER, 
  Z_CLEANER, Z_ARGON, Z_DISPENSER, PUMP1_STEPPER,
  PUMP2_STEPPER, PUMP3_STEPPER, PUMP4_STEPPER
  DC Motor Options: FLUSH_DC, SUCK_DC, AIRDRY_DC
  INPUT INTEGER RANGE: -32000 to 32000
  */

  pinMode(POWER_RELAY, OUTPUT);
  digitalWrite(POWER_RELAY, LOW);

  pinMode(X_SWITCH, INPUT_PULLUP);
  pinMode(Y_SWITCH, INPUT_PULLUP);
  pinMode(Z_SWITCH, INPUT_PULLUP);
  
  pinMode(Z_SUCK_SWITCH, INPUT_PULLUP);
  pinMode(Z_FLUSH_SWITCH, INPUT_PULLUP);
  pinMode(Z_AIRDRY_SWITCH, INPUT_PULLUP);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);
  digitalWrite(X_ENABLE_PIN, LOW);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  digitalWrite(Y_ENABLE_PIN, LOW);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  digitalWrite(Z_ENABLE_PIN, LOW);

  pinMode(Z_SUCK_STEP_PIN, OUTPUT);
  pinMode(Z_SUCK_DIR_PIN, OUTPUT);
  pinMode(Z_SUCK_ENABLE_PIN, OUTPUT);
  digitalWrite(Z_SUCK_ENABLE_PIN, HIGH);

  pinMode(Z_FLUSH_STEP_PIN, OUTPUT);
  pinMode(Z_FLUSH_DIR_PIN, OUTPUT);
  pinMode(Z_FLUSH_ENABLE_PIN, OUTPUT);
  digitalWrite(Z_FLUSH_ENABLE_PIN, HIGH);

  pinMode(Z_AIRDRY_STEP_PIN, OUTPUT);
  pinMode(Z_AIRDRY_DIR_PIN, OUTPUT);
  pinMode(Z_AIRDRY_ENABLE_PIN, OUTPUT);
  digitalWrite(Z_AIRDRY_ENABLE_PIN, HIGH);

  pinMode(PUMP_1_STEP_PIN, OUTPUT);
  //pinMode(PUMP_1_DIR_PIN, OUTPUT);
  pinMode(PUMP_1_ENABLE_PIN, OUTPUT);
  digitalWrite(PUMP_1_ENABLE_PIN, LOW);

  pinMode(PUMP_2_STEP_PIN, OUTPUT);
  pinMode(PUMP_2_DIR_PIN, OUTPUT);
  pinMode(PUMP_2_ENABLE_PIN, OUTPUT);
  digitalWrite(PUMP_2_ENABLE_PIN, LOW);

  pinMode(PUMP_3_STEP_PIN, OUTPUT);
  pinMode(PUMP_3_DIR_PIN, OUTPUT);
  pinMode(PUMP_3_ENABLE_PIN, OUTPUT);
  digitalWrite(PUMP_3_ENABLE_PIN, LOW);

  pinMode(PUMP_4_STEP_PIN, OUTPUT);
  pinMode(PUMP_4_DIR_PIN, OUTPUT);
  pinMode(PUMP_4_ENABLE_PIN, OUTPUT);
  digitalWrite(PUMP_4_ENABLE_PIN, LOW);
  
  pinMode(DC_PUMP_1_STEP_PIN, OUTPUT);
  pinMode(DC_PUMP_1_DIR_PIN, OUTPUT);

  pinMode(DC_PUMP_2_STEP_PIN, OUTPUT);
  pinMode(DC_PUMP_2_DIR_PIN, OUTPUT);

  pinMode(DC_PUMP_3_STEP_PIN, OUTPUT);
  pinMode(DC_PUMP_3_DIR_PIN, OUTPUT);

  pinMode(DC_PUMP_4_STEP_PIN, OUTPUT);
  pinMode(DC_PUMP_4_DIR_PIN, OUTPUT); 

  pinMode(DC_PUMP_5_STEP_PIN, OUTPUT);
  pinMode(DC_PUMP_5_DIR_PIN, OUTPUT); 

  pinMode(DC_PUMP_6_STEP_PIN, OUTPUT);
  pinMode(DC_PUMP_6_DIR_PIN, OUTPUT); 

  //homing();

  EEPROM.get(PH_4_address, PH_4);      // get the zero cal factor from EEPROM
  EEPROM.get(PH_7_address, PH_7);    // get the cal factor from EEPROM
}

//====================================

void loop() {
  recvWithStartEndMarkers();
  if (newData == true) {
    strcpy(tempChars, receivedChars);
    // this temporary copy is necessary to protect the original data
    //   because strtok() used in parseData() replaces the commas with \0
    parseData();
    //showParsedData();
    newData = false;
    toDo = true;
    stepCorrection = true;
  }

  if (PHmeasure == true){
    float Po = analogRead(PH_PROBE_PIN) * 5.0 / 1024;
    float phValue = 7 - (2.5 - Po) * (PH_7 - PH_4) / (PH_7 - PH_4);
    Serial.print("<PH,");
    Serial.print(phValue);
    Serial.println(",0>");
  }
  
  digitalWrite(X_STEP_PIN, LOW);
  digitalWrite(Y_STEP_PIN, LOW);
  digitalWrite(Z_STEP_PIN, LOW);
  
  digitalWrite(Z_SUCK_STEP_PIN, LOW);
  digitalWrite(Z_FLUSH_STEP_PIN, LOW);
  digitalWrite(Z_AIRDRY_STEP_PIN, LOW);
  
  digitalWrite(PUMP_1_STEP_PIN, LOW);
  digitalWrite(PUMP_2_STEP_PIN, LOW);
  digitalWrite(PUMP_3_STEP_PIN, LOW);
  digitalWrite(PUMP_4_STEP_PIN, LOW);

  X_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Y_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Z_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  
  Z_Suck_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Z_Flush_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Z_Airdry_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  
  Pump1_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Pump2_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Pump3_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  Pump4_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);

  DCPump1_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  DCPump2_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  DCPump3_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  DCPump4_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  DCPump5_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);
  DCPump6_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);

  Calibration(selectionFromPC, inputOneFromPC);
  Measure(selectionFromPC, inputOneFromPC);

  Power_Relay_Control(selectionFromPC, inputOneFromPC, inputTwoFromPC);

  homeGantry(selectionFromPC);
  homeDisp(selectionFromPC);
}

void PH4_Cal_Adjust() {
  int cal_counter = 20;     // total number of readings

  int average;
  
  for (int i=0; i < 20; i++) {  // create a moving average with an IIR filter
    average = analogRead(PH_PROBE_PIN);
    Serial.println(average);
    cal_counter--;
    delay(100);
  }

  PH_4 = ((float)average / 20) * 5 / 1024;
  
  EEPROM.put(PH_4_address, PH_4);     // store binary offset calibration factor in EEPROM
  Serial.print("Finished 4: ");
  Serial.println(PH_4);
}
/**************************************************************************************
 * routine to check if the calibration command was sent
 */
void PH7_Cal_Adjust() {
  int cal_counter = 20;     // total number of readings

  int average = 0;
  
  for (int i=0; i < 20; i++) {  // create a moving average with an IIR filter
    average += analogRead(PH_PROBE_PIN);
    Serial.println(average);
    cal_counter--;
    delay(100);
  }
  PH_7 = ((float)average / 20) * 5 / 1024;
  
  EEPROM.put(PH_7_address, PH_7);     // store binary offset calibration factor in EEPROM
  Serial.print("Finished 7: ");
  Serial.println(PH_7);
}
/**************************************************************************************
 * routine to check if the calibration command was sent
 */
void Calibration(char * commandType, long data1) {
  if (strcmp(commandType, "CAL") == 0 && toDo == true) {
    toDo = false;
    if (data1 == 4){
      PH4_Cal_Adjust();
    }
    if (data1 == 7){
      PH7_Cal_Adjust();
    }
  }
}
/**************************************************************************************
 * routine to check if the calibration command was sent
 */
void Measure(char * commandType, long data1){
  if (strcmp(commandType, "PH") == 0 && toDo == true) {
    toDo = false;
    PHmeasure = data1;
  }
}

//====================================
void X_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "X") == 0 && toDo == true) {
    //Serial.println(selectionFromPC);
    toDo = false;
    xCommand = true;

    long newSteps;
    if (X_POS + steps < 0 && stepCorrection == true) {
      newSteps = 0 - X_POS;
      X_POS = 0;
      //Serial.println("1");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (X_POS + steps > X_MAX && stepCorrection == true) {
      newSteps = X_MAX - X_POS;
      X_POS = X_MAX;
      //Serial.println("2");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (X_POS + steps >= 0 && X_POS + steps <= X_MAX && stepCorrection == true) {
      newSteps = steps;
      //Serial.println(steps);
      //Serial.println(newSteps);
      X_POS += newSteps;
      //Serial.println("3");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    X_totalSteps += newSteps;
    //Serial.println(X_totalSteps);
    X_interval = long(stepSpeed);
  }

  unsigned long currentXtime = micros();
  if (X_totalSteps > 0 && currentXtime - previousXtime > X_interval) {
    digitalWrite(X_DIR_PIN, LOW);
    digitalWrite(X_STEP_PIN, HIGH);
    previousXtime = currentXtime;
    //Serial.println(X_totalSteps);
    X_totalSteps--;
  }
  if (X_totalSteps < 0 && currentXtime - previousXtime > X_interval) {
    digitalWrite(X_DIR_PIN, HIGH);
    digitalWrite(X_STEP_PIN, HIGH);
    previousXtime = currentXtime;
    //Serial.println(X_totalSteps);
    X_totalSteps++;
  }
  if (X_totalSteps == 0 && xCommand == true) {
    xCommand = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}
//====================================
void Y_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "Y") == 0 && toDo == true) {
    //Serial.println("Y ACTIVATED");
    toDo = false;
    yCommand = true;

    long newSteps;
    if (Y_POS + steps < 0 && stepCorrection == true) {
      newSteps = 0 - Y_POS;
      Y_POS = 0;
      //Serial.println("1");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Y_POS + steps > Y_MAX && stepCorrection == true) {
      newSteps = Y_MAX - Y_POS;
      Y_POS = Y_MAX;
      //Serial.println("2");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Y_POS + steps >= 0 && Y_POS + steps <= Y_MAX && stepCorrection == true) {
      newSteps = steps;
      Y_POS += newSteps;
      //Serial.println("3");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    Y_totalSteps += newSteps;
    //Serial.println(Y_totalSteps);

    Y_interval = long(stepSpeed);
  }
  unsigned long currentYtime = micros();
  if (Y_totalSteps > 0 && currentYtime - previousYtime > Y_interval) {
    digitalWrite(Y_DIR_PIN, LOW);
    digitalWrite(Y_STEP_PIN, HIGH);
    previousYtime = currentYtime;
    //Serial.println(Y_totalSteps);
    Y_totalSteps--;
  }
  if (Y_totalSteps < 0 && currentYtime - previousYtime > Y_interval) {
    digitalWrite(Y_DIR_PIN, HIGH);
    digitalWrite(Y_STEP_PIN, HIGH);
    previousYtime = currentYtime;
    //Serial.println(Y_totalSteps);
    Y_totalSteps++;
  }
  if (Y_totalSteps == 0 && yCommand == true) {
    yCommand = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void Z_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "Z") == 0 && toDo == true) {
    //Serial.println("Z ACTIVATED");
    toDo = false;
    zCommand = true;

    long newSteps;
    if (Z_POS + steps < 0 && stepCorrection == true) {
      newSteps = 0 - Z_POS;
      Z_POS = 0;
      //Serial.println("1");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_POS + steps > Z_MAX && stepCorrection == true) {
      newSteps = Z_MAX - Z_POS;
      Z_POS = Z_MAX;
      //Serial.println("2");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_POS + steps >= 0 && Z_POS + steps <= Z_MAX && stepCorrection == true) {
      newSteps = steps;
      Z_POS += newSteps;
      //Serial.println("3");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    Z_totalSteps += newSteps;
    Z_interval = long(stepSpeed);
  }
  unsigned long currentZtime = micros();
  if (Z_totalSteps > 0 && currentZtime - previousZtime > Z_interval) {
    digitalWrite(Z_DIR_PIN, LOW);
    digitalWrite(Z_STEP_PIN, HIGH);
    previousZtime = currentZtime;
    //Serial.println(Z_totalSteps);
    Z_totalSteps--;
  }
  if (Z_totalSteps < 0 && currentZtime - previousZtime > Z_interval) {
    digitalWrite(Z_DIR_PIN, HIGH);
    digitalWrite(Z_STEP_PIN, HIGH);
    previousZtime = currentZtime;
    //Serial.println(Z_totalSteps);
    Z_totalSteps++;
  }
  if (Z_totalSteps == 0 && zCommand == true) {
    zCommand = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void Z_Suck_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "ZFLUSH") == 0 && toDo == true) {
    //Serial.println("Z SUCK ACTIVATED");
    toDo = false;
    zSuckCommand = true;

    long newSteps;
    if (Z_SUCK_POS + steps < 0 && stepCorrection == true) {
      newSteps = 0 - Z_SUCK_POS;
      Z_SUCK_POS = 0;
      //Serial.println("1");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_SUCK_POS + steps > Z_SUCK_MAX && stepCorrection == true) {
      newSteps = Z_SUCK_MAX - Z_SUCK_POS;
      Z_SUCK_POS = Z_SUCK_MAX;
      //Serial.println("2");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_SUCK_POS + steps >= 0 && Z_SUCK_POS + steps <= Z_SUCK_MAX && stepCorrection == true) {
      newSteps = steps;
      Z_SUCK_POS += newSteps;
      //Serial.println("3");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    Z_suck_totalSteps += newSteps;
    Z_suck_interval = long(stepSpeed);
  }
  unsigned long currentZsucktime = micros();
  if (Z_suck_totalSteps > 0 && currentZsucktime - previousZsucktime > Z_suck_interval) {
    digitalWrite(Z_SUCK_ENABLE_PIN, LOW);
    digitalWrite(Z_SUCK_DIR_PIN, LOW);
    digitalWrite(Z_SUCK_STEP_PIN, HIGH);
    previousZsucktime = currentZsucktime;
    //Serial.println(Z_totalSteps);
    Z_suck_totalSteps--;
  }
  if (Z_suck_totalSteps < 0 && currentZsucktime - previousZsucktime > Z_suck_interval) {
    digitalWrite(Z_SUCK_ENABLE_PIN, LOW);
    digitalWrite(Z_SUCK_DIR_PIN, HIGH);
    digitalWrite(Z_SUCK_STEP_PIN, HIGH);
    previousZsucktime = currentZsucktime;
    //Serial.println(Z_totalSteps);
    Z_suck_totalSteps++;
  }
  if (Z_suck_totalSteps == 0 && zSuckCommand == true) {
    zSuckCommand = false;
    digitalWrite(Z_SUCK_ENABLE_PIN, HIGH);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}
//=======================================================
void Z_Flush_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "ZAIRDRY") == 0 && toDo == true) {
    //Serial.println("Z FLUSH ACTIVATED");
    toDo = false;
    zFlushCommand = true;

    long newSteps;
    if (Z_FLUSH_POS + steps < 0 && stepCorrection == true) {
      newSteps = 0 - Z_FLUSH_POS;
      Z_FLUSH_POS = 0;
      //Serial.println("1");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_FLUSH_POS + steps > Z_FLUSH_MAX && stepCorrection == true) {
      newSteps = Z_FLUSH_MAX - Z_FLUSH_POS;
      Z_FLUSH_POS = Z_FLUSH_MAX;
      //Serial.println("2");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_FLUSH_POS + steps >= 0 && Z_FLUSH_POS + steps <= Z_FLUSH_MAX && stepCorrection == true) {
      newSteps = steps;
      Z_FLUSH_POS += newSteps;
      //Serial.println("3");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    Z_flush_totalSteps += newSteps;
    Z_flush_interval = long(stepSpeed);
  }
  unsigned long currentZflushtime = micros();
  if (Z_flush_totalSteps > 0 && currentZflushtime - previousZflushtime > Z_flush_interval) {
    digitalWrite(Z_FLUSH_ENABLE_PIN, LOW);
    digitalWrite(Z_FLUSH_DIR_PIN, LOW);
    digitalWrite(Z_FLUSH_STEP_PIN, HIGH);
    previousZflushtime = currentZflushtime;
    //Serial.println(Z_totalSteps);
    Z_flush_totalSteps--;
  }
  if (Z_flush_totalSteps < 0 && currentZflushtime - previousZflushtime > Z_flush_interval) {
    digitalWrite(Z_FLUSH_ENABLE_PIN, LOW);
    digitalWrite(Z_FLUSH_DIR_PIN, HIGH);
    digitalWrite(Z_FLUSH_STEP_PIN, HIGH);
    previousZflushtime = currentZflushtime;
    //Serial.println(Z_totalSteps);
    Z_flush_totalSteps++;
  }
  if (Z_flush_totalSteps == 0 && zFlushCommand == true) {
    zFlushCommand = false;
    digitalWrite(Z_FLUSH_ENABLE_PIN, HIGH);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
  
}

//=======================================================
void Z_Airdry_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "ZDISP") == 0 && toDo == true) {
    //Serial.println("Z AIRDRY ACTIVATED");
    toDo = false;
    zAirdryCommand = true;

    long newSteps;
    if (Z_AIRDRY_POS + steps < 0 && stepCorrection == true) {
      newSteps = 0 - Z_AIRDRY_POS;
      Z_AIRDRY_POS = 0;
      //Serial.println("1");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_AIRDRY_POS + steps > Z_AIRDRY_MAX && stepCorrection == true) {
      newSteps = Z_AIRDRY_MAX - Z_AIRDRY_POS;
      Z_AIRDRY_POS = Z_AIRDRY_MAX;
      //Serial.println("2");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    if (Z_AIRDRY_POS + steps >= 0 && Z_AIRDRY_POS + steps <= Z_AIRDRY_MAX && stepCorrection == true) {
      newSteps = steps;
      Z_AIRDRY_POS += newSteps;
      //Serial.println("3");
      //Serial.println(newSteps);
      stepCorrection = false;
    }

    Z_airdry_totalSteps += newSteps;
    Z_airdry_interval = long(stepSpeed);
  }
  unsigned long currentZairdrytime = micros();
  if (Z_airdry_totalSteps > 0 && currentZairdrytime - previousZairdrytime > Z_airdry_interval) {
    digitalWrite(Z_AIRDRY_ENABLE_PIN, LOW);
    digitalWrite(Z_AIRDRY_DIR_PIN, LOW);
    digitalWrite(Z_AIRDRY_STEP_PIN, HIGH);
    previousZairdrytime = currentZairdrytime;
    //Serial.println(Z_totalSteps);
    Z_airdry_totalSteps--;
  }
  if (Z_airdry_totalSteps < 0 && currentZairdrytime - previousZairdrytime > Z_airdry_interval) {
    digitalWrite(Z_AIRDRY_ENABLE_PIN, LOW);
    digitalWrite(Z_AIRDRY_DIR_PIN, HIGH);
    digitalWrite(Z_AIRDRY_STEP_PIN, HIGH);
    previousZairdrytime = currentZairdrytime;
    //Serial.println(Z_totalSteps);
    Z_airdry_totalSteps++;
  }
  if (Z_airdry_totalSteps == 0 && zAirdryCommand == true) {
    zAirdryCommand = false;
    digitalWrite(Z_AIRDRY_ENABLE_PIN, HIGH);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void Pump1_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "PUMP1") == 0 && toDo == true) {
    toDo = false;
    pump1Command = true;

    PUMP1_totalSteps += steps;
    //Serial.println(PUMP1_totalSteps);
    pump1_interval = long(stepSpeed);
  }
  unsigned long currentPump1time = micros();
  if (PUMP1_totalSteps > 0 && currentPump1time - previousPump1time > pump1_interval) {
    digitalWrite(PUMP_1_DIR_PIN, LOW);
    digitalWrite(PUMP_1_STEP_PIN, HIGH);
    previousPump1time = currentPump1time;
    //Serial.println(PUMP1_totalSteps);
    PUMP1_totalSteps--;
  }
  if (PUMP1_totalSteps < 0 && currentPump1time - previousPump1time > pump1_interval) {
    digitalWrite(PUMP_1_DIR_PIN, HIGH);
    digitalWrite(PUMP_1_STEP_PIN, HIGH);
    previousPump1time = currentPump1time;
    //Serial.println(PUMP1_totalSteps);
    PUMP1_totalSteps++;
  }
  if (PUMP1_totalSteps == 0 && pump1Command == true) {
    pump1Command = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void Pump2_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "PUMP2") == 0 && toDo == true) {
    toDo = false;
    pump2Command = true;

    PUMP2_totalSteps += steps;
    pump2_interval = long(stepSpeed);
  }
  unsigned long currentPump2time = micros();
  if (PUMP2_totalSteps > 0 && currentPump2time - previousPump2time > pump2_interval) {
    digitalWrite(PUMP_2_DIR_PIN, LOW);
    digitalWrite(PUMP_2_STEP_PIN, HIGH);
    previousPump2time = currentPump2time;
    PUMP2_totalSteps--;
  }
  if (PUMP2_totalSteps < 0 && currentPump2time - previousPump2time > pump2_interval) {
    digitalWrite(PUMP_2_DIR_PIN, HIGH);
    digitalWrite(PUMP_2_STEP_PIN, HIGH);
    previousPump2time = currentPump2time;
    PUMP2_totalSteps++;
  }
  if (PUMP2_totalSteps == 0 && pump2Command == true) {
    pump2Command = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void Pump3_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "PUMP3") == 0 && toDo == true) {
    toDo = false;
    pump3Command = true;

    PUMP3_totalSteps += steps;
    pump3_interval = long(stepSpeed);
  }
  unsigned long currentPump3time = micros();
  if (PUMP3_totalSteps > 0 && currentPump3time - previousPump3time > pump3_interval) {
    digitalWrite(PUMP_3_DIR_PIN, LOW);
    digitalWrite(PUMP_3_STEP_PIN, HIGH);
    previousPump3time = currentPump3time;
    PUMP3_totalSteps--;
  }
  if (PUMP3_totalSteps < 0 && currentPump3time - previousPump3time > pump3_interval) {
    digitalWrite(PUMP_3_DIR_PIN, HIGH);
    digitalWrite(PUMP_3_STEP_PIN, HIGH);
    previousPump3time = currentPump3time;
    PUMP3_totalSteps++;
  }
  if (PUMP3_totalSteps == 0 && pump3Command == true) {
    pump3Command = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void Pump4_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "PUMP4") == 0 && toDo == true) {
    toDo = false;
    pump4Command = true;
    
    //Serial.println("4 activated");
    PUMP4_totalSteps += steps;
    pump4_interval = long(stepSpeed);
  }
  unsigned long currentPump4time = micros();
  if (PUMP4_totalSteps > 0 && currentPump4time - previousPump4time > pump4_interval) {
    digitalWrite(PUMP_4_DIR_PIN, HIGH);
    digitalWrite(PUMP_4_STEP_PIN, HIGH);
    previousPump4time = currentPump4time;
    PUMP4_totalSteps--;
  }
  if (PUMP4_totalSteps < 0 && currentPump4time - previousPump4time > pump4_interval) {
    digitalWrite(PUMP_4_DIR_PIN, LOW);
    digitalWrite(PUMP_4_STEP_PIN, HIGH);
    previousPump4time = currentPump4time;
    PUMP4_totalSteps++;
  }
  if (PUMP4_totalSteps == 0 && pump4Command == true) {
    pump4Command = false;
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void DCPump1_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "DC1") == 0 && toDo == true) {
    toDo = false;
    DC1Command = true;
    
    //Serial.println("DC 1 activated");
    DCPUMP1_totalSteps += steps;
    dcpump1_LOWinterval = long(stepSpeed);
    dcpump1_HIGHinterval = abs(long(255)-long(stepSpeed));
  }
  unsigned long currentDCPump1time = micros();
  if (DCPUMP1_totalSteps > 0 && currentDCPump1time - previousDCPump1time > dcpump1_HIGHinterval && HIGH1 == true) {
    digitalWrite(DC_PUMP_1_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_1_STEP_PIN, HIGH);
    previousDCPump1time = currentDCPump1time;
    DCPUMP1_totalSteps--;
    //Serial.println(DCPUMP1_totalSteps);
    HIGH1 = false;
  }
  if (DCPUMP1_totalSteps > 0 && currentDCPump1time - previousDCPump1time > dcpump1_LOWinterval && HIGH1 == false) {
    digitalWrite(DC_PUMP_1_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_1_STEP_PIN, LOW);
    previousDCPump1time = currentDCPump1time;
    HIGH1 = true;
  }
  if (DCPUMP1_totalSteps < 0 && currentDCPump1time - previousDCPump1time > dcpump1_HIGHinterval && HIGH1 == true) {
    digitalWrite(DC_PUMP_1_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_1_STEP_PIN, HIGH);
    previousDCPump1time = currentDCPump1time;
    PUMP1_totalSteps++;
    //Serial.println(DCPUMP1_totalSteps);
    HIGH1 = false;
  }
  if (DCPUMP1_totalSteps < 0 && currentDCPump1time - previousDCPump1time > dcpump1_LOWinterval && HIGH1 == false) {
    digitalWrite(DC_PUMP_1_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_1_STEP_PIN, LOW);
    previousDCPump1time = currentDCPump1time;
    HIGH1 = true;
  }
  if (DCPUMP1_totalSteps == 0 && DC1Command == true) {
    DC1Command = false;
    digitalWrite(DC_PUMP_1_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_1_STEP_PIN, LOW);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}



//====================================
void DCPump2_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "DC2") == 0 && toDo == true) {
    toDo = false;
    DC2Command = true;
    
    //Serial.println("DC 2 activated");
    DCPUMP2_totalSteps += steps;
    dcpump2_LOWinterval = long(stepSpeed);
    dcpump2_HIGHinterval = abs(long(255)-long(stepSpeed));
  }
  unsigned long currentDCPump2time = micros();
  if (DCPUMP2_totalSteps > 0 && currentDCPump2time - previousDCPump2time > dcpump2_HIGHinterval && HIGH2 == true) {
    digitalWrite(DC_PUMP_2_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_2_STEP_PIN, HIGH);
    previousDCPump2time = currentDCPump2time;
    DCPUMP2_totalSteps--;
    //Serial.println(DCPUMP2_totalSteps);
    HIGH2 = false;
  }
  if (DCPUMP2_totalSteps > 0 && currentDCPump2time - previousDCPump2time > dcpump2_LOWinterval && HIGH2 == false) {
    digitalWrite(DC_PUMP_2_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_2_STEP_PIN, LOW);
    previousDCPump2time = currentDCPump2time;
    HIGH2 = true;
  }
  if (DCPUMP2_totalSteps < 0 && currentDCPump2time - previousDCPump2time > dcpump2_HIGHinterval && HIGH2 == true) {
    digitalWrite(DC_PUMP_2_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_2_STEP_PIN, HIGH);
    previousDCPump2time = currentDCPump2time;
    PUMP2_totalSteps++;
    //Serial.println(DCPUMP2_totalSteps);
    HIGH2 = false;
  }
  if (DCPUMP2_totalSteps < 0 && currentDCPump2time - previousDCPump2time > dcpump2_LOWinterval && HIGH2 == false) {
    digitalWrite(DC_PUMP_2_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_2_STEP_PIN, LOW);
    previousDCPump2time = currentDCPump2time;
    HIGH2 = true;
  }
  if (DCPUMP2_totalSteps == 0 && DC2Command == true) {
    DC2Command = false;
    digitalWrite(DC_PUMP_2_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_2_STEP_PIN, LOW);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void DCPump3_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "DC3") == 0 && toDo == true) {
    toDo = false;
    DC3Command = true;
    
    //Serial.println("DC 3 activated");
    DCPUMP3_totalSteps += steps;
    dcpump3_LOWinterval = long(stepSpeed);
    dcpump3_HIGHinterval = abs(long(255)-long(stepSpeed));
  }
  unsigned long currentDCPump3time = micros();
  if (DCPUMP3_totalSteps > 0 && currentDCPump3time - previousDCPump3time > dcpump3_HIGHinterval && HIGH3 == true) {
    digitalWrite(DC_PUMP_3_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_3_STEP_PIN, HIGH);
    previousDCPump3time = currentDCPump3time;
    DCPUMP3_totalSteps--;
    //Serial.println(DCPUMP3_totalSteps);
    HIGH3 = false;
  }
  if (DCPUMP3_totalSteps > 0 && currentDCPump3time - previousDCPump3time > dcpump3_LOWinterval && HIGH3 == false) {
    digitalWrite(DC_PUMP_3_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_3_STEP_PIN, LOW);
    previousDCPump3time = currentDCPump3time;
    HIGH3 = true;
  }
  if (DCPUMP3_totalSteps < 0 && currentDCPump3time - previousDCPump3time > dcpump3_HIGHinterval && HIGH3 == true) {
    digitalWrite(DC_PUMP_3_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_3_STEP_PIN, HIGH);
    previousDCPump3time = currentDCPump3time;
    PUMP3_totalSteps++;
    //Serial.println(DCPUMP3_totalSteps);
    HIGH3 = false;
  }
  if (DCPUMP3_totalSteps < 0 && currentDCPump3time - previousDCPump3time > dcpump3_LOWinterval && HIGH3 == false) {
    digitalWrite(DC_PUMP_3_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_3_STEP_PIN, LOW);
    previousDCPump3time = currentDCPump3time;
    HIGH3 = true;
  }
  if (DCPUMP3_totalSteps == 0 && DC3Command == true) {
    DC3Command = false;
    digitalWrite(DC_PUMP_3_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_3_STEP_PIN, LOW);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void DCPump4_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "DC4") == 0 && toDo == true) {
    toDo = false;
    DC4Command = true;
    
    //Serial.println("DC 4 activated");
    DCPUMP4_totalSteps += steps;
    dcpump4_LOWinterval = long(stepSpeed);
    dcpump4_HIGHinterval = abs(long(255)-long(stepSpeed));
  }
  unsigned long currentDCPump4time = micros();
  if (DCPUMP4_totalSteps > 0 && currentDCPump4time - previousDCPump4time > dcpump4_HIGHinterval && HIGH4 == true) {
    digitalWrite(DC_PUMP_4_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_4_STEP_PIN, HIGH);
    previousDCPump4time = currentDCPump4time;
    DCPUMP4_totalSteps--;
    //Serial.println(DCPUMP4_totalSteps);
    HIGH4 = false;
  }
  if (DCPUMP4_totalSteps > 0 && currentDCPump4time - previousDCPump4time > dcpump4_LOWinterval && HIGH4 == false) {
    digitalWrite(DC_PUMP_4_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_4_STEP_PIN, LOW);
    previousDCPump4time = currentDCPump4time;
    HIGH4 = true;
  }
  if (DCPUMP4_totalSteps < 0 && currentDCPump4time - previousDCPump4time > dcpump4_HIGHinterval && HIGH4 == true) {
    digitalWrite(DC_PUMP_4_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_4_STEP_PIN, HIGH);
    previousDCPump4time = currentDCPump4time;
    PUMP4_totalSteps++;
    //Serial.println(DCPUMP4_totalSteps);
    HIGH4 = false;
  }
  if (DCPUMP4_totalSteps < 0 && currentDCPump4time - previousDCPump4time > dcpump4_LOWinterval && HIGH4 == false) {
    digitalWrite(DC_PUMP_4_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_4_STEP_PIN, LOW);
    previousDCPump4time = currentDCPump4time;
    HIGH4 = true;
  }
  if (DCPUMP4_totalSteps == 0 && DC4Command == true) {
    DC4Command = false;
    digitalWrite(DC_PUMP_4_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_4_STEP_PIN, LOW);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void DCPump5_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "DC5") == 0 && toDo == true) {
    toDo = false;
    DC5Command = true;
    
    //Serial.println("DC 5 activated");
    DCPUMP5_totalSteps += steps;
    dcpump5_LOWinterval = long(stepSpeed);
    dcpump5_HIGHinterval = abs(long(255)-long(stepSpeed));
  }
  unsigned long currentDCPump5time = micros();
  if (DCPUMP5_totalSteps > 0 && currentDCPump5time - previousDCPump5time > dcpump5_HIGHinterval && HIGH5 == true) {
    digitalWrite(DC_PUMP_5_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_5_STEP_PIN, HIGH);
    previousDCPump5time = currentDCPump5time;
    DCPUMP5_totalSteps--;
    //Serial.println(DCPUMP5_totalSteps);
    HIGH5 = false;
  }
  if (DCPUMP5_totalSteps > 0 && currentDCPump5time - previousDCPump5time > dcpump5_LOWinterval && HIGH5 == false) {
    digitalWrite(DC_PUMP_5_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_5_STEP_PIN, LOW);
    previousDCPump5time = currentDCPump5time;
    HIGH5 = true;
  }
  if (DCPUMP5_totalSteps < 0 && currentDCPump5time - previousDCPump5time > dcpump5_HIGHinterval && HIGH5 == true) {
    digitalWrite(DC_PUMP_5_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_5_STEP_PIN, HIGH);
    previousDCPump5time = currentDCPump5time;
    DCPUMP5_totalSteps++;
    //Serial.println(DCPUMP5_totalSteps);
    HIGH5 = false;
  }
  if (DCPUMP5_totalSteps < 0 && currentDCPump5time - previousDCPump5time > dcpump5_LOWinterval && HIGH5 == false) {
    digitalWrite(DC_PUMP_5_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_5_STEP_PIN, LOW);
    previousDCPump5time = currentDCPump5time;
    HIGH5 = true;
  }
  if (DCPUMP5_totalSteps == 0 && DC5Command == true) {
    DC5Command = false;
    digitalWrite(DC_PUMP_5_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_5_STEP_PIN, LOW);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}

//====================================
void DCPump6_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "DC6") == 0 && toDo == true) {
    toDo = false;
    DC6Command = true;
    
    //Serial.println("DC 6 activated");
    DCPUMP6_totalSteps += steps;
    dcpump6_LOWinterval = long(stepSpeed);
    dcpump6_HIGHinterval = abs(long(255)-long(stepSpeed));
  }
  unsigned long currentDCPump6time = micros();
  if (DCPUMP6_totalSteps > 0 && currentDCPump6time - previousDCPump6time > dcpump6_HIGHinterval && HIGH6 == true) {
    digitalWrite(DC_PUMP_6_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_6_STEP_PIN, HIGH);
    previousDCPump6time = currentDCPump6time;
    DCPUMP6_totalSteps--;
    //Serial.println(DCPUMP6_totalSteps);
    HIGH6 = false;
  }
  if (DCPUMP6_totalSteps > 0 && currentDCPump6time - previousDCPump6time > dcpump6_LOWinterval && HIGH6 == false) {
    digitalWrite(DC_PUMP_6_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_6_STEP_PIN, LOW);
    previousDCPump6time = currentDCPump6time;
    HIGH6 = true;
  }
  if (DCPUMP6_totalSteps < 0 && currentDCPump6time - previousDCPump6time > dcpump6_HIGHinterval && HIGH6 == true) {
    digitalWrite(DC_PUMP_6_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_6_STEP_PIN, HIGH);
    previousDCPump6time = currentDCPump6time;
    DCPUMP6_totalSteps++;
    //Serial.println(DCPUMP6_totalSteps);
    HIGH6 = false;
  }
  if (DCPUMP6_totalSteps < 0 && currentDCPump6time - previousDCPump6time > dcpump6_LOWinterval && HIGH6 == false) {
    digitalWrite(DC_PUMP_6_DIR_PIN, HIGH);
    digitalWrite(DC_PUMP_6_STEP_PIN, LOW);
    previousDCPump6time = currentDCPump6time;
    HIGH6 = true;
  }
  if (DCPUMP6_totalSteps == 0 && DC6Command == true) {
    DC6Command = false;
    digitalWrite(DC_PUMP_6_DIR_PIN, LOW);
    digitalWrite(DC_PUMP_6_STEP_PIN, LOW);
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}
//====================================
void Power_Relay_Control(char * typeMotor, long stepSpeed, long steps) {
  if (strcmp(typeMotor, "POWER") == 0 && toDo == true) {
    toDo = false;
    if (stepSpeed == 0) {
      digitalWrite(POWER_RELAY, LOW);
    }
    if (stepSpeed == 1) {
      digitalWrite(POWER_RELAY, HIGH);
    }
    Serial.print("<");
    Serial.print(typeMotor);
    Serial.print(",");
    Serial.print(stepSpeed);
    Serial.print(",");
    Serial.print(steps);
    Serial.println(">");
  }
}
//====================================

void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      } else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

//====================================

void parseData() { // split the data into its parts

  char * strtokIndx; // this is used by strtok() as an index

  strtokIndx = strtok(tempChars, ","); // get the first part - the string
  strcpy(selectionFromPC, strtokIndx); // copy it to selectionFromPC
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  inputOneFromPC = atol(strtokIndx); // convert this part to an long
  strtokIndx = strtok(NULL, ",");
  inputTwoFromPC = atol(strtokIndx); // convert this part to an long
}

//====================================

void showParsedData() {
  Serial.print("Selection ");
  Serial.println(selectionFromPC);
  Serial.print("Speed ");
  Serial.println(inputOneFromPC);
  Serial.print("Steps ");
  Serial.println(inputTwoFromPC);
}

void homeGantry(char* typeCommand){
  if (strcmp(typeCommand, "homeGantry") == 0 && toDo == true) {
    homingGantry();
    toDo = false;
    Serial.println("<homeGantry,0,0>");
  }
}
void homeDisp(char* typeCommand){
  if (strcmp(typeCommand, "homeDisp") == 0 && toDo == true) {
    //Serial.println("working");
    homingDisp();
    toDo = false;
    Serial.println("<homeDisp,0,0>");
  }
}

void homingGantry() {

  xSwitchState = 1;
  ySwitchState = 1;
  zSwitchState = 1;
  
  digitalWrite(X_DIR_PIN, HIGH);
  while (xSwitchState == 1) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(200);
    //Serial.print("X Switch: ");
    //Serial.println(xSwitchState);
    xSwitchState = digitalRead(X_SWITCH);
  }

  digitalWrite(X_DIR_PIN, LOW);
  for (int i = 0; i < 3000; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(200);
  }

  X_POS = 0;

  digitalWrite(Y_DIR_PIN, HIGH);
  while (ySwitchState == 1) {
    digitalWrite(Y_STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(Y_STEP_PIN, LOW);
    delayMicroseconds(200);
    //Serial.print("Y Switch: ");
    //Serial.println(ySwitchState);
    ySwitchState = digitalRead(Y_SWITCH);
  }

  digitalWrite(Y_DIR_PIN, LOW);
  for (int i = 0; i < 3000; i++) {
    digitalWrite(Y_STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(Y_STEP_PIN, LOW);
    delayMicroseconds(200);
  }

  Y_POS = 0;

  digitalWrite(Z_DIR_PIN, HIGH);
  while (zSwitchState == 1) {
    digitalWrite(Z_STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(Z_STEP_PIN, LOW);
    delayMicroseconds(200);
    //Serial.print("Z Switch: ");
    //Serial.println(zSwitchState);
    zSwitchState = digitalRead(Z_SWITCH);
  }

  digitalWrite(Z_DIR_PIN, LOW);
  for (int i = 0; i < 500; i++) {
    digitalWrite(Z_STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(Z_STEP_PIN, LOW);
    delayMicroseconds(200);
  }

  Z_POS = 0;
}

void homingDisp() {

  digitalWrite(Z_SUCK_ENABLE_PIN, LOW);
  digitalWrite(Z_AIRDRY_ENABLE_PIN, LOW);
  digitalWrite(Z_FLUSH_ENABLE_PIN, LOW);
  
  digitalWrite(Z_SUCK_DIR_PIN, HIGH);
  while (zSuckSwitchState == 1) {
    digitalWrite(Z_SUCK_STEP_PIN, HIGH);
    delayMicroseconds(50);
    digitalWrite(Z_SUCK_STEP_PIN, LOW);
    delayMicroseconds(50);
    //Serial.print("Z Suck Switch: ");
    //Serial.println(zSuckSwitchState);
    zSuckSwitchState = digitalRead(Z_SUCK_SWITCH);
  }

  digitalWrite(Z_SUCK_DIR_PIN, LOW);
  for (int i = 0; i < 10000; i++) {
    digitalWrite(Z_SUCK_STEP_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(Z_SUCK_STEP_PIN, LOW);
    delayMicroseconds(100);
  }

  Z_SUCK_POS = 0;
  digitalWrite(Z_SUCK_ENABLE_PIN, HIGH);

  digitalWrite(Z_FLUSH_DIR_PIN, HIGH);
  while (zFlushSwitchState == 1) {
    digitalWrite(Z_FLUSH_STEP_PIN, HIGH);
    delayMicroseconds(50);
    digitalWrite(Z_FLUSH_STEP_PIN, LOW);
    delayMicroseconds(50);
    //Serial.print("Z Flush Switch: ");
    //Serial.println(zFlushSwitchState);
    zFlushSwitchState = digitalRead(Z_FLUSH_SWITCH);
  }

  digitalWrite(Z_FLUSH_DIR_PIN, LOW);
  for (int i = 0; i < 18000; i++) {
    digitalWrite(Z_FLUSH_STEP_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(Z_FLUSH_STEP_PIN, LOW);
    delayMicroseconds(100);
  }

  Z_FLUSH_POS = 0;
  digitalWrite(Z_FLUSH_ENABLE_PIN, HIGH);

  digitalWrite(Z_AIRDRY_DIR_PIN, HIGH);
  while (zAirdrySwitchState == 1) {
    digitalWrite(Z_AIRDRY_STEP_PIN, HIGH);
    delayMicroseconds(50);
    digitalWrite(Z_AIRDRY_STEP_PIN, LOW);
    delayMicroseconds(50);
    //Serial.print("Z Airdry Switch: ");
    //Serial.println(zAirdrySwitchState);
    zAirdrySwitchState = digitalRead(Z_AIRDRY_SWITCH);
  }

  digitalWrite(Z_AIRDRY_DIR_PIN, LOW);
  for (int i = 0; i < 31000; i++) {
    digitalWrite(Z_AIRDRY_STEP_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(Z_AIRDRY_STEP_PIN, LOW);
    delayMicroseconds(100);
  }

  Z_AIRDRY_POS = 0;
  digitalWrite(Z_AIRDRY_ENABLE_PIN, HIGH);
}
