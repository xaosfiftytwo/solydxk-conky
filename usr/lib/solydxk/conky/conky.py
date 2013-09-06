#! /usr/bin/env python3

# sudo apt-get install python3-gi
# from gi.repository import Gtk, GdkPixbuf, GObject, Pango, Gdk
from gi.repository import Gtk, Gdk
import os
import functions
import gettext
import webbrowser
import shutil
import re
from os.path import abspath, dirname, join, expanduser, exists
from time import sleep
from config import Config
from logger import Logger
from execcmd import ExecCmd
from dialogs import MessageDialogSave

TEXT_BLUE = '00BFFF'
TEXT_ORANGE = 'FF8000'

# i18n: http://docs.python.org/2/library/gettext.html
gettext.install("solydxk-conky", "/usr/share/locale")
#t = gettext.translation("solydxk-conky", "/usr/share/locale")
#_ = t.lgettext

menuItems = ['preferences', 'network', 'system']


#class for the main window
class Conky(object):

    def __init__(self):
        self.scriptDir = abspath(dirname(__file__))

        # Load window and widgets
        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(self.scriptDir, '../../../share/solydxk/conky/conky.glade'))

        go = self.builder.get_object
        self.window = go('conkyWindow')
        self.ebTitle = go('ebTitle')
        self.lblTitle = go('lblTitle')
        self.lblMenuTitle = go('lblMenuTitle')
        self.statusbar = go('statusbar')
        self.ebMenu = go('ebMenu')
        self.ebMenuPreferences = go('ebMenuPreferences')
        self.lblMenuPreferences = go('lblMenuPreferences')
        self.ebMenuNetwork = go('ebMenuNetwork')
        self.lblMenuNetwork = go('lblMenuNetwork')
        self.ebMenuSystem = go('ebMenuSystem')
        self.lblMenuSystem = go('lblMenuSystem')
        self.nbConky = go('nbConky')
        self.btnSave = go('btnSave')

        # Preferences objects
        self.lblPrefAction = go('lblPrefAction')
        self.cmbPrefAction = go('cmbPrefAction')
        self.lsAction = go('lsAction')
        self.btnPrefActionApply = go('btnPrefActionApply')
        self.lblPrefAutostart = go('lblPrefAutostart')
        self.chkPrefAutostart = go('chkPrefAutostart')
        self.lblPrefAutostartText = go('lblPrefAutostartText')
        self.lblPrefSleep = go('lblPrefSleep')
        self.cmbPrefSleep = go('cmbPrefSleep')
        self.lsSleep = go('lsSleep')
        self.lblPrefSleepText = go('lblPrefSleepText')
        self.lblPrefAlign = go('lblPrefAlign')
        self.cmbPrefAlign = go('cmbPrefAlign')
        self.lsAlign = go('lsAlign')
        self.lblPrefAlignText = go('lblPrefAlignText')

        # Network objects
        self.lblNetwInterface = go('lblNetwInterface')
        self.txtNetwInterface = go('txtNetwInterface')
        self.lblNetwInterfaceText = go('lblNetwInterfaceText')
        self.lblNetwDownSpeed = go('lblNetwDownSpeed')
        self.txtNetwDownSpeed = go('txtNetwDownSpeed')
        self.lblNetwSpeedText = go('lblNetwSpeedText')
        self.lblNetwUpSpeed = go('lblNetwUpSpeed')
        self.txtNetwUpSpeed = go('txtNetwUpSpeed')
        self.btnNetspeed = go('btnNetspeed')
        self.lblNetwLanIP = go('lblNetwLanIP')
        self.chkNetwLanIP = go('chkNetwLanIP')
        self.lblNetwLanIPText = go('lblNetwLanIPText')
        self.lblNetwIP = go('lblNetwIP')
        self.chkNetwIP = go('chkNetwIP')

        # System objects
        self.lblSysCoresTemp = go('lblSysCoresTemp')
        self.chkSysCores = go('chkSysCores')
        self.lblSysCoresTempText = go('lblSysCoresTempText')
        self.lblSysHdTemp = go('lblSysHdTemp')
        self.chkSysHd = go('chkSysHd')
        self.lblSysTempUnit = go('lblSysTempUnit')
        self.cmbSysTempUnit = go('cmbSysTempUnit')
        self.lsTemp = go('lsTemp')
        self.lblSysCpuFan = go('lblSysCpuFan')
        self.chkSysCpuFan = go('chkSysCpuFan')
        self.lblSysChassisFan = go('lblSysChassisFan')
        self.chkSysChassisFan = go('chkSysChassisFan')
        self.lblSysBattery = go('lblSysBattery')
        self.rbtSysBattery = go('rbtSysBattery')
        self.lblSysSwap = go('lblSysSwap')
        self.rbtSysSwap = go('rbtSysSwap')
        self.lblSysKernel = go('lblSysKernel')
        self.chkSysKernel = go('chkSysKernel')
        self.lblSysUP = go('lblSysUP')
        self.chkSysUP = go('chkSysUP')

        # Read from config file
        self.cfg = Config(join(self.scriptDir, 'conky.conf'))
        self.clrTitleFg = Gdk.color_parse(self.cfg.getValue('COLORS', 'title_fg'))
        self.clrTitleBg = Gdk.color_parse(self.cfg.getValue('COLORS', 'title_bg'))
        self.clrMenuSelect = Gdk.color_parse(self.cfg.getValue('COLORS', 'menu_select'))
        self.clrMenuHover = Gdk.color_parse(self.cfg.getValue('COLORS', 'menu_hover'))
        self.clrMenuBg = Gdk.color_parse(self.cfg.getValue('COLORS', 'menu_bg'))

        # Set background and forground colors
        self.ebTitle.modify_bg(Gtk.StateType.NORMAL, self.clrTitleBg)
        self.lblTitle.modify_fg(Gtk.StateType.NORMAL, self.clrTitleFg)
        self.lblMenuPreferences.modify_fg(Gtk.StateType.NORMAL, self.clrTitleBg)
        self.lblMenuNetwork.modify_fg(Gtk.StateType.NORMAL, self.clrTitleBg)
        self.lblMenuSystem.modify_fg(Gtk.StateType.NORMAL, self.clrTitleBg)
        self.lblMenuTitle.modify_fg(Gtk.StateType.NORMAL, self.clrTitleBg)
        self.ebMenu.modify_bg(Gtk.StateType.NORMAL, self.clrMenuBg)
        self.ebMenuPreferences.modify_bg(Gtk.StateType.NORMAL, self.clrMenuBg)
        self.ebMenuNetwork.modify_bg(Gtk.StateType.NORMAL, self.clrMenuBg)
        self.ebMenuSystem.modify_bg(Gtk.StateType.NORMAL, self.clrMenuBg)

        # Translations
        self.window.set_title(_("SolydXK Conky"))
        self.lblTitle.set_text(self.window.get_title())
        self.lblMenuPreferences.set_text(_("Preferences"))
        self.lblMenuNetwork.set_text(_("Network"))
        self.lblMenuSystem.set_text(_("System"))
        self.btnSave.set_label(_("Save"))
        self.lblPrefAction.set_text(_("Action"))
        self.btnPrefActionApply.set_label(_("Apply"))
        self.lblPrefAutostart.set_text(_("Autostart"))
        self.lblPrefAutostartText.set_text(_("Autostart Conky on login."))
        self.lblPrefSleep.set_text(_("Sleep"))
        self.lblPrefSleepText.set_text(_("Seconds to wait before starting Conky.\nDefault is 20 seconds."))
        self.lblPrefAlign.set_text(_("Align"))
        self.lblPrefAlignText.set_text(_("Conky alignment on the desktop."))
        self.lblNetwInterface.set_text(_("Interface"))
        self.lblNetwInterfaceText.set_text(_("Auto detected (use ifconfig)."))
        self.lblNetwDownSpeed.set_text(_("Download speed"))
        self.lblNetwSpeedText.set_text(_("Test your download and upload speed\nwith speed.net (in Kilobytes)."))
        self.lblNetwUpSpeed.set_text(_("Upload speed"))
        self.btnNetspeed.set_label(_("speedtest.net"))
        self.lblNetwLanIP.set_text(_("LAN IP"))
        self.lblNetwLanIPText.set_text(_("Check to show these items."))
        self.lblNetwIP.set_text(_("IP"))
        self.lblSysCoresTemp.set_text(_("Core temperature"))
        self.lblSysCoresTempText.set_text(_("Check to show these items."))
        self.lblSysHdTemp.set_text(_("HD temperature"))
        self.lblSysTempUnit.set_text(_("Temperature unit"))
        self.lblSysCpuFan.set_text(_("CPU fan speed"))
        self.lblSysChassisFan.set_text(_("Chassis fan speed"))
        self.lblSysBattery.set_text(_("Battery"))
        self.lblSysSwap.set_text(_("Swap"))
        self.lblSysKernel.set_text(_("Kernel"))
        self.lblSysUP.set_text(_("Update Pack"))

        # Fill combos
        actions = [[_("Start")], [_("Stop")], [_("Remove")]]
        for a in actions:
            self.lsAction.append(a)

        self.sleep = [[0], [10], [20], [30], [40], [50], [60]]
        for s in self.sleep:
            self.lsSleep.append(s)

        align = [[_("Right")], [_("Left")]]
        for a in align:
            self.lsAlign.append(a)

        temperature = [[_("Celsius")], [_("Fahrenheit")]]
        for t in temperature:
            self.lsTemp.append(t)

        # Initialize logging
        self.log = Logger('', 'debug', True, self.statusbar)

        # Get command lines
        self.commandCore = self.cfg.getValue('COMMANDS', 'core')
        self.commandCpu = self.cfg.getValue('COMMANDS', 'cpu')
        self.commandChassis = self.cfg.getValue('COMMANDS', 'chassis')
        self.commandHdd = self.cfg.getValue('COMMANDS', 'hdd')
        self.commandLanIp = self.cfg.getValue('COMMANDS', 'lanip')
        self.commandIp = self.cfg.getValue('COMMANDS', 'ip')
        self.commandKernel = self.cfg.getValue('COMMANDS', 'kernel')
        self.commandUp = self.cfg.getValue('COMMANDS', 'up')

        # Init variables
        self.ec = ExecCmd(self.log)
        self.selectedMenuItem = None
        self.defaultSpeed = '1000'
        self.home = expanduser("~/")
        self.dist = functions.getDistribution(False)
        self.luaDir = join(self.home, '.lua/scripts')
        self.lua = join(self.luaDir, 'clock_rings.lua')
        self.conkyrc = join(self.home, '.conkyrc')
        self.conkyStart = join(self.home, '.conky-start')
        self.autostartDir = join(self.home, '.config/autostart')
        self.desktop = join(self.autostartDir, 'conky.desktop')

        # Get current settings
        self.getSettings()

        # Show version number in status bar
        self.version = functions.getPackageVersion('solydxk-conky')
        functions.pushMessage(self.statusbar, self.version)

        # Show preferences at startup
        self.on_ebMenuPreferences_button_release_event()

        self.builder.connect_signals(self)
        self.window.show()

    # ===============================================
    # Menu section functions
    # ===============================================

    def on_ebMenuPreferences_enter_notify_event(self, widget, event):
        self.changeMenuBackground(menuItems[0])

    def on_ebMenuNetwork_enter_notify_event(self, widget, event):
        self.changeMenuBackground(menuItems[1])

    def on_ebMenuSystem_enter_notify_event(self, widget, event):
        self.changeMenuBackground(menuItems[2])

    def on_ebMenuPreferences_leave_notify_event(self, widget, event):
        self.changeMenuBackground(self.selectedMenuItem)

    def on_ebMenuNetwork_leave_notify_event(self, widget, event):
        self.changeMenuBackground(self.selectedMenuItem)

    def on_ebMenuSystem_leave_notify_event(self, widget, event):
        self.changeMenuBackground(self.selectedMenuItem)

    def changeMenuBackground(self, menuItem, select=False):
        ebs = []
        ebs.append([menuItems[0], self.ebMenuPreferences])
        ebs.append([menuItems[1], self.ebMenuNetwork])
        ebs.append([menuItems[2], self.ebMenuSystem])
        for eb in ebs:
            if eb[0] == menuItem:
                if select:
                    self.selectedMenuItem = menuItem
                    eb[1].modify_bg(Gtk.StateType.NORMAL, self.clrMenuSelect)
                else:
                    if eb[0] != self.selectedMenuItem:
                        eb[1].modify_bg(Gtk.StateType.NORMAL, self.clrMenuHover)
            else:
                if eb[0] != self.selectedMenuItem or select:
                    eb[1].modify_bg(Gtk.StateType.NORMAL, self.clrMenuBg)

    def on_ebMenuPreferences_button_release_event(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[0]:
            self.changeMenuBackground(menuItems[0], True)
            self.lblMenuTitle.set_text(self.lblMenuPreferences.get_text())
            self.nbConky.set_current_page(0)

    def on_ebMenuNetwork_button_release_event(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[1]:
            self.changeMenuBackground(menuItems[1], True)
            self.lblMenuTitle.set_text(self.lblMenuNetwork.get_text())
            self.nbConky.set_current_page(1)

    def on_ebMenuSystem_button_release_event(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[2]:
            self.changeMenuBackground(menuItems[2], True)
            self.lblMenuTitle.set_text(self.lblMenuSystem.get_text())
            self.nbConky.set_current_page(2)

    # ===============================================
    # Button functions
    # ===============================================

    def on_btnSave_clicked(self, widget):
        self.saveSettings()

    def on_btnPrefActionApply_clicked(self, widget):
        action = self.getActiveComboValue(self.cmbPrefAction)
        if action:
            if action[0] == 0:
                # Start
                if functions.isProcessRunning('conky'):
                    os.system('killall conky')
                os.system('conky &')
                self.log.write(_("Conky started"), 'conky.on_btnPrefActionApply_clicked', 'info')
            elif action[0] == 1:
                # Stop
                if functions.isProcessRunning('conky'):
                    os.system('killall conky')
                    self.log.write(_("Conky stopped"), 'conky.on_btnPrefActionApply_clicked', 'info')
                else:
                    self.log.write(_("Conky is not running"), 'conky.on_btnPrefActionApply_clicked', 'info')
            elif action[0] == 2:
                # Remove
                self.removeConky()
                self.getDefaultSettings()
                self.log.write(_("Conky removed"), 'conky.on_btnPrefActionApply_clicked', 'info')

    def on_btnNetspeed_clicked(self, widget):
        self.openUrl("http://speedtest.net")

    # ===============================================
    # Get settings
    # ===============================================

    # Default settings (no .conkyrc in user home directory)
    def getDefaultSettings(self):
        # Set default values in gui
        self.log.write(_("Get default settings"), 'conky.getDefaultSettings', 'info')
        self.cmbPrefAction.set_active(0)
        self.cmbPrefSleep.set_active(2)
        self.cmbPrefAlign.set_active(0)
        self.chkPrefAutostart.set_active(True)
        self.txtNetwInterface.set_text(functions.getNetworkInterface())
        self.txtNetwDownSpeed.set_text(self.defaultSpeed)
        self.txtNetwUpSpeed.set_text(self.defaultSpeed)
        self.chkNetwLanIP.set_active(True)
        self.chkNetwIP.set_active(True)
        self.chkSysCores.set_active(True)
        self.chkSysHd.set_active(True)
        self.cmbSysTempUnit.set_active(0)
        self.chkSysCpuFan.set_active(True)
        self.chkSysChassisFan.set_active(True)
        self.rbtSysBattery.set_active(True)
        self.chkSysKernel.set_active(True)
        self.chkSysUP.set_active(True)

    # Get conky settings for the current user
    def getSettings(self):
        if exists(self.conkyrc):
            self.log.write(_("Start reading existing settings"), 'conky.getSettings', 'info')
            self.cmbPrefAction.set_active(0)
            # TODO: Read values from conkyrc, and show these in the gui
            conkyrcCont = functions.getFileContents(self.conkyrc)
            luaCont = functions.getFileContents(self.lua)
            startCont = functions.getFileContents(self.conkyStart)

            if functions.findRegExpInString('\[ETH\]', conkyrcCont):
                # If the [ETH] placeholder is found, assume template
                self.getDefaultSettings()
            else:
                # Preferences
                if exists(self.desktop):
                    self.log.write(_("Autostart found"), 'conky.getSettings', 'debug')
                    self.chkPrefAutostart.set_active(True)

                sleepStr = functions.findRegExpInString('\d+', startCont)
                if sleepStr:
                    sleepNr = functions.strToNumber(sleepStr, True)
                    self.log.write(_("Current nr of seconds to sleep before starting Conky: %(sleepnr)d" % {'sleepnr': sleepNr}), 'conky.getSettings', 'debug')
                    index = -1
                    for val in self.sleep:
                        if index >= 0:
                            if sleepNr < val[0]:
                                break
                        index += 1
                    self.cmbPrefSleep.set_active(index)

                alignment = functions.findRegExpInString('alignment\s([a-z]*)', conkyrcCont, 1)
                if alignment:
                    self.log.write(_("Current alignment: %(alignment)s" % {'alignment': alignment}), 'conky.getSettings', 'debug')
                    if alignment == 'tr':
                        self.cmbPrefAlign.set_active(0)
                    else:
                        self.cmbPrefAlign.set_active(1)
                else:
                    self.cmbPrefAlign.set_active(0)

                # Network
                eth = functions.findRegExpInString('\{downspeed\s+([a-z0-9]*)', conkyrcCont, 1)
                if eth:
                    self.log.write(_("Current network interface: %(interface)s" % {'interface': eth}), 'conky.getSettings', 'debug')
                    self.txtNetwInterface.set_text(eth)
                else:
                    self.txtNetwInterface.set_text(functions.getNetworkInterface())

                dl = functions.findRegExpInString('downspeedf.*\n.*\n,*[a-z\=\s]*(\d*)', luaCont, 1)
                if dl:
                    self.log.write(_("Current download speed: %(dl)s" % {'dl': dl}), 'conky.getSettings', 'debug')
                    self.txtNetwDownSpeed.set_text(dl)
                else:
                    self.txtNetwDownSpeed.set_text(self.defaultSpeed)

                ul = functions.findRegExpInString('upspeedf.*\n.*\n,*[a-z\=\s]*(\d*)', luaCont, 1)
                if ul:
                    self.log.write(_("Current upload speed: %(ul)s" % {'ul': ul}), 'conky.getSettings', 'debug')
                    self.txtNetwUpSpeed.set_text(ul)
                else:
                    self.txtNetwUpSpeed.set_text(self.defaultSpeed)

                if functions.findRegExpInString('<inet', conkyrcCont):
                    self.log.write(_("Check LAN IP"), 'conky.getSettings', 'debug')
                    self.chkNetwLanIP.set_active(True)
                if functions.findRegExpInString('dyndns', conkyrcCont):
                    self.log.write(_("Check IP"), 'conky.getSettings', 'debug')
                    self.chkNetwIP.set_active(True)

                # System
                if functions.findRegExpInString('core\d*\s+temp', conkyrcCont):
                    self.log.write(_("Check cores"), 'conky.getSettings', 'debug')
                    self.chkSysCores.set_active(True)
                if functions.findRegExpInString('hddtemp', conkyrcCont, 0, True):
                    self.log.write(_("Check HD temperature"), 'conky.getSettings', 'debug')
                    self.chkSysHd.set_active(True)

                if functions.findRegExpInString('sensors\s+\-f', conkyrcCont):
                    self.log.write(_("Using temperature unit Fahrenheit"), 'conky.getSettings', 'debug')
                    self.cmbSysTempUnit.set_active(1)
                else:
                    self.log.write(_("Using temperature unit Celsius"), 'conky.getSettings', 'debug')
                    self.cmbSysTempUnit.set_active(0)

                if functions.findRegExpInString('cpu\s+fan', conkyrcCont):
                    self.log.write(_("Check CPU fan"), 'conky.getSettings', 'debug')
                    self.chkSysCpuFan.set_active(True)
                if functions.findRegExpInString('chassis\s+fan', conkyrcCont):
                    self.log.write(_("Check chassis fan"), 'conky.getSettings', 'debug')
                    self.chkSysChassisFan.set_active(True)
                if functions.findRegExpInString('kernel', conkyrcCont, 0, True):
                    self.log.write(_("Check kernel"), 'conky.getSettings', 'debug')
                    self.chkSysKernel.set_active(True)
                if functions.findRegExpInString('packlevel', conkyrcCont):
                    self.log.write(_("Check Update Pack"), 'conky.getSettings', 'debug')
                    self.chkSysUP.set_active(True)
        else:
            self.getDefaultSettings()

    # ===============================================
    # Save settings
    # ===============================================

    # Save settings: copy templates, and set values
    def saveSettings(self):
        self.log.write(_("Save settings..."), 'conky.saveSettings', 'info')

        # Kill Conky, and remove all files
        self.removeConky()
        # Wait 5 seconds in the hope conky was stopped
        sleep(5)

        # conkyrc
        template = join(self.scriptDir, 'cfg/conkyrc')
        if exists(template):
            self.log.write(_("Copy %(template)s to %(conkyrc)s" % {"template": template, "conkyrc" :self.conkyrc}), 'conky.saveSettings', 'debug')
            shutil.copy2(template, self.conkyrc)
            functions.chownCurUsr(self.conkyrc)
        else:
            self.log.write(_("Conkyrc template not found %(template)s" % {"template": template}), 'conky.saveSettings', 'error')

        # lua
        template = join(self.scriptDir, 'cfg/clock_rings.lua')
        if exists(template):
            if not exists(self.luaDir):
                os.makedirs(self.luaDir)
            self.log.write(_("Copy %(template)s to %(lua)s" % {"template": template, "lua" :self.lua}), 'conky.saveSettings', 'debug')
            shutil.copy2(template, self.lua)
            functions.chownCurUsr(self.lua)
        else:
            self.log.write(_("Lua template not found %(template)s" % {"template": template}), 'conky.saveSettings', 'error')

        # start script
        template = join(self.scriptDir, 'cfg/conky-start')
        if os.path.exists(template):
            self.log.write(_("Copy %(template)s to %(conkyStart)s" % {"template": template, "conkyStart" :self.conkyStart}), 'conky.saveSettings', 'debug')
            shutil.copy2(template, self.conkyStart)
            functions.chownCurUsr(self.conkyStart)
            functions.makeExecutable(self.conkyStart)
        else:
            self.log.write(_("Start script not found %(template)s" % {"template": template}), 'conky.saveSettings', 'error')

        # Download and upload speed
        dl = self.txtNetwDownSpeed.get_text()
        functions.replaceStringInFile('\[DSPEED\]', str(dl), self.lua)
        self.log.write(_("Save download speed: %(dl)s" % {'dl': dl}), 'conky.saveSettings', 'debug')
        ul = self.txtNetwUpSpeed.get_text()
        functions.replaceStringInFile('\[USPEED\]', str(ul), self.lua)
        self.log.write(_("Save upload speed: %(ul)s" % {'ul': ul}), 'conky.saveSettings', 'debug')

        # Battery / Swap
        #bat = '/proc/acpi/battery/BAT0/state'
        if self.rbtSysSwap.get_active():
            self.log.write(_("Swap seletected: replace Battery with Swap index"), 'conky.saveSettings', 'debug')
            functions.replaceStringInFile('\$\{battery_percent BAT1\}', '${swapperc}', self.conkyrc)
            functions.replaceStringInFile('\}BAT', '}Swap', self.conkyrc)
            functions.replaceStringInFile("'battery_percent'", "'swapperc'", self.lua)
            functions.replaceStringInFile("'BAT1'", "''", self.lua)

        # Get selecte temperature unit, and get sensors data accordingly
        tempUnit = self.getActiveComboValue(self.cmbSysTempUnit)[1][0:1].lower()
        if tempUnit == 'c':
            # Celsius
            self.log.write(_("Temperature unit: Celsius"), 'conky.saveSettings', 'debug')
            sensorsCommand = 'sensors'
            sensors = self.ec.run(sensorsCommand, False, False)
        else:
            # Fahrenheit
            self.log.write(_("Temperature unit: Fahrenheit"), 'conky.saveSettings', 'debug')
            sensorsCommand = 'sensors -f'
            sensors = self.ec.run(sensorsCommand, False, False)

        # Core temperature
        if self.chkSysCores.get_active():
            coreList = []
            sensorsList = sensors.splitlines(True)
            for line in sensorsList:
                reObj = re.search('core\s{0,}\d.*\:', line, re.I)
                if reObj:
                    newLine = self.commandCore.replace('[CORESTR]', reObj.group(0))
                    newLine = newLine.replace('[SENSORSTR]', sensorsCommand)
                    self.log.write(_("Core found: %(core)s" % {'core': reObj.group(0)}), 'conky.saveSettings', 'debug')
                    coreList.append(newLine)

            if coreList:
                self.log.write(_("Add Core lines to .conkyrc"), 'conky.saveSettings', 'debug')
                functions.replaceStringInFile('#\s\[CORE\]', '\n'.join(coreList), self.conkyrc)

        # CPU fan speed
        if self.chkSysCpuFan.get_active():
            cpufan = functions.findRegExpInString('cpu\s{0,}fan.*\:', sensors)
            self.log.write(_("Cpu fan value = %(cpufan)s" % {'cpufan' :str(cpufan)}), 'conky.saveSettings', 'debug')
            if cpufan:
                newLine = self.commandCpu.replace('[CPUSTR]', cpufan)
                functions.replaceStringInFile('#\s\[CPUFAN\]', newLine, self.conkyrc)

        # Chassis fan speed
        if self.chkSysChassisFan.get_active():
            chafan = functions.findRegExpInString('chassis\s{0,}fan.*\:', sensors)
            self.log.write(_("Chassis fan value = %(chafan)s" % {'chafan' :str(chafan)}), 'conky.saveSettings', 'debug')
            if chafan:
                newLine = self.commandChassis.replace('[CHASTR]', chafan)
                functions.replaceStringInFile('#\s\[CHAFAN\]', newLine, self.conkyrc)

        # HD temperature unit
        if self.chkSysHd.get_active():
            self.log.write(_("Add HDD temperature to .conkyrc"), 'conky.saveSettings', 'debug')
            newLine = self.commandHdd.replace('[TEMPUNIT]', tempUnit.upper())
            hddCommand = 'hddtemp -n'
            if tempUnit == 'f':
                hddCommand = 'hddtemp -n -u f'
            newLine = newLine.replace('[HDDSTR]', hddCommand)
            functions.replaceStringInFile('#\s\[HDDTEMP\]', newLine, self.conkyrc)

        # LAN IP
        if self.chkNetwLanIP.get_active():
            self.log.write(_("Add LAN IP to .conkyrc"), 'conky.saveSettings', 'debug')
            functions.replaceStringInFile('#\s\[LANIP\]', self.commandLanIp, self.conkyrc)

        # IP
        if self.chkNetwIP.get_active():
            self.log.write(_("Add IP to .conkyrc"), 'conky.saveSettings', 'debug')
            functions.replaceStringInFile('#\s\[IP\]', self.commandIp, self.conkyrc)

        # Kernel
        if self.chkSysKernel.get_active():
            self.log.write(_("Add Kernel to .conkyrc"), 'conky.saveSettings', 'debug')
            functions.replaceStringInFile('#\s\[KERNEL\]', self.commandKernel, self.conkyrc)

        # UP
        if self.chkSysUP.get_active():
            self.log.write(_("Add Update Pack to .conkyrc"), 'conky.saveSettings', 'debug')
            functions.replaceStringInFile('#\s\[UP\]', self.commandUp, self.conkyrc)

        # Conky desktop alignment
        alignment = self.getActiveComboValue(self.cmbPrefAlign)
        self.log.write(_("Conky alignment = %(alignment)s" % {'alignment': alignment[1]}), 'conky.saveSettings', 'debug')
        if alignment[0] > 0:
            functions.replaceStringInFile('alignment\s+tr', 'alignment tl', self.conkyrc)

        # Write sleep before conky start
        sleepNr = functions.strToNumber(self.getActiveComboValue(self.cmbPrefSleep)[1], True)
        self.log.write(_("Conky sleep before start = %(sleep)d seconds" % {'sleep': sleepNr}), 'conky.saveSettings', 'debug')
        if sleepNr != 20:
            functions.replaceStringInFile('20', str(sleepNr), self.conkyStart)

        # Network interface
        eth = self.txtNetwInterface.get_text()
        self.log.write(_("Save network interface: %(interface)s" % {'interface': eth}), 'conky.saveSettings', 'debug')
        functions.replaceStringInFile('\[ETH\]', eth, self.conkyrc)
        functions.replaceStringInFile('\[ETH\]', eth, self.lua)

        # Change color scheme for SolydX
        if 'solydx' in self.dist.lower():
            self.log.write(_("Create orange theme for SolydX"), 'conky.saveSettings', 'debug')
            functions.replaceStringInFile(TEXT_BLUE, TEXT_ORANGE, self.conkyrc)
            functions.replaceStringInFile(TEXT_BLUE, TEXT_ORANGE, self.lua)

        # Automatically start Conky when the user logs in
        if self.chkPrefAutostart.get_active() and not exists(self.desktop):
            self.log.write(_("Write autostart file: %(desktop)s" % {'desktop': self.desktop}), 'conky.saveSettings', 'debug')
            if not exists(self.autostartDir):
                os.makedirs(self.autostartDir)
            desktopCont = '[Desktop Entry]\nComment=SolydXK Conky\nExec=[CONKYSTART]\nIcon=/usr/share/solydxk/logo.png\nStartupNotify=true\nTerminal=false\nType=Application\nName=SolydXK Conky\nGenericName=SolydXK Conky'
            f = open(self.desktop, 'w')
            f.write(desktopCont.replace('[CONKYSTART]', self.conkyStart))
            f.close()
            functions.makeExecutable(self.desktop)

        msg = "SolydXK Conky configuration has finished.\n\nWill now start Conky with the new configuration."
        MessageDialogSave(self.window.get_title(), msg, Gtk.MessageType.INFO, self.window).show()
        self.log.write(_("Save settings done"), 'conky.saveSettings', 'info')

        # Restart Conky
        if functions.isProcessRunning('conky'):
            os.system('killall conky')
        os.system('conky &')

    # ===============================================
    # Miscellaneous functions
    # ===============================================

    def removeConky(self):
        if functions.isProcessRunning('conky'):
            os.system('killall conky')
        if exists(self.conkyrc):
            os.remove(self.conkyrc)
        if exists(self.lua):
            os.remove(self.lua)
        if exists(self.desktop):
            os.remove(self.desktop)
        if exists(self.conkyStart):
            os.remove(self.conkyStart)

    # Open an URL or a program
    def openUrl(self, urlOrPath):
        if urlOrPath != '':
            if '://' in urlOrPath:
                self.log.write(_("Open URL: %(url)s") % {"url": urlOrPath}, 'conky.openUrl', 'debug')
                webbrowser.open(urlOrPath)
            else:
                self.log.write(_("Start program: %(prg)s") % {"prg": urlOrPath}, 'conky.openUrl', 'debug')
                os.system(urlOrPath)
        else:
            self.log.write(_("Nothing to open"), 'conky.openUrl', 'error')

    # Get the selected index and value from a combo box
    def getActiveComboValue(self, combo):
        value = None
        model = combo.get_model()
        active = combo.get_active()
        if active >= 0:
            value = [active, model[active][0]]
        return value

    # Close the gui
    def on_conkyWindow_destroy(self, widget, data=None):
        # Close the app
        Gtk.main_quit()

if __name__ == '__main__':
    # Create an instance of our GTK application
    try:
        gui = Conky()
        Gtk.main()
    except KeyboardInterrupt:
        pass
