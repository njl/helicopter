#define LED 8

#define STATUS 13


byte sendPacket(byte cmds[]){
  static byte markL, countP, countR, one, zero;
  static bool data;
  static const byte maskB[] = {1,2,4,8,16,32,64,128};

  digitalWrite(STATUS,HIGH);

  markL = 77;
  countP = 4;
  countR = 8;
  
  one = 0;
  zero = 0;

  data = true;

  while(markL--){
    digitalWrite(LED,LOW);
    delayMicroseconds(10);
    digitalWrite(LED,HIGH);
    delayMicroseconds(10);
  }

  delayMicroseconds(1998);

  markL = 12;

  while(data){

    while(markL--){
      digitalWrite(LED,LOW);
      delayMicroseconds(10);
      digitalWrite(LED,HIGH);
      delayMicroseconds(10);
    }
    markL = 12;

    if(cmds[4-countP] & maskB[--countR]){
      one++;
      delayMicroseconds(688);
    }else{
      zero++;
      delayMicroseconds(288);
    }

    if(!countR){
      countR = 8;
      countP--;
    }

    if(!countP){
      data = false;
    }
  }

  while(markL--){
    digitalWrite(LED,LOW);
    delayMicroseconds(10);
    digitalWrite(LED,HIGH);
    delayMicroseconds(10);
  }

  digitalWrite(STATUS,LOW);

  return((.1-.014296-one*.000688-zero*.000288)*1000); // in ms.
}


byte cmds[] = {63, 63, 0, 63};
//yaw, pitch, throttle, trim

void setup(){
    Serial.begin(9600);
    pinMode(STATUS, OUTPUT);
    digitalWrite(STATUS, LOW);
    pinMode(LED, OUTPUT);
    digitalWrite(LED, HIGH);
}


void serialEvent(){
   if(Serial.available() != 4){
        return;
    }
    for(int i=0; i < 4; ++i){
        cmds[i] = Serial.read();
    }
}

void loop(){
    delay(sendPacket(cmds));
}
