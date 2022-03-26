#include "quaternion.h"

void dmpDataReady() {
    mpuInterrupt = true;
}


// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setupQuat(uint8_t bus) {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
        Wire.setClock(400000); // 400kHz I2C clock. Comment this line if having compilation difficulties
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif
    TCA9548A(bus);

    // initialize serial communication
    // (115200 chosen because it is required for Teapot Demo output, but it's
    // really up to you depending on your project)
    while (!Serial); // wait for Leonardo enumeration, others continue immediately

    // NOTE: 8MHz or slower host processors, like the Teensy @ 3.3V or Arduino
    // Pro Mini running at 3.3V, cannot handle this baud rate reliably due to
    // the baud timing being too misaligned with processor ticks. You must use
    // 38400 or slower in these cases, or use some kind of external separate
    // crystal solution for the UART timer.

    // initialize device
    Serial.println(F("Initializing I2C devices..."));
    mpu.initialize();
    pinMode(INTERRUPT_PIN, INPUT);

    // verify connection
    Serial.println(F("Testing device connections..."));
    Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

    // load and configure the DMP
    Serial.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize();

    //    // supply your own gyro offsets here, scaled for min sensitivity
    //    mpu.setXGyroOffset(220);
    //    mpu.setYGyroOffset(76);
    //    mpu.setZGyroOffset(-85);
    //    mpu.setZAccelOffset(1788); // 1688 factory default for my test chip

    // make sure it worked (returns 0 if so)
    if (devStatus == 0) {
        // Calibration Time: generate offsets and calibrate our MPU6050
        //        mpu.CalibrateAccel(6);
        //        mpu.CalibrateGyro(6);
        //        mpu.PrintActiveOffsets();
        // turn on the DMP, now that it's ready
        Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

        // enable Arduino interrupt detection
        Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
        Serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
        Serial.println(F(")..."));
        attachInterrupt(digitalPinToInterrupt(INTERRUPT_PIN), dmpDataReady, RISING);
        mpuIntStatus = mpu.getIntStatus();

        // set our DMP Ready flag so the main loop() function knows it's okay to use it
        Serial.println(F("DMP ready! Waiting for first interrupt..."));
        dmpReady = true;

        // get expected DMP packet size for later comparison
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {
        // ERROR!
        // 1 = initial memory load failed
        // 2 = DMP configuration updates failed
        // (if it's going to break, usually the code will be 1)
        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }

    // configure LED for output
    pinMode(LED_PIN, OUTPUT);
}

size_t generateQuatSmall(MPU6050 mpu, uint8_t* buf, uint8_t bus, uint8_t offset){
    int q_raw[4];
    // if programming failed, don't try to do anything
    if (!dmpReady) return;
    // read a packet from FIFO
    TCA9548A(bus);
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 
        union QdataS qq[4];

        // display quaternion values in easy matrix form: w x y z
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        q_raw[0] = q.w * 10000; 
        q_raw[1] = q.x * 10000;
        q_raw[2] = q.y * 10000;
        q_raw[3] = q.z * 10000;
//        q_raw[0] = 10; 
//        q_raw[1] = 20;
//        q_raw[2] = 30;
//        q_raw[3] = 40;

        for (int i = 0; i < 4; i++) {
//            printf("%d\n", i);
            
            memcpy(buf + 2*i + offset*8, (const char*)&(q_raw[i]), 2*sizeof(uint8_t));
    
        }
        return sizeof(buf);
    }
}

size_t writeQuatToBuf(uint8_t* buf, uint8_t bus, uint8_t offset){
    uint8_t q_raw[4];
    // if programming failed, don't try to do anything
    if (!dmpReady) return;
    // read a packet from FIFO
    TCA9548A(bus);
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 
        // display quaternion values in easy matrix form: w x y z
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        q_raw[0] = q.w * 100; 
        q_raw[1] = q.x * 100;
        q_raw[2] = q.y * 100;
        q_raw[3] = q.z * 100;
//        Serial.println();
//        Serial.println(bus);
//        Serial.print(q_raw[0]);
//        Serial.print(", ");
//        Serial.print(q_raw[1]);
//        Serial.print(", ");
//        Serial.print(q_raw[2]);
//        Serial.print(", ");
//        Serial.print(q_raw[3]);
//        Serial.print(", ");
//        Serial.println();

        for (int i = 0; i < 4; i++) {
//            printf("%d\n", i);
            
            memcpy(buf + i + offset, (const char*)&(q_raw[i]), sizeof(uint8_t));
    
        }
        return sizeof(buf);
    }
}

size_t generateQuat(uint8_t* buf){
    float q_raw[4];
    // if programming failed, don't try to do anything
    if (!dmpReady) return;
    // read a packet from FIFO
    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 
        union Qdata qq[4];

        
        // display quaternion values in easy matrix form: w x y z
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        q_raw[0] = q.w; 
        q_raw[1] = q.x;
        q_raw[2] = q.y;
        q_raw[3] = q.z;

        for (int i = 0; i < 4; i++) {
            qq[i].f = q_raw[i];
            const uint8_t *src = qq[i].u; 
            memcpy(buf+i*4, src, 4);
        }

        return Serial.write(buf, sizeof(buf));
        
//         Serial.print("quat\t");
//         Serial.print(q.w);
//         Serial.print("\t");
//         Serial.print(q.x);
//         Serial.print("\t");
//         Serial.print(q.y);
//         Serial.print("\t");
//         Serial.println(q.z);
    }
}
