# Start with Arduino IDE

These instructions target the initial **PY32F071** assembly. The board also supports F072, but this software release does not yet support that variant.

You will make MicroPetal's green LED blink. No breadboard or extra LED is needed.

**Status:** the sketch compiles with Arduino CLI using this hardware package, and the identical Blink binary was written and readback-verified on a real board through the factory USB-HID loader (macOS, 23 November 2026). Uploading with the Arduino IDE's own Upload button, and Windows/Linux hosts, have not yet been tried on hardware.

If using a repository checkout instead of the ZIP, open a terminal in its `software/` directory. All paths and commands below are relative to that directory.

## 1. Prepare the board (before USB)

Read [the power/jumper reference](SCHEMATIC-ANALYSIS.md#power-selection-and-jumpers). No JP3 change is required for Blink. Leave JP7 1–2 and JP4/JP5/JP6 open. Disconnect all power before changing jumpers.

Use a USB **data** cable, not a charge-only cable. Leave shields and the barrel supply disconnected. At first power-up check VCC matches the JP3 selection before continuing.

## 2. Install the software (once)

1. Install [Arduino IDE](https://www.arduino.cc/en/software/) and [Python 3](https://www.python.org/downloads/). On Windows enable the Python launcher when installing.
2. Extract the MicroPetal software ZIP. Keep this folder: it also holds the upload tool used by Arduino.
3. Open Arduino IDE → **Preferences** (Settings on some macOS versions) and copy **Sketchbook location**. Close Arduino IDE.
4. Open Terminal / PowerShell in the extracted MicroPetal software folder. Run the command below, replacing the quoted path with that sketchbook location:

macOS/Linux:

```sh
python3 tools/install.py --sketchbook "/your/Arduino/sketchbook"
```

Windows:

```powershell
py -3 tools/install.py --sketchbook "C:\Users\YourName\Documents\Arduino"
```

The script downloads the compiler and installs the HID uploader into a private virtual environment. It copies the board support to your sketchbook's `hardware/micropetal/py32` folder, and preserves any older install under `micropetal-backups`. It does not change your Arduino preferences or require administrator access. Allow several minutes for the first download. If Python/USB permissions fail, see troubleshooting below. Host installation was tested on Apple Silicon only; Windows/Linux need confirmation.

5. Reopen Arduino IDE. **Tools → Board → MicroPetal PY32F071 → MicroPetal Uno R1 (PY32F071, experimental)**. Do **not** select Arduino Uno.

There is no public Boards Manager URL yet. This is a local hardware-package installation; no “Burn Bootloader” step is required.

## 3. Open and check Blink

Choose **File → Examples → MicroPetal → Blink**, or open `examples/Blink/Blink.ino` from the extracted folder.

```cpp
void setup() { pinMode(LED_BUILTIN, OUTPUT); }
void loop() {
  digitalWrite(LED_BUILTIN, LED_ON);  delay(500);
  digitalWrite(LED_BUILTIN, LED_OFF); delay(500);
}
```

Click **Verify** (the check mark). It should compile. Unlike an Uno, this board's LED is active-low: `LED_ON` means LOW. The 22k LED resistor can make it faint.

## 4. Put the board in upload mode

1. Disconnect USB.
2. Fit a shunt between **J3 pins 3 and 4**: BOOT0 ↔ VCC. Identify pin numbers from the CAD/pin-1 marker, not by guessing orientation. Never short J3 5–6.
3. Connect USB. The ROM loader should enumerate as a USB HID device (normally VID:PID `ffff:0448`), not a serial COM port. If already powered, tap **RST** after fitting the shunt.
4. Click **Upload** (right arrow). The recipe calls `puyaisp -t hid -f ...bin`, which writes and verifies the sketch.
5. After success, disconnect USB, remove J3 3–4, then reconnect USB. The LED should blink twice per second (one full on/off cycle per second).

**Do not use SW1 BTN as BOOT; it is an ordinary D12 button. No serial port selection is needed for HID upload.** The ROM loader remains in the chip, so you can repeat these steps even after a bad sketch. The uploader command has worked on a board; the IDE Upload button with no port selected is still to be confirmed in the IDE itself (Arduino CLI accepts it).

## 5. Try the button and analog input

Open the included **Button** example: BTN lights the LED while held. Avoid it while SPI is in use because BTN shares MISO.

For **AnalogSerial**, connect a 10k potentiometer's ends to **3V3** and **GND**, wiper to **A0**. A 3.3 V USB-UART adapter is required to see messages:

| Adapter | MicroPetal |
|---|---|
| RX | D2 (TX) |
| TX (optional, for input) | D0 (RX) |
| GND | GND |
| VCC | Leave disconnected; power board from USB |

Open Serial Monitor on the **adapter's** port at 115200 baud. `Serial` is USART3 on D2/D0, **not native USB and not D1/D0**. Values are 0–1023 by default; `analogReadResolution(12)` selects 0–4095.

## Troubleshooting

- **Board absent from menu:** check Sketchbook location, restart IDE, and confirm `hardware/micropetal/py32/boards.txt` exists there.
- **Compiler/uploader missing:** rerun the installer from the final extracted folder; moving it afterward breaks the absolute tool path. It will preserve the previous board install.
- **No HID device:** check the data cable, J3 3–4, reset, selected VCC supply, and actual MCU marking. BTN does not enable ISP. Try unplug/replug with the BOOT shunt fitted.
- **Port menu empty:** normal for factory HID programming; only the optional UART adapter creates a serial port.
- **Upload denied on Linux:** install a narrow udev rule for USB `ffff:0448` / hidraw access using the distro's instructions, then replug. Avoid running the IDE as root. Windows may need the HID backend dependencies supplied by hidapi; do not replace the device driver with a serial driver.
- **LED reversed/faint:** active-low and 22k series resistor; use `LED_ON` / `LED_OFF`.
- **No serial text:** use D2 TX, not D1; correct adapter port, 115200 baud, common ground and 3.3 V logic.

See [pinout/API limits](PINOUT.md) before reusing an Uno shield or AVR-specific library.
