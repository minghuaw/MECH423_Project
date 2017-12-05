#include <Servo.h>

#define SERVOUP 2
#define SERVOLEFT 3
#define SERVORIGHT 4
#define SERVO_WIPE_L 5
#define SERVO_WIPE_R 6
#define HIGHEND 2700
#define LOWEND 600
#define START_BYTE 0xff
#define RX_BUFFER_SIZE 7
#define UP 1
#define DOWN 0
#define DOWN_ANGLE 1420
#define UP_ANGLE 1520
#define WIPE_UP 2300

Servo myservo_l;
Servo myservo_r;
Servo myservo_u;
Servo wpservo_l;
Servo wpservo_r;

byte rx_buffer[RX_BUFFER_SIZE];
byte rx_byte;
unsigned int idx = 0;
unsigned int left_angle = 1600; // MIN 700, MID 1600, MAX 2500
unsigned int right_angle = 1500; // MIN 600, MID 1500, MAX 2400
unsigned int up_angle = UP_ANGLE;
unsigned int last_left = left_angle;
unsigned int last_right = right_angle;
unsigned int last_up = UP_ANGLE;
unsigned int lift = 1;
unsigned int up_scale = 20;
unsigned int park_l = 1720;
unsigned int park_r = 1380;
float up_step;
float left_step;
float right_step;
float step_num = 20;

const int wp_steps = 11;
//int wipe_l[24] = {2215,2069,1377,2069,1377,1118,1377,1118,1465,1118,1465,1084,1465,1084,961,1084,961,750,961,750,812,750,812,2215};
//int wipe_r[24] = {2057,1569,1847,1569,1847,1481,1847,1481,1134,1481,1134,963,1134,963,1120,963,1120,1040,1040,1040,610,1040,610,2057};
int wipe_l[wp_steps] = {2215,2069,1377,1133,1000,750, 730,1509,1776,801,2215};
int wipe_r[wp_steps] = {2057,1509,1847,1808,1351,1227,1008,1704,1700,620,2057};

void setup() {
  // put your setup code here, to run once:
  up_step = (UP_ANGLE - DOWN_ANGLE)/50;
  
  Serial.begin(9600);
  while(!Serial){
    ;
  }

  randomSeed(50);
  
  myservo_u.attach(SERVOUP, LOWEND, HIGHEND);
  myservo_l.attach(SERVOLEFT, LOWEND, HIGHEND);
  myservo_r.attach(SERVORIGHT, LOWEND, HIGHEND);
  wpservo_l.attach(SERVO_WIPE_L, LOWEND, HIGHEND);
  wpservo_r.attach(SERVO_WIPE_R, LOWEND, HIGHEND);

  wpservo_l.writeMicroseconds(wipe_l[0]);
  wpservo_r.writeMicroseconds(wipe_r[0]);
//  wpservo_l.writeMicroseconds(1000);
//  wpservo_r.writeMicroseconds(1351);
}

void loop() {
  myservo_u.writeMicroseconds(last_up);
  myservo_l.writeMicroseconds(last_left);
  myservo_r.writeMicroseconds(last_right);

  if(last_up < up_angle){
    last_up += up_step;
  }
  else{
    last_up -= up_step;  
  }

  if (lift == 0){
    up_angle = DOWN_ANGLE-up_scale;
  }
  else if (lift == 1){
    up_angle = UP_ANGLE;  
  }
  else if (lift == 2){
    myservo_u.writeMicroseconds(WIPE_UP);
    delay(500);
    myservo_l.writeMicroseconds(park_l);
    myservo_r.writeMicroseconds(park_r);

    int i=0;
    for (i=0; i<3; i++){
      wipe();
    }
    
    delay(500); // delay 1 sec to ensure 
    lift = 1;
    myservo_l.writeMicroseconds(last_left);
    myservo_r.writeMicroseconds(last_right);
  }
  
  if(last_left < left_angle){
    last_left += left_step;
  }
  else{
    last_left -= left_step;  
  }

  if(last_right < right_angle){
    last_right += right_step;
  }
  else{
    last_right -= right_step;  
  }

  delayMicroseconds(5000);
  
}

void serialEvent(){
  while(Serial.available()){
    rx_byte = Serial.read();

    // Checking for start byte
    if (rx_byte == START_BYTE){
      idx = 0;
    }

    rx_buffer[idx] = rx_byte;
    idx++;

    if(idx == RX_BUFFER_SIZE){
      idx = 0; // reset idx
      restoreData();
      left_angle = (unsigned int)((rx_buffer[1] << 8) | rx_buffer[2]);
      right_angle = (unsigned int)((rx_buffer[3] << 8) | rx_buffer[4]); 
      lift = (unsigned int)rx_buffer[5];
      up_scale = (unsigned int)(rx_buffer[6]); 

      if(left_angle>last_left)
        left_step = (left_angle-last_left)/step_num;
      else
        left_step = (last_left-left_angle)/step_num;

      if(right_angle>last_right)
        right_step = (right_angle-last_right)/step_num;
      else
        right_step = (last_right-right_angle)/step_num;
        
    }
  }
}

/**
 * Check the end byte that if the data bytes need to restored to 0xff
 */
void restoreData(){
  switch(rx_buffer[RX_BUFFER_SIZE-1]){
    case 0x00: {
      break;
    }
    case 0x01: {
      rx_buffer[RX_BUFFER_SIZE-4] = 0xff;
    }
    case 0x02: {
      rx_buffer[RX_BUFFER_SIZE-5] = 0xff;
    }
    case 0x10: {
      rx_buffer[RX_BUFFER_SIZE-6] = 0xff;
    }
    case 0x20: {
      rx_buffer[RX_BUFFER_SIZE-7] = 0xff;
    }
  } 
}

void wipe(){
  int i = 0;
  for (i=wp_steps-1; i>=0; i--){
    int wl = wipe_l[i];
    int wr = wipe_r[i];
    if (i !=0){
      wl += random(50, 300);
      wr += random(50, 300);
    }
    wpservo_l.writeMicroseconds(wl);
    wpservo_r.writeMicroseconds(wr);
    delay(500); // delay 1 seconds
  }
}
