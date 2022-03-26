#include "quaternion.h"
#include "accelgyro.h"
#include "mpu6050_calibration.h"
#include "i2cmux.h"
#include "MPU6050.h"

unsigned long elapsedTime = 0;
uint8_t buf[21] = {0};

uint8_t sequenceNumber = 1;

int8_t sig_int = 0;

bool button_start = false;

void setup()
{
  Serial.begin(115200); //initial the Serial
  pinMode(5, INPUT);
  dmpDataReady();
  setupQuat(6);
  setupQuat(7);
//    setupCalibration(6);
//    setupCalibration(7);
}

void writeQuat()
{
  writeQuatToBuf(buf, 6, 0);
  writeQuatToBuf(buf, 7, 4);
  Serial.write(buf, 8);
  while (millis() - elapsedTime < 50)
    ;
  elapsedTime = millis();
}


long startTime;
bool buttonState = false;

int countPerIter = 0;

bool debounce(uint8_t *count)
{
  if (digitalRead(5) == LOW && !buttonState)
  {
    // If someone presses the button for the first time
    startTime = millis();
    buttonState = true;
//    while (millis() - startTime < 10);
    return false;
  }
  
  else if (buttonState && countPerIter < 100)
  {
    countPerIter++;

    return true;
  }

  else if (buttonState && countPerIter >= 100)
  {
    // If someone lets go of button
    buttonState = false;
    (*count)++;
    countPerIter = 0;
    return false;
  } 
  
  else return false; 
}
long lastDebounceTime = 0;
long debounceDelay = 50;
bool debounce_start() {

 
  if (digitalRead(5) == LOW)
  {
    // If someone presses the button for the first time
    
    button_start = !button_start;

    delay(500);
  }
  return button_start;
  
  
}


 
void writeAll()
{
//  buf[0] = sequenceNumber;
  writeAccelGyroToBuf(mpu, buf, 6, 0);



  for (int i = 0; i < 3; i++)
  {
    sig_int = buf[i];
    Serial.print(sig_int);
    Serial.print(", ");
  }
  Serial.println();

  while (millis() - elapsedTime < 10);
  elapsedTime = millis();
}

void loop()
{
  
    writeAll();
}
