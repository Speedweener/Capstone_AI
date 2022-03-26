
//#include "quaternion.h"
//#include "mpu6050_calibration.h"
//#include "i2cmux.h"
//#include <Arduino_FreeRTOS.h>
//#include <queue.h>
//
//unsigned long elapsedTime = 0;
//
//QueueHandle_t arrayQueue;
//
//void TaskSendBLE(void *pvParameters);
//void TaskReadI2C(void *pvParameters);
//
//uint8_t buf[8] = {0};
//
//void setup() {
//  Serial.begin(115200);  //initial the Serial
//  dmpDataReady();
//  setupQuat(6);
//  setupQuat(7);
//  arrayQueue  = xQueueCreate(30, //Queue length
//                        sizeof(uint8_t)*8);
//                        
//  if (arrayQueue!= NULL) {
//      Serial.println("success!");
////       Create task that consumes the queue if it was created.
//      xTaskCreate(TaskSendBLE,// Task function
//                  "SendBLE",// Task name
//                  128,// Stack size 
//                  NULL,
//                  1,// Priority
//                  NULL);
//    
//      // Create task that publish data in the queue if it was created.
//      xTaskCreate(TaskReadI2C, // Task function
//                  "ReadI2C",// Task name
//                  128,// Stack size 
//                  NULL,
//                  1,// Priority
//                  NULL);
//  }
////  vTaskStartScheduler();
//  
//  // setupCalibration();
//}
//
//// 100 Hz = 100 times / s
//// Period = 1/f = 1/100 = 10000 us
//
//
//void loop(){};
//
//void TaskSendBLE(void *pvParameters) {
//    
//    for (;;) {
////        if(xQueueReceive(arrayQueue,&buf,portMAX_DELAY) == pdPASS ){
//////          Serial.println(buf);
//////            Serial.write(buf, sizeof(buf));//send what has been received
////            vTaskDelay(100/portTICK_PERIOD_MS);
////        }
//        xQueueReceive(arrayQueue,&buf,portMAX_DELAY);
//        for (int i = 0; i < 8; i++) {
//          Serial.print(buf[i]);
//          Serial.print(", ");
//        }
//        Serial.println();
//    }
//}
//
//void TaskReadI2C(void *pvParameters) {
//    
//    for (;;) {
//      generateQuatSmaller(buf, 6, 0);
//      generateQuatSmaller(buf, 7, 1);
//      xQueueSend(arrayQueue, &buf, portMAX_DELAY);
//      vTaskDelay(500/portTICK_PERIOD_MS);
//    }
//}
//
