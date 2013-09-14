#! /usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import os
    import sys
    import shutil
    import functions
    import gtk
    import string
    import re
    from user import home
    from execcmd import ExecCmd
    from dialogs import QuestionDialog, MessageDialogSave
except Exception as detail:
    print(detail)
    exit(1)

TEXT_BLUE = '00BFFF'
TEXT_ORANGE = 'FF8000'

ec = ExecCmd()
scriptDir = os.path.dirname(os.path.realpath(__file__))
dist = functions.getDistroName()
luaDir = os.path.join(home, '.lua/scripts')
lua = os.path.join(luaDir, 'clock_rings.lua')
conkyrc = os.path.join(home, '.conkyrc')
conkyStart = os.path.join(home, '.conky-start')
autostartDir = os.path.join(home, '.config/autostart')
desktop = os.path.join(autostartDir, 'conky.desktop')
title = "SolydXK Conky"



if 'solydx' in dist.lower():
    qd = QuestionDialog(title, "Make sure compositing is enabled.\nGo to: Settings > Window Manager Tweaks > Tab: Compositor > check: Enable display compositing\n\nContinue installing SolydXK Conky?")
    answer = qd.show()
    if not answer:
        sys.exit(2)

qd = QuestionDialog(title, "Show temperatures in Celsius?\n\nSelect 'No' to show temperatures in Fahrenheit.")
answer = qd.show()
if not answer:
    tmpUnit = '°F'
    sensors = ec.run('sensors -f', False, False)
else:
    tmpUnit = '°C'
    sensors = ec.run('sensors', False, False)

functions.log('=============================================', True)
functions.log(title)
functions.log("Running distribution: %s" % dist)
functions.log("User home directory = %s" % home)
functions.log('=============================================')
functions.log(sensors)
functions.log('=============================================')

# =====================================================================
# Create files from templates if they do not exist for the current user
# =====================================================================
install = False
if os.path.exists(conkyrc):
    qd = QuestionDialog(title, "You already seem to have a Conky configuration file.\nBackup and continue?")
    answer = qd.show()
    if answer:
        install = True
else:
    install = True

if install:
    # conkyrc
    template = os.path.join(scriptDir, 'cfg/conkyrc')
    if os.path.exists(template):
        functions.log("Copy %s to %s" % (template, conkyrc))
        functions.backupFile(conkyrc)
        shutil.copy2(template, conkyrc)
        functions.chownCurUsr(conkyrc)
    else:
        functions.log("ERROR: Conkyrc not found: %s" % template)
        sys.exit(2)
    # lua
    template = os.path.join(scriptDir, 'cfg/clock_rings.lua')
    if os.path.exists(template):
        if not os.path.exists(luaDir):
            os.makedirs(luaDir)
        functions.log("Copy %s to %s" % (template, lua))
        functions.backupFile(lua)
        shutil.copy2(template, lua)
        functions.chownCurUsr(lua)
    else:
        functions.log("ERROR: Lua script not found: %s" % template)
        sys.exit(2)
    # Start script
    template = os.path.join(scriptDir, 'cfg/conky-start')
    if os.path.exists(template):
        functions.backupFile(conkyStart)
        functions.log("Copy %s to %s" % (template, conkyStart))
        shutil.copy2(template, conkyStart)
        functions.chownCurUsr(conkyStart)
        functions.makeExecutable(conkyStart)
    else:
        functions.log("ERROR: Conky-start not found: %s" % template)
        sys.exit(2)

# =====================================================================
# Check hardware and adapt configs accordingly
# =====================================================================
# Get bandwidth speed estimate
dload = 1024
qd = QuestionDialog(title, "Do you want to test your download speed?\n\nA 10MB file is going to be downloaded.\nDefault is set to 1MB.")
answer = qd.show()
if answer:
    functions.repaintGui()
    dload = int(functions.getBandwidthSpeed())
    if dload <= 1024:
        dload = 1024
        functions.log("Default speed selected: %d" % dload)
    else:
        dload *= 5
    #uload = int(dload / 10)
functions.replaceStringInFile('\[DSPEED\]', str(dload), lua)
functions.replaceStringInFile('\[USPEED\]', str(dload), lua)


# Network interface
functions.log('=============================================')
eth = functions.getNetworkInterface()
functions.log('=============================================')
if eth is None:
    eth = 'eth0'
functions.replaceStringInFile('\[ETH\]', eth, conkyrc)
functions.replaceStringInFile('\[ETH\]', eth, lua)

# Battery / Swap
bat = ec.run('acpi', True, False)
if bat.lower().find('battery') >= 0:
    functions.log("Battery detected: replace Swap with Battery index")
    functions.replaceStringInFile('\$\{swapperc\}', '${battery_percent BAT1}', conkyrc)
    functions.replaceStringInFile('\}Swap', '}BAT', conkyrc)
    functions.replaceStringInFile("'swapperc'", "'battery_percent'", lua)

