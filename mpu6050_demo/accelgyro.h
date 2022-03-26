#ifndef ACCELGYRO_H
#define ACCELGYRO_H

// I2Cdev and MPU6050 must be installed as libraries, or else the .cpp/.h files
// for both classes must be in the include path of your project
#include "I2Cdev.h"
#include "MPU6050.h"

int16_t ag[6];
uint8_t tmp1, tmp2;

void writeAccelGyroToBuf(MPU6050 accelgyro, uint8_t *buf, uint8_t bus, uint8_t offset);

#endif /*ACCELGYRO_H*/
