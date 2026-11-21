from os.path import join
from SCons.Script import Import
Import("env")
base=join(env.PioPlatform().get_dir(),"hardware","micropetal","py32")
core=join(base,"cores","micropetal")
variant=join(base,"variants","micropetal_uno")
env.Append(CCFLAGS=["-mcpu=cortex-m0plus","-mthumb","-Os","-g","-ffunction-sections","-fdata-sections"], CFLAGS=["-std=gnu11"], CXXFLAGS=["-std=gnu++17","-fno-exceptions","-fno-rtti","-fno-threadsafe-statics"], ASFLAGS=["-mcpu=cortex-m0plus","-mthumb"], CPPDEFINES=["PY32F071xB","USE_HAL_DRIVER",("F_CPU",8000000),("HSE_VALUE",8000000),("ARDUINO",10819),"ARDUINO_ARCH_PY32","ARDUINO_MICROPETAL_UNO_R1"], CPPPATH=[core,variant,join(core,"cmsis"),join(core,"device"),join(core,"hal")], LINKFLAGS=["-mcpu=cortex-m0plus","-mthumb","-nostartfiles","--specs=nano.specs","--specs=nosys.specs","-Wl,--gc-sections","-T"+join(variant,"linker.ld")], LIBS=["m","c","stdc++","supc++"], LIBSOURCE_DIRS=[join(base,"libraries")])
env.Append(LIBS=[env.BuildLibrary(join("$BUILD_DIR","micropetal"),core)])