# Core temperature
coreList = []
coreLine = "${color 00BFFF}[CORESTR]${alignr}${color FFFFFF}${execi 30 sensors | sed -n 's/[CORESTR][ ]*//p' | cut -d' ' -f1}"
sensorsList = sensors.splitlines(True)
for line in sensorsList:
    reObj = re.search('core\s{0,}\d.*\:', line, re.I)
    if reObj:
        newLine = string.replace(coreLine, '[CORESTR]', reObj.group(0))
        if 'F' in tmpUnit:
            newLine = string.replace(newLine, 'sensors', 'sensors -f')
        functions.log("Core string found: %s" % reObj.group(0))
        coreList.append(newLine)

if coreList:
    functions.log("Add Core lines to .conkyrc")
    functions.replaceStringInFile('#\s\[CORE\]', '\n'.join(coreList), conkyrc)

# CPU fan speed
cpufan = functions.findRegExpInString('cpu\s{0,}fan.*\:', sensors)
functions.log("Cpufan value = %s" % cpufan)
if cpufan:
    cpuLine = '${color 00BFFF}CPU fan:${alignr}${color FFFFFF}${execi 30 sensors | grep "[CPUSTRING]"|cut -d":" -f2|sed "s/ //g"|sed "s/+//g" | cut -d"R" -f1} RPM'
    functions.log("Write CPU fan speed: %s" % cpufan)
    newLine = string.replace(cpuLine, '[CPUSTRING]', cpufan)
    functions.replaceStringInFile('#\s\[CPUFAN\]', newLine, conkyrc)

# Chassis fan speed
chafan = functions.findRegExpInString('chassis\s{0,}fan.*\:', sensors)
functions.log("Chafan value = %s" % chafan)
if chafan:
    chaLine = '${color 00BFFF}Chassis fan:${alignr}${color FFFFFF}${execi 30 sensors | grep "[CHASTRING]"|cut -d":" -f2|sed "s/ //g"|sed "s/+//g" | cut -d"R" -f1} RPM'
    functions.log("Write chassis fan speed: %s" % chafan)
    newLine = string.replace(chaLine, '[CHASTRING]', chafan)
    functions.replaceStringInFile('#\s\[CHAFAN\]', newLine, conkyrc)

# HD temperature unit
hddTempLine = '${color 00BFFF}HD Temp (sda):${alignr}${color FFFFFF} ${execi 600 /usr/sbin/hddtemp -n /dev/sda}[TMPUNIT]'
functions.log("Tmpunit = %s" % tmpUnit)
newLine = string.replace(hddTempLine, '[TMPUNIT]', tmpUnit)
if 'F' in tmpUnit:
    newLine = string.replace(newLine, 'hddtemp', 'hddtemp -u f')
functions.replaceStringInFile('#\s\[HDDTEMP\]', newLine, conkyrc)

# =====================================================================
# Change color scheme accordingly
# =====================================================================
if 'solydx' in dist.lower():
    functions.log("Create orange theme for SolydX")
    functions.replaceStringInFile(TEXT_BLUE, TEXT_ORANGE, conkyrc)
    functions.replaceStringInFile(TEXT_BLUE, TEXT_ORANGE, lua)

# =====================================================================
# Automatically start Conky when the user logs in
# =====================================================================
if not os.path.exists(desktop):
    functions.log("Write autostart file: %s" % desktop)
    if not os.path.exists(autostartDir):
        os.makedirs(autostartDir)
    desktopCont = '[Desktop Entry]\nComment=SolydXK Conky\nExec=[CONKYSTART]\nIcon=conky\nStartupNotify=true\nTerminal=false\nType=Application\nName=SolydXK Conky\nGenericName=SolydXK Conky'
    f = open(desktop, 'w')
    f.write(string.replace(desktopCont, '[CONKYSTART]', conkyStart))
    f.close()
    functions.makeExecutable(desktop)

# =====================================================================
# Finish up
# =====================================================================
msg = "SolydXK Conky configuration has finished."
functions.log(msg)
log = os.path.join(home, '.conky-log')
if os.path.exists(log) and os.path.exists('/usr/bin/xdg-open'):
    qd = QuestionDialog(title, "%s.\n\nWould you like to see the log file?" % msg)
    answer = qd.show()
    if answer:
        os.system("/usr/bin/xdg-open %s" % log)
else:
    MessageDialogSave(title, msg, gtk.MESSAGE_INFO).show()

# Restart Conky
os.system('killall conky')
os.system('sleep 5 && conky &')
