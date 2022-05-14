# Hardware: Adafruit Qt Py 2040
import adafruit_displayio_ssd1306
import displayio
from adafruit_display_text import label
import terminalio
import board
import busio
import adafruit_sdcard
import os
import storage
import audiopwmio
from audiomp3 import MP3Decoder
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

displayio.release_displays()

# Init display
WIDTH = 128
HEIGHT = 64
BORDER = 2
i2c = busio.I2C(board.GP17, board.GP16)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Make the display context
splash = displayio.Group()
display.show(splash)

# Draw black background
color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x0
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Label text
text1 = "Files on SD card: X"
text_area = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF, x=8, y=8)
splash.append(text_area)
text2 = "SSD1306"
text_area2 = label.Label(
    terminalio.FONT, text=text2, scale=2, color=0xFFFFFF, x=9, y=44
)
splash.append(text_area2)

# Init Sd card
spi = busio.SPI(board.GP14, board.GP15, board.GP12)
cs = DigitalInOut(board.GP13)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# List files on SD card
print("Files on SD card:")
numfiles = 0
for filename in os.listdir("/sd"):
    numfiles += 1
    print(filename)

text_area.text = f'Files on SD card: {numfiles}'

# Init LED out
led = DigitalInOut(board.GP18)
led.direction = Direction.OUTPUT
led.value = False
led2 = DigitalInOut(board.GP11)
led2.direction = Direction.OUTPUT
led2.value = False

# Init button in
button = DigitalInOut(board.GP19)
button.direction = Direction.INPUT
button.pull = Pull.UP

# Init audio file
mp3file = open("/PINBALL-sm.mp3", "rb")
decoder = MP3Decoder(mp3file)
audio = audiopwmio.PWMAudioOut(board.GP20)

debouncer = Debouncer(button)

# Main loop
while True:
    audio.play(decoder)
    while audio.playing:
        debouncer.update()
        if debouncer.fell:
            # Button is pressed
            led.value = True
            led2.value = not led2.value
        elif debouncer.rose:
            # Button is not pressed
            led.value = False