int VRx = A0;
int VRy = A1;
int SW = 2;

void setup() {
  Serial.begin(9600);
  pinMode(SW, INPUT_PULLUP);
}

void loop() {
  int x = analogRead(VRx);
  int y = analogRead(VRy);
  int button = digitalRead(SW);

  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.println(button);

  delay(10);
}
