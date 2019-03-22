#include <Mouse.h>
#include <Keyboard.h>
void setup() {
  Mouse.begin();
  Keyboard.begin();
}
void loop() {
  // Wait for current chopping activity to stop.  (About 30 seconds.)
  delay(35000L);
  // Chopping leaves you looking forward.  Look down again.
  for (int i = 0; i < 8; i++) {
    Mouse.move(0, -40, 0);
    delay(10);
  }
  // Press E to start chopping again.
  Keyboard.press('e');
  delay(100);
  Keyboard.releaseAll();
}