#include "accelgyro.h"

void writeAccelGyroToBuf(MPU6050 accelgyro, uint8_t *buf, uint8_t bus, uint8_t offset) {
    // read raw accel/gyro measurements from device
    TCA9548A(bus);
    accelgyro.getMotion6(&(ag[0]), &(ag[1]), &(ag[2]), &(ag[3]), &(ag[4]), &(ag[5]));
    
    for (int i = 0; i < 3; i++) {
        tmp1 = (uint8_t)(ag[i*2] >> 8);
        tmp2 = (uint8_t)(ag[i*2 + 1] >> 8);
        
        memcpy(buf + i * 2 + offset, (const char*)&tmp1, sizeof(uint8_t));
        memcpy(buf + i * 2 + 1 + offset, (const char*)&tmp2, sizeof(uint8_t));
    }
}
