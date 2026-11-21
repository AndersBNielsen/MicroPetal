from os.path import join
import json, os
from SCons.Script import Default, DefaultEnvironment
env=DefaultEnvironment()
env.Replace(AR="arm-none-eabi-ar", AS="arm-none-eabi-as", CC="arm-none-eabi-gcc", CXX="arm-none-eabi-g++", OBJCOPY="arm-none-eabi-objcopy", RANLIB="arm-none-eabi-ranlib", SIZETOOL="arm-none-eabi-size", SIZEPROGREGEXP=r"^(?:\.text|\.rodata|\.data|\.isr_vector|\.ARM|\.preinit_array|\.init_array|\.fini_array|\.ARM.exidx)\s+(\d+).*", SIZEDATAREGEXP=r"^(?:\.data|\.bss)\s+(\d+).*", SIZECHECKCMD="$SIZETOOL -A -d $SOURCES", SIZEPRINTCMD="$SIZETOOL -B -d $SOURCES", PROGSUFFIX=".elf")
env.Append(BUILDERS={"ElfToBin":__import__('SCons.Builder',fromlist=['Builder']).Builder(action=env.VerboseAction("$OBJCOPY -O binary $SOURCES $TARGET","Building $TARGET"),suffix=".bin")})
program=env.BuildProgram()
env.Depends(program,join(env.PioPlatform().get_dir(),"hardware","micropetal","py32","variants","micropetal_uno","linker.ld"))
binary=env.ElfToBin(join("$BUILD_DIR","${PROGNAME}"),program)
env.Depends(binary,"checkprogsize")
Default(binary)
uploader="puyaisp"
config=join(env.PioPlatform().get_dir(),"upload-config.json")
if os.path.exists(config):
    with open(config) as f: uploader=json.load(f)["uploader"]
# SCons handles the executable token as a quoted argument on Windows and Unix.
env.Replace(UPLOADER=uploader)
upload=env.Alias("upload",binary,env.VerboseAction('"$UPLOADER" -t hid -f "$SOURCE"',"Uploading through Puya USB HID ROM ISP"))
env.AlwaysBuild(upload)
