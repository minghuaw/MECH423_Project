#include <Servo.h>

#define SERVOUP 2
#define SERVOLEFT 3
#define SERVORIGHT 4
#define HIGHEND 2700
#define LOWEND 600
#define START_BYTE 0xff
#define RX_BUFFER_SIZE 7
#define DOWN 1200
#define UP 1500

Servo myservo_l;
Servo myservo_r;
Servo myservo_u;

byte rx_buffer[RX_BUFFER_SIZE];
byte rx_byte;
unsigned int idx = 0;
unsigned int left_angle = 1600; // MIN 700, MID 1600, MAX 2500
unsigned int right_angle = 1500; // MIN 600, MID 1500, MAX 2700
unsigned int up_angle = UP;
unsigned int last_left = left_angle;
unsigned int last_right = right_angle;
unsigned int last_up = UP;
float up_step;
float left_step;
float right_step;
float step_num = 50;

void setup() {
  // put your setup code here, to run once:
  up_step = (UP - DOWN)/step_num;
  
  Serial.begin(9600);
  while(!Serial){
    ;
  }

  myservo_u.attach(SERVOUP, LOWEND, HIGHEND);
  myservo_l.attach(SERVOLEFT, LOWEND, HIGHEND);
  myservo_r.attach(SERVORIGHT, LOWEND, HIGHEND);
}

void loop() {
  myservo_u.writeMicroseconds(last_up);
  myservo_l.writeMicroseconds(last_left);
  myservo_r.writeMicroseconds(last_right);

  if(last_up < up_angle){
//    last_up += up_step;
      last_up++;
  }
  else{
//    last_up -= up_step;  
      last_up--;
  }
  
  if(last_left < left_angle){
//    last_left += left_step;
    last_left++;
  }
  else{
//    last_left -= left_step;  
    last_left--;
  }

  if(last_right < right_angle){
//    last_right += right_step;
    last_right++;
  }
  else{
//    last_right -= right_step;  
    last_right--;
  }

//  delayMicroseconds(10000);
  
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

      if(left_angle>last_left)
        left_step = (left_angle-last_left)/step_num;
      else
        left_step = (last_left-left_angle)/step_num;

      if(right_angle>last_right)
        right_step = (right_angle-last_right)/step_num;
      else
        right_step = (last_right-right_angle)/step_num;
        
      if (rx_buffer[5] == 0){
        up_angle = DOWN;
      }    
      else if (rx_buffer[5] == 1){
        up_angle = UP;  
      }
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
      rx_buffer[RX_BUFFER_SIZE-3] = 0xff;
    }
    case 0x02: {
      rx_buffer[RX_BUFFER_SIZE-4] = 0xff;
    }
    case 0x10: {
      rx_buffer[RX_BUFFER_SIZE-5] = 0xff;
    }
    case 0x20: {
      rx_buffer[RX_BUFFER_SIZE-6] = 0xff;
    }
  } 
}
