# Start with PlatformIO in VS Code

These instructions target the initial **PY32F071** assembly. The board also supports F072, but this software release does not yet support that variant.

Goal: compile and upload the same blinking-LED program, with files organized as a small project.

**Status:** local platform and API smoke examples compile under PlatformIO. Hardware uploads remain untested.

If using a repository checkout instead of the ZIP, open a terminal in its `software/` directory. All paths and commands below are relative to that directory.

## 1. Board preparation

Follow [the power/jumper instructions](SCHEMATIC-ANALYSIS.md) **before power-on**: JP3 must select 3.3 V (open 1–2, close 2–3); JP7 remains 1–2. Leave JP4/JP5/JP6 open. Use USB only and no shield for first bring-up. Confirm VCC measures about 3.3 V.

## 2. Install tools

1. Install [VS Code](https://code.visualstudio.com/) and its **PlatformIO IDE** extension. Wait for its initialization to finish.
2. Install [Python 3](https://www.python.org/downloads/), then extract the software ZIP to a folder you intend to keep.
3. Open a terminal in that extracted folder and run:

```sh
python3 tools/install.py --no-arduino
```

On Windows use `py -3 tools/install.py --no-arduino`. This installs a pinned compiler and USB-HID uploader; it does not install an Arduino board package. If you already ran the Arduino installer you can skip this step.

4. In VS Code choose **File → Open Folder**, then select **examples/platformio** inside the extracted package. Trust the local project if prompted.

Do not use the New Project wizard's Arduino Uno board selection. MicroPetal uses a custom local platform included with the package.

## 3. Project files

`platformio.ini`:

```ini
[env:micropetal_uno]
platform = symlink://../../platform
board = micropetal_uno
framework = arduino
monitor_speed = 115200
```

The relative platform path assumes you open the included example in its original location. For your own project elsewhere, replace it with a path to the extracted `platform` folder, e.g. `platform = symlink:///absolute/path/MicroPetal/platform` (Windows: `symlink://C:/path/MicroPetal/platform`). Keep the package around: the local platform is not registered in PlatformIO's public registry.

`src/main.cpp`:

```cpp
#include <Arduino.h>
void setup() { pinMode(LED_BUILTIN, OUTPUT); }
void loop() {
  digitalWrite(LED_BUILTIN, LED_ON);  delay(500);
  digitalWrite(LED_BUILTIN, LED_OFF); delay(500);
}
```

Unlike `.ino` files, C++ files need `#include <Arduino.h>` and forward declarations if a function is called before it is defined. All ordinary `setup()` / `loop()` code is shared between the two environments.

## 4. Build, then upload

Click the **check-mark Build** icon in VS Code's PlatformIO toolbar. Look for **SUCCESS**. In a PlatformIO terminal you can instead run:

```sh
pio run
```

The binary is `.pio/build/micropetal_uno/program.bin`.

For upload:

1. Unplug USB; fit **J3 3–4** (BOOT0 ↔ VCC).
2. Connect USB using a data cable (or tap RST if already connected).
3. Click the **right-arrow Upload** icon, or run `pio run -t upload` in the PlatformIO terminal.
4. After write/verify succeeds, unplug, remove J3 3–4 and reconnect. Expect a dim green blinking LED.

USB programming uses the factory **HID** loader, not a serial port. No `upload_port` is required. SW1 BTN is D12, not BOOT. Do not use J3's other pairs as boot shunts.

If necessary the equivalent direct uploader command from the package root is:

```sh
tools/.venv/bin/puyaisp -t hid -f examples/platformio/.pio/build/micropetal_uno/program.bin
```

Windows: `tools\.venv\Scripts\puyaisp.exe -t hid -f examples\platformio\.pio\build\micropetal_uno\program.bin`.

## 5. More examples and Serial Monitor

Copy a sketch from `examples` into `src/main.cpp`, add `#include <Arduino.h>`, and build again. Keep only one `setup()` and `loop()` in the project. `tests/CompileSmoke/CompileSmoke.ino` is a **compile-only** integration check, not a first-run sketch for a populated board.

For serial messages, use an external **3.3 V USB-UART** adapter: adapter RX → D2, adapter TX → D0, GND → GND; leave adapter VCC disconnected. Set `monitor_port` to that adapter's port and keep `monitor_speed = 115200`. Click the plug/Monitor icon. No native USB serial device is implemented.

I2C uses the separate SDA/SCL pins, not A4/A5. SPI uses D10–D13; do not press BTN during SPI. [Pinout and limitations](PINOUT.md).

## If something fails

- **Unknown board/platform:** open the correct example folder and check the local `platform` path.
- **Uploader not found:** rerun `tools/install.py --no-arduino` from the final package location; it records the uploader path for PlatformIO.
- **No USB-HID device:** confirm JP3/voltage, a data cable, J3 3–4, reset and chip marking. Refer to the [Arduino troubleshooting section](ARDUINO-START.md#troubleshooting) for host permissions.
- **Serial monitor shows no device:** MicroPetal USB is not a CDC serial port. Use the external UART adapter.
- **Downloaded generic Puya platform instead:** keep the supplied `symlink://` platform setting; generic F030 support is not an F071 port.
