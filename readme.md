# Alchemy

This project is for experimenting on the Skyrim Alchemy generator, as well as considering other crafting systems.

I don't know what copyright applies to this file.

## Skyrim Alchemy

Turns out there's only one purpose for [making your own potions](https://en.uesp.net/wiki/Skyrim:Alchemy) in Skyrim.  To make money.  And the only way to do that is with the Hearthfire add-on, or Skyrim Special Edition.

Purchase the [Falkreath property](https://en.uesp.net/wiki/Skyrim:Lakeview_Manor) as quickly as possible, and then build a garden & greenhouse.  Plant [Creep Cluster](https://en.uesp.net/wiki/Skyrim:Creep_Cluster) (Special Edition has a bug where you can only harvest this from the standalone planters), [Mora Tapinella](https://en.uesp.net/wiki/Skyrim:Mora_Tapinella) and [Scaly Philiota](https://en.uesp.net/wiki/Skyrim:Scaly_Pholiota).

Every three in-game days (you can even sleep 24h x 3 to pass the time) harvest these crops and then create the potion.  It's the most valuable farmable potion in the game.  (All other potions you can buy or find.)

It's also important to work up your speech so that all vendors will purchase all items.  This allows you to pay for expensive armors, training, etc. with potions.  By the time you get all the Alchemy perks your potions should be worth around $3k each.

## Skyrim Grind

The early game grind in Skyrim can be avoided with a simple trick.  It's tedious, but chopping wood for the Bannered Mare in Whiterun, and selling it to Hulda, is a fast and safe way to get cash in the early game.  There's even a chopping block next to the door.  However, the chopping activity takes about 30 seconds of real-time and doing that for an hour is tedious.  You can use an inexpensive microcontroller - like an Arduino Leonardo - to automate this task.  Running it overnight will net you about $20k which is enough to hire a sellsword (like Jenassa, who is usually in The Drunken Huntsman) and get decent armor and weaponry.

This program works for me on a Leonardo, but you may need to tweak the timing and movement for your system.  Stand in front of the woodcutting block with your cursor on the block itself.  Press "E" to start chopping and immediately plug in the Leonardo.  Just unplug it to stop.

```C
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
```

## Skyrim Muffle

[Muffle](https://en.uesp.net/wiki/Skyrim:Muffle_(effect)) increases your Illusion XP by a crazy amount.  Casting Muffle a few hundres times is enough to roll Illusion up to 100.  Take your level-ups and use Legendary to set Illusion back to 15.  Repeat.  If you don't want to wear out your mouse, you can get an inexpensive microcontroller - like the Arduino Leonardo - that does HID inputs.  You can then program it to do all that tedious clicking for you.

Here is a program that you can load on a Leonardo to click.  Careful!  Once you've programmed your Leonardo, it will start clicking away as soon as you plug it in, which makes reprogramming it kind of a pain.  I found that about 700ms of mouse-down then 1500ms of mouse-up was about right.  Initially, you'll run out of magicka pretty quickly but that's okay.  Just let it run and check occasionally to see if you've maxed out.

Once you've programmed your Leonardo with this program, go somewhere safe and put the muffle spell in your right hand.  Plug the microcontroller in to start, and then unplug it to stop.

```C
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
```
