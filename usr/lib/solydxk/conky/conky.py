#! /usr/bin/env python3

# sudo apt-get install python3-gi
# from gi.repository import Gtk, GdkPixbuf, GObject, Pango, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import os
import functions
import webbrowser
import shutil
from os.path import abspath, dirname, join, expanduser, exists
from time import sleep
from config import Config
from logger import Logger
from execcmd import ExecCmd
from dialogs import MessageDialog, WarningDialog

# i18n: http://docs.python.org/3/library/gettext.html
import gettext
from gettext import gettext as _
gettext.install('solydxk-conky')

# Menu items
menuItems = ['preferences', 'network', 'system', 'colors']

# Default colors
DAY_CLOCK_K = '009BD4'
DAY_CLOCK_X = 'FF7F01'
DATE_TITLE_K = 'FFFFFF'
DATE_TITLE_X = 'FFFFFF'
SYS_INFO_K = '00455F'
SYS_INFO_X = '842900'


#class for the main window
class Conky(object):

    def __init__(self):
        self.scriptDir = abspath(dirname(__file__))

        # Load window and widgets
        self.builder = Gtk.Builder()
        self.builder.add_from_file(join(self.scriptDir, '../../../share/solydxk/conky/conky.glade'))

        go = self.builder.get_object
        self.window = go('conkyWindow')
        self.lblMenuTitle = go('lblMenuTitle')
        self.statusbar = go('statusbar')
        self.btnPreferences = go('btnPreferences')
        self.btnNetwork = go('btnNetwork')
        self.btnSystem = go('btnSystem')
        self.btnColors = go('btnColors')
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
        self.lblSysKernel = go('lblSysKernel')
        self.chkSysKernel = go('chkSysKernel')

        # Color objects
        self.colorchooser = go('colorchooserDialog')
        self.lblDateTitle = go('lblDateTitle')
        self.lblDayClock = go('lblDayClock')
        self.lblSystemInfo = go('lblSystemInfo')
        self.colorBtnDateTitle = go('colorBtnDateTitle')
        self.colorBtnDayClock = go('colorBtnDayClock')
        self.colorBtnSystemInfo = go('colorBtnSystemInfo')
        self.dateTitleColor = None
        self.dayClockColor = None
        self.systemInfoColor = None
        self.dateTitleColorNew = None
        self.dayClockColorNew = None
        self.systemInfoColorNew = None

        # Translations
        self.window.set_title(_("SolydXK Conky"))
        self.btnPreferences.set_label(_("Preferences"))
        self.btnNetwork.set_label(_("Network"))
        self.btnSystem.set_label(_("System"))
        self.btnColors.set_label(_("Colors"))
        self.btnSave.set_label(_("Save"))
        self.lblPrefAction.set_label(_("Action"))
        self.btnPrefActionApply.set_label(_("Apply"))
        self.lblPrefAutostart.set_label(_("Autostart"))
        self.lblPrefAutostartText.set_label(_("Autostart Conky on login."))
        self.lblPrefSleep.set_label(_("Sleep"))
        self.lblPrefSleepText.set_label(_("Seconds to wait before starting Conky.\nDefault is 20 seconds."))
        self.lblPrefAlign.set_label(_("Align"))
        self.lblPrefAlignText.set_label(_("Conky alignment on the desktop."))
        self.lblNetwInterface.set_label(_("Interface"))
        self.lblNetwInterfaceText.set_label(_("Auto detected (use ifconfig)."))
        self.lblNetwDownSpeed.set_label(_("Download speed"))
        self.lblNetwSpeedText.set_label(_("Test your download and upload speed\nwith speedtest.net (in Kilobytes)."))
        self.lblNetwUpSpeed.set_label(_("Upload speed"))
        self.btnNetspeed.set_label("speedtest.net")
        self.lblNetwLanIP.set_label(_("LAN IP"))
        self.lblNetwLanIPText.set_label(_("Check to show these items."))
        self.lblNetwIP.set_label(_("IP"))
        self.lblSysCoresTemp.set_label(_("Core temperature"))
        self.lblSysCoresTempText.set_label(_("Check to show these items."))
        self.lblSysHdTemp.set_label(_("HD temperature"))
        self.lblSysTempUnit.set_label(_("Temperature unit"))
        self.lblSysCpuFan.set_label(_("CPU fan speed"))
        self.lblSysChassisFan.set_label(_("Chassis fan speed"))
        self.lblSysKernel.set_label(_("Kernel"))
        self.lblDateTitle.set_label(_("Date and title"))
        self.lblDayClock.set_label(_("Day and clock"))
        self.lblSystemInfo.set_label(_("System information"))
        self.corelbl = _("Core temp")
        self.cpulbl = _("CPU fan")
        self.chassislbl = _("Chassis fan")
        self.hdlbl = _("HD temp")
        self.lanlbl = _("LAN IP")
        self.iplbl = _("IP")
        self.kernellbl = _("Kernel")
        reset = _("Reset")
        go('btnResetDateTitle').set_label(reset)
        go('btnResetDayClock').set_label(reset)
        go('btnResetSystemInfo').set_label(reset)

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

        # Get distribution specific settings
        self.dist = functions.getDistribution(False).lower()
        conf_path = join(self.scriptDir, 'cfg/conky-k.conf')
        self.conkyrc_template = join(self.scriptDir, 'cfg/conkyrc-k')
        self.lua_template = join(self.scriptDir, 'cfg/clock_rings-k.lua')
        self.dateTitleColorDefault = DATE_TITLE_K.upper()
        self.dayClockColorDefault = DAY_CLOCK_K.upper()
        self.systemInfoColorDefault = SYS_INFO_K.upper()
        if 'solydx' in self.dist:
            conf_path = join(self.scriptDir, 'cfg/conky-x.conf')
            self.conkyrc_template = join(self.scriptDir, 'cfg/conkyrc-x')
            self.lua_template = join(self.scriptDir, 'cfg/clock_rings-x.lua')
            self.dateTitleColorDefault = DATE_TITLE_X.upper()
            self.dayClockColorDefault = DAY_CLOCK_X.upper()
            self.systemInfoColorDefault = SYS_INFO_X.upper()

        # Read from config file
        self.cfg = Config(conf_path)
        self.commandCore = self.cfg.getValue('COMMANDS', 'core')
        self.commandCpu = self.cfg.getValue('COMMANDS', 'cpu')
        self.commandChassis = self.cfg.getValue('COMMANDS', 'chassis')
        self.commandHdd = self.cfg.getValue('COMMANDS', 'hdd')
        self.commandLanIp = self.cfg.getValue('COMMANDS', 'lanip')
        self.commandIp = self.cfg.getValue('COMMANDS', 'ip')
        self.commandKernel = self.cfg.getValue('COMMANDS', 'kernel')

        # Init variables
        self.ec = ExecCmd(self.log)
        self.selectedMenuItem = None
        self.defaultSpeed = '1000'
        self.home = expanduser("~/")
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
        self.on_btnPreferences_clicked()

        self.builder.connect_signals(self)
        self.window.show()

    # ===============================================
    # Menu section functions
    # ===============================================

    def on_btnPreferences_clicked(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[0]:
            self.selectedMenuItem = menuItems[0]
            self.lblMenuTitle.set_label(self.btnPreferences.get_label())
            self.nbConky.set_current_page(0)

    def on_btnNetwork_clicked(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[1]:
            self.selectedMenuItem = menuItems[1]
            self.lblMenuTitle.set_label(self.btnNetwork.get_label())
            self.nbConky.set_current_page(1)

    def on_btnSystem_clicked(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[2]:
            self.selectedMenuItem = menuItems[2]
            self.lblMenuTitle.set_label(self.btnSystem.get_label())
            self.nbConky.set_current_page(2)

    def on_btnColors_clicked(self, widget=None, event=None):
        if self.selectedMenuItem != menuItems[3]:
            self.selectedMenuItem = menuItems[3]
            self.lblMenuTitle.set_label(self.btnColors.get_label())
            self.nbConky.set_current_page(3)

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
                if self.startConky():
                    self.log.write("Conky started", 'conky.on_btnPrefActionApply_clicked', 'info')
                else:
                    self.log.write("Could not start Conky", 'conky.on_btnPrefActionApply_clicked', 'warning')
            elif action[0] == 1:
                # Stop
                if self.stopConky():
                    self.log.write("Conky stopped", 'conky.on_btnPrefActionApply_clicked', 'info')
                else:
                    self.log.write("Could not stop Conky", 'conky.on_btnPrefActionApply_clicked', 'warning')
            elif action[0] == 2:
                # Remove
                self.removeConky()
                self.getDefaultSettings()
                self.log.write("Conky removed", 'conky.on_btnPrefActionApply_clicked', 'info')

    def on_btnNetspeed_clicked(self, widget):
        self.openUrl("http://speedtest.net")

    def on_colorBtnDateTitle_color_set(self, widget):
        hex_color = self.getHexColor(widget)
        if hex_color != self.dateTitleColor:
            self.dateTitleColorNew = hex_color
            self.log.write("Selected Date and Title color: %(hex_color)s" % {'hex_color': hex_color}, 'conky.on_colorBtnDateTitle_color_set', 'info')

    def on_colorBtnDayClock_color_set(self, widget):
        hex_color = self.getHexColor(widget)
        if hex_color != self.dayClockColor:
            self.dayClockColorNew = hex_color
            self.log.write("Selected Day and Clock color: %(hex_color)s" % {'hex_color': hex_color}, 'conky.on_colorBtnDayClock_color_set', 'info')

    def on_colorBtnSystemInfo_color_set(self, widget):
        hex_color = self.getHexColor(widget)
        if hex_color != self.systemInfoColor:
            self.systemInfoColorNew = hex_color
            self.log.write("Selected System Information color: %(hex_color)s" % {'hex_color': hex_color}, 'conky.on_colorBtnSystemInfo_color_set', 'info')

    def on_btnResetDateTitle_clicked(self, widget):
        if self.dateTitleColor != self.dateTitleColorDefault:
            self.dateTitleColorNew = self.dateTitleColorDefault
            self.setColorButtonColor(self.colorBtnDateTitle, self.dateTitleColorDefault)
            self.log.write("Reset Date and Title color: %s" % self.dateTitleColorDefault, 'conky.on_btnResetDateTitle_clicked', 'info')

    def on_btnResetDayClock_clicked(self, widget):
        if self.dayClockColor != self.dayClockColorDefault:
            self.dayClockColorNew = self.dayClockColorDefault
            self.setColorButtonColor(self.colorBtnDayClock, self.dayClockColorDefault)
            self.log.write("Reset Day and Clock color: %s" % self.dayClockColorDefault, 'conky.on_btnResetDayClock_clicked', 'info')

    def on_btnResetSystemInfo_clicked(self, widget):
        if self.systemInfoColor != self.systemInfoColorDefault:
            self.systemInfoColorNew = self.systemInfoColorDefault
            self.setColorButtonColor(self.colorBtnSystemInfo, self.systemInfoColorDefault)
            self.log.write("Reset System Information color: %s" % self.systemInfoColorDefault, 'conky.on_btnResetSystemInfo_clicked', 'info')

    # ===============================================
    # Get settings
    # ===============================================

    # Default settings (no .conkyrc in user home directory)
    def getDefaultSettings(self):
        # Set default values in gui
        self.log.write("Get default settings", 'conky.getDefaultSettings', 'info')
        self.cmbPrefAction.set_active(0)
        self.cmbPrefSleep.set_active(2)
        self.cmbPrefAlign.set_active(0)
        self.chkPrefAutostart.set_active(True)
        eth = functions.getNetworkInterface()
        if eth is None:
            eth = 'eth0'
        self.txtNetwInterface.set_text(eth)
        self.txtNetwDownSpeed.set_text("%s0" % self.defaultSpeed)
        self.txtNetwUpSpeed.set_text(self.defaultSpeed)
        self.chkNetwLanIP.set_active(True)
        self.chkNetwIP.set_active(True)
        self.chkSysCores.set_active(True)
        self.chkSysHd.set_active(True)
        self.cmbSysTempUnit.set_active(0)
        self.chkSysCpuFan.set_active(True)
        self.chkSysChassisFan.set_active(True)
        self.chkSysKernel.set_active(True)
        self.dayClockColor = self.dayClockColorDefault
        self.dateTitleColor = self.dateTitleColorDefault
        self.systemInfoColor = self.systemInfoColorDefault
        self.setColorButtonColor(self.colorBtnDayClock, self.dayClockColor)
        self.setColorButtonColor(self.colorBtnDateTitle, self.dateTitleColor)
        self.setColorButtonColor(self.colorBtnSystemInfo, self.systemInfoColor)

    # Get conky settings for the current user
    def getSettings(self):
        if exists(self.conkyrc):
            self.log.write("Start reading existing settings", 'conky.getSettings', 'info')
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
                    self.log.write("Autostart found", 'conky.getSettings', 'debug')
                    self.chkPrefAutostart.set_active(True)
                try:
                    sleepStr = functions.findRegExpInString('\d{2,}', startCont)
                    if sleepStr:
                        sleepNr = functions.strToNumber(sleepStr, True)
                        self.log.write("Current nr of seconds to sleep before starting Conky: %(sleepnr)d" % {'sleepnr': sleepNr}, 'conky.getSettings', 'debug')
                        index = -1
                        for val in self.sleep:
                            if index >= 0:
                                if sleepNr < val[0]:
                                    break
                            index += 1
                        self.cmbPrefSleep.set_active(index)
                except:
                    # Best effort
                    pass

                alignment = functions.findRegExpInString('alignment\s([a-z]*)', conkyrcCont, 1)
                if alignment:
                    self.log.write("Current alignment: %(alignment)s" % {'alignment': alignment}, 'conky.getSettings', 'debug')
                    if alignment == 'tr':
                        self.cmbPrefAlign.set_active(0)
                    else:
                        self.cmbPrefAlign.set_active(1)
                else:
                    self.cmbPrefAlign.set_active(0)

                # Network
                eth = functions.findRegExpInString('\{downspeed\s+([a-z0-9]*)', conkyrcCont, 1)
                if eth:
                    self.log.write("Current network interface: %(interface)s" % {'interface': eth}, 'conky.getSettings', 'debug')
                    self.txtNetwInterface.set_text(eth)
                else:
                    eth = functions.getNetworkInterface()
                    if eth is None:
                        eth = 'eth0'
                    self.txtNetwInterface.set_text()

                dl = functions.findRegExpInString('downspeedf.*\n.*\n,*[a-z\max=\s]*(\d*)', luaCont, 1)
                if dl:
                    self.log.write("Current download speed: %(dl)s" % {'dl': dl}, 'conky.getSettings', 'debug')
                    self.txtNetwDownSpeed.set_text(dl)
                else:
                    self.txtNetwDownSpeed.set_text("%s0" % self.defaultSpeed)

                ul = functions.findRegExpInString('upspeedf.*\n.*\n,*[a-z\max=\s]*(\d*)', luaCont, 1)
                if ul:
                    self.log.write("Current upload speed: %(ul)s" % {'ul': ul}, 'conky.getSettings', 'debug')
                    self.txtNetwUpSpeed.set_text(ul)
                else:
                    self.txtNetwUpSpeed.set_text(self.defaultSpeed)

                if functions.findRegExpInString(self.lanlbl, conkyrcCont, caseSensitive=True):
                    self.log.write("Check LAN IP", 'conky.getSettings', 'debug')
                    self.chkNetwLanIP.set_active(True)
                if functions.findRegExpInString('pre_exec myip', conkyrcCont):
                    self.log.write("Check IP", 'conky.getSettings', 'debug')
                    self.chkNetwIP.set_active(True)

                # System
                if functions.findRegExpInString(self.corelbl, conkyrcCont, caseSensitive=True):
                    self.log.write("Check cores", 'conky.getSettings', 'debug')
                    self.chkSysCores.set_active(True)
                if functions.findRegExpInString(self.hdlbl, conkyrcCont, caseSensitive=True):
                    self.log.write("Check HD temperature", 'conky.getSettings', 'debug')
                    self.chkSysHd.set_active(True)

                if functions.findRegExpInString('sensors\s+\-f', conkyrcCont):
                    self.log.write("Using temperature unit Fahrenheit", 'conky.getSettings', 'debug')
                    self.cmbSysTempUnit.set_active(1)
                else:
                    self.log.write("Using temperature unit Celsius", 'conky.getSettings', 'debug')
                    self.cmbSysTempUnit.set_active(0)

                if functions.findRegExpInString(self.cpulbl, conkyrcCont, caseSensitive=True):
                    self.log.write("Check CPU fan", 'conky.getSettings', 'debug')
                    self.chkSysCpuFan.set_active(True)
                if functions.findRegExpInString(self.chassislbl, conkyrcCont, caseSensitive=True):
                    self.log.write("Check chassis fan", 'conky.getSettings', 'debug')
                    self.chkSysChassisFan.set_active(True)
                if functions.findRegExpInString(self.kernellbl, conkyrcCont, caseSensitive=True):
                    self.log.write("Check kernel", 'conky.getSettings', 'debug')
                    self.chkSysKernel.set_active(True)

                # Colors
                hex_color = functions.findRegExpInString('\$\{color\s+([0-9a-zA-Z]{6})\}', conkyrcCont, 1)
                if hex_color is None:
                    hex_color = self.dayClockColorDefault
                else:
                    hex_color = hex_color.upper()
                self.log.write("Day and Clock color: %(hex_color)s" % {'hex_color': hex_color}, 'conky.getSettings', 'debug')
                self.dayClockColor = hex_color

                hex_color = functions.findRegExpInString('\$\{color\s+([0-9a-zA-Z]{6})\}\$\{hr\}', conkyrcCont, 1)
                if hex_color is None:
                    hex_color = self.dateTitleColorDefault
                else:
                    hex_color = hex_color.upper()
                self.log.write("Date and Title color: %(hex_color)s" % {'hex_color': hex_color}, 'conky.getSettings', 'debug')
                self.dateTitleColor = hex_color

                hex_color = functions.findRegExpInString('\$\{color\s+([0-9a-zA-Z]{6})\}\$\{goto', conkyrcCont, 1)
                if hex_color is None:
                    hex_color = self.systemInfoColorDefault
                else:
                    hex_color = hex_color.upper()
                self.log.write("System Information color: %(hex_color)s" % {'hex_color': hex_color}, 'conky.getSettings', 'debug')
                self.systemInfoColor = hex_color

                self.setColorButtonColor(self.colorBtnDayClock, self.dayClockColor)
                self.setColorButtonColor(self.colorBtnDateTitle, self.dateTitleColor)
                self.setColorButtonColor(self.colorBtnSystemInfo, self.systemInfoColor)

        else:
            self.getDefaultSettings()

    # ===============================================
    # Save settings
    # ===============================================

    # Save settings: copy templates, and set values
    def saveSettings(self):
        self.log.write("Save settings...", 'conky.saveSettings', 'info')

        # Reset colors
        self.dayClockColor = self.dayClockColorDefault
        self.dateTitleColor = self.dateTitleColorDefault
        self.systemInfoColor = self.systemInfoColorDefault
        # Kill Conky, and remove all files
        self.removeConky()

        # conkyrc
        if exists(self.conkyrc_template):
            if not exists(self.conkyrc):
                self.log.write("Copy %(template)s to %(conkyrc)s" % {"template": self.conkyrc_template, "conkyrc" :self.conkyrc}, 'conky.saveSettings', 'debug')
                shutil.copy2(self.conkyrc_template, self.conkyrc)
                functions.chownCurUsr(self.conkyrc)
        else:
            self.log.write("Conkyrc template not found %(template)s" % {"template": self.conkyrc_template}, 'conky.saveSettings', 'error')

        # lua
        if exists(self.lua_template):
            if not exists(self.lua):
                if not exists(self.luaDir):
                    os.makedirs(self.luaDir)
                self.log.write("Copy %(template)s to %(lua)s" % {"template": self.lua_template, "lua" :self.lua}, 'conky.saveSettings', 'debug')
                shutil.copy2(self.lua_template, self.lua)
                functions.chownCurUsr(self.lua)
        else:
            self.log.write("Lua template not found %(template)s" % {"template": self.lua_template}, 'conky.saveSettings', 'error')

        # start script
        template = join(self.scriptDir, 'cfg/conky-start')
        if os.path.exists(template):
            if not exists(self.conkyStart):
                self.log.write("Copy %(template)s to %(conkyStart)s" % {"template": template, "conkyStart" :self.conkyStart}, 'conky.saveSettings', 'debug')
                shutil.copy2(template, self.conkyStart)
        else:
            self.log.write("Start script not found %(template)s" % {"template": template}, 'conky.saveSettings', 'error')

        # Download and upload speed
        dl = self.txtNetwDownSpeed.get_text()
        functions.replaceStringInFile('\[DSPEED\]', str(dl), self.lua)
        self.log.write("Save download speed: %(dl)s" % {'dl': dl}, 'conky.saveSettings', 'debug')
        ul = self.txtNetwUpSpeed.get_text()
        functions.replaceStringInFile('\[USPEED\]', str(ul), self.lua)
        self.log.write("Save upload speed: %(ul)s" % {'ul': ul}, 'conky.saveSettings', 'debug')

        # Get selecte temperature unit, and get sensor data accordingly
        tempUnit = self.getActiveComboValue(self.cmbSysTempUnit)[1][0:1].lower()
        tempUnitStr = '°C'
        if tempUnit == 'c':
            # Celsius
            self.log.write("Temperature unit: Celsius", 'conky.saveSettings', 'debug')
            sensorsCommand = 'sensors'
        else:
            # Fahrenheit
            self.log.write("Temperature unit: Fahrenheit", 'conky.saveSettings', 'debug')
            tempUnitStr = '°F'
            sensorsCommand = 'sensors -f'
        sensors = self.ec.run(sensorsCommand, False, False)

        # Localization
        functions.replaceStringInFile('\[CPU\]', _("CPU"), self.conkyrc)
        functions.replaceStringInFile('\[RAM\]', _("RAM"), self.conkyrc)
        functions.replaceStringInFile('\[DISK\]', _("Disk"), self.conkyrc)
        functions.replaceStringInFile('\[NET\]', _("Net"), self.conkyrc)

        # Core temperature
        if self.chkSysCores.get_active():
            self.commandCore = self.commandCore.replace('[TEMPUNIT]', tempUnitStr)
            self.commandCore = self.commandCore.replace("[CORELABEL]", self.corelbl)
            self.commandCore = self.commandCore.replace("[SENSORSTR]", sensorsCommand)
            functions.replaceStringInFile('#\s*\[CORE\]', self.commandCore, self.conkyrc)
            self.log.write("Core command added", 'conky.saveSettings', 'debug')

        # CPU fan speed
        if self.chkSysCpuFan.get_active():
            cpufan = functions.findRegExpInString('cpu\s{0,}fan.*\:', sensors)
            self.log.write("Cpu fan value = %(cpufan)s" % {'cpufan' :str(cpufan)}, 'conky.saveSettings', 'debug')
            if cpufan:
                self.commandCpu = self.commandCpu.replace("[CPULABEL]", self.cpulbl)
                self.commandCpu = self.commandCpu.replace('[CPUSTR]', cpufan)

                functions.replaceStringInFile('#\s*\[CPUFAN\]', self.commandCpu, self.conkyrc)

        # Chassis fan speed
        if self.chkSysChassisFan.get_active():
            chafan = functions.findRegExpInString('chassis\s{0,}fan.*\:', sensors)
            self.log.write("Chassis fan value = %(chafan)s" % {'chafan' :str(chafan)}, 'conky.saveSettings', 'debug')
            if chafan:
                self.commandChassis = self.commandChassis.replace("[CHASSISLABEL]", self.chassislbl)
                self.commandChassis = self.commandChassis.replace('[CHASTR]', chafan)
                functions.replaceStringInFile('#\s*\[CHAFAN\]', self.commandChassis, self.conkyrc)

        # HD temperature unit
        if self.chkSysHd.get_active():
            self.log.write("Add HDD temperature to .conkyrc", 'conky.saveSettings', 'debug')
            self.commandHdd = self.commandHdd.replace('[TEMPUNIT]', tempUnitStr)
            self.commandHdd = self.commandHdd.replace('[HDLABEL]', self.hdlbl)
            hddCommand = 'hddtemp -n'
            if tempUnit == 'f':
                hddCommand = 'hddtemp -n -u f'
            self.commandHdd = self.commandHdd.replace('[HDDSTR]', hddCommand)
            functions.replaceStringInFile('#\s*\[HDDTEMP\]', self.commandHdd, self.conkyrc)

        # LAN IP
        if self.chkNetwLanIP.get_active():
            self.log.write("Add LAN IP to .conkyrc", 'conky.saveSettings', 'debug')
            self.commandLanIp = self.commandLanIp.replace("[LANLABEL]", self.lanlbl)
            functions.replaceStringInFile('#\s*\[LANIP\]', self.commandLanIp, self.conkyrc)

        # IP
        if self.chkNetwIP.get_active():
            self.log.write("Add IP to .conkyrc", 'conky.saveSettings', 'debug')
            self.commandIp = self.commandIp.replace("[IPLABEL]", self.iplbl)
            functions.replaceStringInFile('#\s*\[IP\]', self.commandIp, self.conkyrc)

        # Kernel
        if self.chkSysKernel.get_active():
            self.log.write("Add Kernel to .conkyrc", 'conky.saveSettings', 'debug')
            self.commandKernel = self.commandKernel.replace("[KERNELLABEL]", self.kernellbl)
            functions.replaceStringInFile('#\s*\[KERNEL\]', self.commandKernel, self.conkyrc)

        # Conky desktop alignment
        alignment = self.getActiveComboValue(self.cmbPrefAlign)
        self.log.write("Conky alignment = %(alignment)s" % {'alignment': alignment[1]}, 'conky.saveSettings', 'debug')
        if alignment[0] > 0:
            functions.replaceStringInFile('alignment\s+tr', 'alignment tl', self.conkyrc)

        # Write sleep before conky start
        sleepNr = functions.strToNumber(self.getActiveComboValue(self.cmbPrefSleep)[1], True)
        self.log.write("Conky sleep before start = %(sleep)d seconds" % {'sleep': sleepNr}, 'conky.saveSettings', 'debug')
        if sleepNr != 20:
            functions.replaceStringInFile('20', str(sleepNr), self.conkyStart)

        # Network interface
        eth = self.txtNetwInterface.get_text()
        self.log.write("Save network interface: %(interface)s" % {'interface': eth}, 'conky.saveSettings', 'debug')
        functions.replaceStringInFile('\[ETH\]', eth, self.conkyrc)
        functions.replaceStringInFile('\[ETH\]', eth, self.lua)

        # Write colors
        if self.dayClockColorNew == self.dayClockColor:
            self.dayClockColorNew = None
        if self.dateTitleColorNew == self.dateTitleColor:
            self.dateTitleColorNew = None
        if self.systemInfoColorNew == self.systemInfoColor:
            self.systemInfoColorNew = None

        if self.dateTitleColorNew is not None:
            functions.replaceStringInFile(self.dateTitleColor, self.dateTitleColorNew, self.conkyrc)
            self.log.write("Replace Date and Title color %s with %s" % (self.dateTitleColor, self.dateTitleColorNew), 'conky.saveSettings', 'info')
            self.dateTitleColor = self.dateTitleColorNew
        if self.dayClockColorNew is not None:
            functions.replaceStringInFile(self.dayClockColor, self.dayClockColorNew, self.conkyrc)
            functions.replaceStringInFile(self.dayClockColor, self.dayClockColorNew, self.lua)
            self.log.write("Replace Day and Clock color %s with %s" % (self.dayClockColor, self.dayClockColorNew), 'conky.saveSettings', 'info')
            self.dayClockColor = self.dayClockColorNew
        if self.systemInfoColorNew is not None:
            functions.replaceStringInFile(self.systemInfoColor, self.systemInfoColorNew, self.conkyrc)
            functions.replaceStringInFile(self.systemInfoColor, self.systemInfoColorNew, self.lua)
            self.log.write("Replace System Info color %s with %s" % (self.systemInfoColor, self.systemInfoColorNew), 'conky.saveSettings', 'info')
            self.systemInfoColor = self.systemInfoColorNew

        # Automatically start Conky when the user logs in
        if self.chkPrefAutostart.get_active() and not exists(self.desktop):
            self.log.write("Write autostart file: %(desktop)s" % {'desktop': self.desktop}, 'conky.saveSettings', 'debug')
            if not exists(self.autostartDir):
                os.makedirs(self.autostartDir)
            desktopCont = '[Desktop Entry]\nComment=SolydXK Conky\nExec=[CONKYSTART]\nIcon=/usr/share/solydxk/logo.png\nStartupNotify=true\nTerminal=false\nType=Application\nName=SolydXK Conky\nGenericName=SolydXK Conky'
            f = open(self.desktop, 'w')
            f.write(desktopCont.replace('[CONKYSTART]', self.conkyStart))
            f.close()
            functions.makeExecutable(self.desktop)

        msg = "SolydXK Conky configuration has finished.\n\nWill now start Conky with the new configuration."
        MessageDialog(self.window.get_title(), msg)
        self.log.write("Save settings done", 'conky.saveSettings', 'info')

        # Restart Conky
        functions.makeExecutable(self.conkyStart)
        self.startConky()

    # ===============================================
    # Miscellaneous functions
    # ===============================================

    def startConky(self):
        max_wait = 5
        wait_cnt = 0
        if self.stopConky():
            os.system('conky &')
            while not functions.isProcessRunning('conky'):
                sleep(1)
                wait_cnt += 1
                if wait_cnt >= max_wait:
                    break
        if functions.isProcessRunning('conky'):
            return True
        return False

    def stopConky(self):
        max_wait = 5
        wait_cnt = 0
        os.system('killall conky')
        while functions.isProcessRunning('conky'):
            sleep(1)
            wait_cnt += 1
            if wait_cnt >= max_wait:
                break
        if not functions.isProcessRunning('conky'):
            return True
        return False

    def getHexColor(self, colorbutton, include_alpha=False):
        color = colorbutton.get_rgba()

        red = color.red
        if red <= 1:
            red = (color.red * 255)
        green = color.green
        if green <= 1:
            green = (color.green * 255)
        blue = color.blue
        if blue <= 1:
            blue = (color.blue * 255)
        alpha = color.alpha
        if alpha <= 1:
            alpha = (color.alpha * 255)

        if include_alpha:
            hex_color = "%02x%02x%02x%02x" % (red, green, blue, alpha)
        else:
            hex_color = "%02x%02x%02x" % (red, green, blue)

        #print((">> rgba = {} {} {} {} is hex {}".format(color.red, color.green, color.blue, color.alpha, hex_color)))
        return hex_color.upper()

    def setColorButtonColor(self, colorbutton, hex_color):
        rgba_color = Gdk.RGBA()
        hex_color = hex_color.strip()
        if hex_color[0:1] != '#':
            hex_color = "#%s" % hex_color
        if rgba_color.parse(hex_color):
            colorbutton.set_rgba(rgba_color)
        else:
            msg = _("Could not set color: %s" % hex_color)
            WarningDialog(self.btnColors.get_label(), msg)

    def removeConky(self):
        self.stopConky()
        if exists(self.conkyrc):
            os.rename(self.conkyrc, "%s.bak" % self.conkyrc)
        if exists(self.lua):
            os.rename(self.lua, "%s.bak" % self.lua)
        if exists(self.desktop):
            os.remove(self.desktop)
        if exists(self.conkyStart):
            os.remove(self.conkyStart)

    # Open an URL or a program
    def openUrl(self, urlOrPath):
        if urlOrPath != '':
            if '://' in urlOrPath:
                self.log.write("Open URL: %(url)s" % {"url": urlOrPath}, 'conky.openUrl', 'debug')
                webbrowser.open(urlOrPath)
            else:
                self.log.write("Start program: %(prg)s" % {"prg": urlOrPath}, 'conky.openUrl', 'debug')
                os.system(urlOrPath)
        else:
            self.log.write("Nothing to open", 'conky.openUrl', 'error')

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
