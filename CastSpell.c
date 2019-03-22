#include <Mouse.h>
void setup() {
  Mouse.begin();
}
void loop() {
  Mouse.press(MOUSE_LEFT);
  delay(700);
  Mouse.release(MOUSE_LEFT);
  delay(1500);
}