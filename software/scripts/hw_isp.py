#!/usr/bin/env python3
"""Bench helper for scripts/hw-test.sh: ROM HID wait, full-flash backup and restore.

Uses the puyaisp/hidapi modules installed by tools/install.py (run with tools/.venv python).
Never changes option bytes. Restore always readback-verifies and compares option bytes.
"""
import argparse, hashlib, json, sys, time
from pathlib import Path

VID, PID = 0xFFFF, 0x0448
FLASH_BASE, FLASH_SIZE = 0x08000000, 128 * 1024
CONFIG_OFFSET = 120 * 1024  # Firestarter reserved config: 0x0801E000..end (8 KiB)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def devices(serial=None):
    import hid
    found = hid.enumerate(VID, PID)
    if serial:
        found = [d for d in found if d.get('serial_number') == serial]
    return found


def cmd_wait(a):
    deadline = time.time() + a.timeout
    while time.time() < deadline:
        found = devices(a.serial)
        if len(found) == 1:
            d = found[0]
            print(f"ROM HID loader present: {VID:04x}:{PID:04x} serial={d.get('serial_number')} manufacturer={d.get('manufacturer_string')}")
            return 0
        if len(found) > 1:
            sys.exit('More than one ROM HID loader found; pass --serial')
        time.sleep(0.5)
    sys.exit(f'No ROM HID loader {VID:04x}:{PID:04x} within {a.timeout}s (J3 3-4 fitted? tap RST)')


def connect(serial):
    from puyaisp.puyaisp import HIDProgrammer
    found = devices(serial)
    if len(found) != 1:
        sys.exit(f'Expected exactly one ROM HID loader, found {len(found)}')
    isp = HIDProgrammer(VID, PID, found[0]['path'], 5000)
    isp.readinfo()
    isp.readoption()
    if not isp.chip_known or isp.chip_options['flash_size'] != FLASH_SIZE:
        isp.close()
        sys.exit('Unexpected chip/flash size; refusing')
    print(f"Connected: {isp.chip_options['name']} bootloader v{isp.verstr}; options {isp.optionstr}")
    return isp, found[0].get('serial_number')


def cmd_backup(a):
    out = Path(a.outdir)
    flash, opts, meta = out / 'backup-flash.bin', out / 'backup-options.bin', out / 'backup.json'
    if flash.exists():
        sys.exit(f'{flash} exists; refusing to overwrite a backup')
    out.mkdir(parents=True, exist_ok=True)
    isp, serial = connect(a.serial)
    try:
        options = bytes(isp.option)
        data = isp.readflash(FLASH_BASE, FLASH_SIZE)
        again = isp.readflash(FLASH_BASE, FLASH_SIZE)
        if data != again:
            sys.exit('Two full reads differ; backup not trusted')
        flash.write_bytes(data)
        opts.write_bytes(options)
        info = {'serial': serial, 'chip': isp.chip_options['name'], 'bootloader': isp.verstr,
                'flash_sha256': sha(data), 'options_hex': options.hex(),
                'config_region_blank': data[CONFIG_OFFSET:] == b'\xff' * (FLASH_SIZE - CONFIG_OFFSET),
                'time': time.strftime('%Y-%m-%dT%H:%M:%S%z')}
        meta.write_text(json.dumps(info, indent=2) + '\n')
        print(json.dumps(info))
    finally:
        isp.close()


def cmd_restore(a):
    out = Path(a.outdir)
    backup = (out / 'backup-flash.bin').read_bytes()
    options = (out / 'backup-options.bin').read_bytes()
    if len(backup) != FLASH_SIZE:
        sys.exit('Backup is not a full 128 KiB image')
    if a.image:
        image = Path(a.image).read_bytes()
        if len(image) >= CONFIG_OFFSET:
            sys.exit('Image overlaps the reserved config region')
        target = bytearray(b'\xff' * FLASH_SIZE)
        target[:len(image)] = image
        target[CONFIG_OFFSET:] = backup[CONFIG_OFFSET:]
        target = bytes(target)
        print(f'Restoring image {a.image} ({len(image)} B, sha256 {sha(image)}) + config region from backup')
        if backup[:len(image)] != image:
            print('NOTE: image differs from what was on the board at backup time')
    else:
        target = backup
        print(f'Restoring exact pre-test backup (sha256 {sha(backup)})')
    # Skip trailing 0xFF (already erased) to shorten the write; verify the whole flash afterwards.
    end = len(target.rstrip(b'\xff'))
    end += (-end) % 4
    isp, _ = connect(a.serial)
    try:
        if bytes(isp.option) != options:
            sys.exit('Option bytes differ from backup BEFORE restore; stopping for a human decision')
        isp.erase()
        isp.writeflash(FLASH_BASE, target[:end])
        isp.verifyflash(FLASH_BASE, target)
        isp.readoption()
        if bytes(isp.option) != options:
            sys.exit('Option bytes changed during restore')
        result = {'restored_sha256': sha(target), 'bytes_written': end, 'full_flash_verified': True,
                  'options_unchanged': True, 'matches_backup': target == backup}
        (out / 'restore.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result))
        isp.run()
    finally:
        isp.close()


def cmd_check_image(a):
    backup = (Path(a.outdir) / 'backup-flash.bin').read_bytes()
    image = Path(a.image).read_bytes()
    same = backup[:len(image)] == image and backup[len(image):CONFIG_OFFSET] == b'\xff' * (CONFIG_OFFSET - len(image))
    print('backup application region == image' if same else 'backup application region DIFFERS from image')
    return 0 if same else 3


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--serial', help='USB serial number of the ROM loader to use')
s = p.add_subparsers(dest='cmd', required=True)
w = s.add_parser('wait'); w.add_argument('--timeout', type=float, default=60); w.set_defaults(f=cmd_wait)
b = s.add_parser('backup'); b.add_argument('outdir'); b.set_defaults(f=cmd_backup)
r = s.add_parser('restore'); r.add_argument('outdir'); r.add_argument('--image'); r.set_defaults(f=cmd_restore)
c = s.add_parser('check-image'); c.add_argument('outdir'); c.add_argument('image'); c.set_defaults(f=cmd_check_image)
a = p.parse_args()
sys.exit(a.f(a) or 0)
