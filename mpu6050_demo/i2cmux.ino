#include "i2cmux.h"

void TCA9548A(uint8_t bus){
  Wire.beginTransmission(0x77);  // TCA9548A address
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
//  Serial.print(bus);
}
