#include <SPI.h>
#include <Wire.h>

int input = 0;

// Push button pins
const int pin5 = 5; //short enabled
const int pin6 = 6; //e1 IDA4 W1
const int pin7 = 7; //e8 IDA3 W1
const int pin8 = 8; //e8 IDA2 W1
const int pin9 = 9; //e8 IDA1 W1
const int pin10 = 10; //e8 IDA1 W2
const int pin11 = 11; //e8 IDA2 W2
const int pin12 = 12; //e8 IDA3 W2
const int pin13 = 13; //e8 IDA4 W2


void setup() {
  Serial.begin(115200);
  Serial.setTimeout(1);
  pinMode(pin5, OUTPUT);
  pinMode(pin6, OUTPUT);
  pinMode(pin7, OUTPUT);
  pinMode(pin8, OUTPUT);
  pinMode(pin9, OUTPUT);
  pinMode(pin10, OUTPUT);
  pinMode(pin11, OUTPUT);
  pinMode(pin12, OUTPUT);
  pinMode(pin13, OUTPUT);
  digitalWrite(5, LOW);
  digitalWrite(6, LOW);
  digitalWrite(7, LOW);
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
  digitalWrite(11, LOW);
  digitalWrite(12, LOW);
  digitalWrite(13, LOW);
}

void writeIDA(int n) {

  if (n == 1) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(9, HIGH);
    digitalWrite(10, HIGH);
    Serial.println("Changed to IDA1");
  } else if (n == 2) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(8, HIGH);
    digitalWrite(11, HIGH);
    Serial.println("Changed to IDA2");
  } else if (n == 3) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(7, HIGH);
    digitalWrite(12, HIGH);
    Serial.println("Changed to IDA3");
  } else if (n == 4) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(6, HIGH);
    digitalWrite(13, HIGH);
    Serial.println("Changed to IDA4");
  } else if (n == 5) {
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
    digitalWrite(7, HIGH);
    digitalWrite(8, HIGH);
    digitalWrite(9, HIGH);
    digitalWrite(10, HIGH);
    digitalWrite(11, HIGH);
    digitalWrite(12, HIGH);
    digitalWrite(13, HIGH);
    Serial.println("All electrodes active");
  } else if (n == 11) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(6, HIGH);
    Serial.println("Changed to Electrode 1");
  } else if (n == 12) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(7, HIGH);
    Serial.println("Changed to Electrode 2");
  } else if (n == 13) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(8, HIGH);
    Serial.println("Changed to Electrode 3");
  } else if (n == 14) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(9, HIGH);
    Serial.println("Changed to Electrode 4");
  } else if (n == 15) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(10, HIGH);
    Serial.println("Changed to Electrode 5");
  } else if (n == 16) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(11, HIGH);
    Serial.println("Changed to Electrode 6");
  } else if (n == 17) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(12, HIGH);
    Serial.println("Changed to Electrode 7");
  } else if (n == 18) {
    digitalWrite(5, LOW);
    digitalWrite(6, LOW);
    digitalWrite(7, LOW);
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);
    digitalWrite(11, LOW);
    digitalWrite(12, LOW);
    digitalWrite(13, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(13, HIGH);
    Serial.println("Changed to Electrode 8");
  }
  
}

void loop()
{
  if (Serial.available() > 0) {
    input = Serial.readString().toInt();
    writeIDA(input);
  }
}
