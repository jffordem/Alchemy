#include <Mouse.h>
void setup() {
  delay(5000); // wait 5 seconds so that you can reprogram
  Mouse.begin();
}
void loop() {
  Mouse.press(MOUSE_LEFT);
  delay(700);
  Mouse.release(MOUSE_LEFT);
  delay(1500);
}