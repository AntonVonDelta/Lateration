void setup() {
  Serial.begin(115200);
  pinMode(A1,INPUT);
  pinMode(A2,INPUT);
}

int start=0;
int count=0;

// the loop routine runs over and over again forever:
void loop() {
  while(true){ 
    // Great improvement by using port manipulation
    bool val1 = PINC & B00000010;   //digitalRead(A1);
    bool val2= PINC & B00000100; //digitalRead(A2);

    // Event timeout
    if(count>2000){
      Serial.println("Reset");
      count=0;
      start=0;
      return;
    }
    
    if(val1){
      if(start==0) {
        start=1;
      }
      else if(start==2){
        // Started by the other mic and ended by this one
        Serial.println("MIC2 MIC1");
        Serial.println(count);
        start=0;
        count=0;
      }
    }
    if(val2){
      if(start==0) {
        start=2;
      }
      else if(start==1){
        // Started by the other mic and ended by this one
        Serial.println("MIC1 MIC2");
        Serial.println(count);
        start=0;
        count=0;
      }
    }
  
    if(start!=0) count++;

  }
}
