from machine import Pin, I2C
import ssd1306

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

DEADZONE = 10
MAX_LEVEL = 5
_last = None


def level_from(value):
    """0 = står stille (-10..10), ellers 1-5 efter hvor langt ud værdien er."""
    a = abs(value)
    if a < DEADZONE:
        return 0
    return min(MAX_LEVEL, 1 + (a - DEADZONE) * MAX_LEVEL // 90)


def draw(level, value):
    oled.fill(0)
    oled.text("HASTIGHED", 28, 0)
    if level == 0:
        oled.text("STOP", 48, 14)
    else:
        oled.text("FREM" if value > 0 else "BAK", 48, 14)
    oled.text(str(level), 60, 26)
    box_w, gap = 20, 4
    x0 = (128 - (MAX_LEVEL * box_w + (MAX_LEVEL - 1) * gap)) // 2
    for i in range(MAX_LEVEL):
        x = x0 + i * (box_w + gap)
        if i < level:
            oled.fill_rect(x, 42, box_w, 20, 1)
        else:
            oled.rect(x, 42, box_w, 20, 1)
    oled.show()


def show(value):
    """Kald med y-værdien (-100..100). Tegner kun, når noget ændrer sig."""
    global _last
    level = level_from(value)
    state = (level, value > 0)
    if state == _last:
        return
    _last = state
    draw(level, value)


draw(0, 0)