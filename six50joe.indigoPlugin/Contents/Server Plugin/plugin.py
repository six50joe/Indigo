#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################

import indigo
import subprocess

import os
import sys
import logging
import time
import thread
#import json, operator
#import csv,codecs,cStringIO
#from lib.csvUnicode import unicodeReader, unicodeWriter, UTF8Recoder
#from lib.strVarTime import prettyDate, strToTime, timeToStr, timeDiff
from collections import defaultdict
#from tabulate import tabulate
#from texttable.texttable import Texttable
from operator import itemgetter
#from ghpu import GitHubPluginUpdater
from ghpu import GitHubPluginUpdater
from os.path import expanduser
import datetime
import datetime
import dateutil.relativedelta
import re

CONFIG_FILE_DIR           = expanduser("~") + "/Documents"
RELAY_THRESHOLDS_FILENAME = "relay_thresholds.txt"
PropaneThresholds = {}

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.


#variableEnablePrefs = [u'triggeringNodeId', u'triggeringDeviceId', u'triggeringDeviceName', u'triggeringEventText']

#nodeStatsMap = dict()
#for i, j in enumerate(nodeStatsConf):
#	nodeStatsMap[j[0]] = i


#nodeStatsHeaders = {u'node' : u'Node', u'device' : u'Device', u'Cmds: In', u'Out', u'Notifications', u'Batt.reports', u'# Ack triggers: Slow', u'No Ack', u'AckTime (ms): Min', u'Max', u'Avg'}

########################################
# Tiny function to convert a list of integers (bytes in this case) to a
# hexidecimal string for pretty logging.
def convertListToHexStr(byteList):
	return ' '.join([u'%02X' % byte for byte in byteList])
	
########################################
# Tiny function to convert a list of integers (bytes in this case) to a
# hexidecimal list (string formatted) 
def convertListToHexStrList(byteList):
	return [u'0x%02X' % byte for byte in byteList]
	
########################################
# convert integer to hex string
def hexStr(integer):
	return u'0x%02X' % integer
	
########################################
# Safely get keys from dictionary
def safeGet(dct, defaultVal, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return defaultVal
    return dct

########################################
# Nested defaultdict   
def treeDD():
    return defaultdict(treeDD)
    
		
########################################
# Iterate through dct and remove references to triggerID
#def removeTriggerFromDict(d, triggerId):
#	for k, v in d.iteritems():
#		if isinstance(v, dict):
#			d[k] = removeTriggerFromDict(v, triggerId)
#		elif k == u'triggers':
#			d[k] = [t for t in v if t != triggerId]
#		else:
#			raise ValueError(u'Possible error in triggerMap dictionary, v: %s' % unicode(v))
#	return d


################################################################################
class Plugin(indigo.PluginBase):

	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		super(Plugin, self).__init__(pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		#indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

		self.errorState = False

		self.pluginName = u'Six50Joe'

                # Set plugin preferences
		self.setUpdatePluginPrefs()

			
	########################################
	def __del__(self):
		indigo.PluginBase.__del__(self)
				
	########################################
	def startup(self):
		self.logger.debug(u"startup called")

		self.logger.debug(u'Getting plugin updater')
		self.updater = GitHubPluginUpdater(self)
		

	########################################
	def updatePlugin(self):
		
		self.logger.info(u'Initiating plugin update')
		updateResult = self.updater.update()
		
		return updateResult

	########################################
	def checkPluginUpdates(self, notify = False, performUpdate = False):
		
		self.logger.debug(u'Checking for plugin updates')
		updateAvailable = self.updater.checkForUpdate()
		
		if updateAvailable:
			if notify and len(self.checkForUpdatesEmail) > 0:
				self.logger.debug(u'Notifying that new plugin version is available via e-mail')
				indigo.server.sendEmailTo(self.checkForUpdatesEmail, 
					subject=u'Indigo %s plugin update available' % (self.pluginName), 
					body=u'A new update of %s plugin is available and can be updated from the plugin menu within Indigo' % (self.pluginName))
					
			if performUpdate:
				self.updatePlugin()
				
		return updateAvailable

	# Catch changes to config prefs
	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		self.extDebug(u'CALL closedPrefsConfigUi, valuesDict: %s' % unicode(valuesDict))
		self.extDebug(u'CALL closedPrefsConfigUi, userCancelled: %s' % unicode(userCancelled))
		
		self.setUpdatePluginPrefs(True)

		# FIX DO VALIDATION
		self.pluginConfigErrorState = False

	########################################
	def shutdown(self):
		self.logger.debug(u"shutdown called")

		# moved to stopThread in runConcurrentThread, don't believe the below saved prefs at all times		
		# 		if self.keepStats:
		# 			self.logger.debug(u'Saving z-wave node statistics')
		# 			self.pluginPrefs[u'nodeStats'] = self.store(self.nodeStats)

	########################################
	def wakeUp(self):
	   indigo.PluginBase.wakeUp(self)
	   self.logger.debug("wakeUp method called")

	########################################
	def prepareToSleep(self):
	   indigo.PluginBase.prepareToSleep(self)
	   self.logger.debug("prepareToSleep method called")

	########################################
	def extDebug(self, msg):
		if self.extensiveDebug:
			self.debugLog(msg)

		
		
	########################################
	# If runConcurrentThread() is defined, then a new thread is automatically created
	# and runConcurrentThread() is called in that thread after startup() has been called.
	#
	# runConcurrentThread() should loop forever and only return after self.stopThread
	# becomes True. If this function returns prematurely then the plugin host process
	# will log an error and attempt to call runConcurrentThread() again after several seconds.
	def runConcurrentThread(self):
		try:
			counter = 0
			while True:
				self.logger.debug(u'runConcurrentThread')
				
				counter += 1
				self.sleep(3613)
		except self.StopThread:
			self.logger.debug(u'runConcurrentThread self.StopThread')
			if self.keepStats:
				self.logger.debug(u'Saving z-wave node statistics before quitting plugin')
				self.pluginPrefs[u'nodeStats'] = self.store(self.nodeStats)
		# 		if self.errorState:
		# 			# FIX, find some way to shutdown if there are errors
		# 			self.logger.error(u'Plugin in error state, stopping concurrent thread')
		# 			pass

				
		
	#####
	# Set or update plugin preferences
	# 	running 		: True if plugin is already running and prefs are to be changed
	#
	def setUpdatePluginPrefs(self, running = False):
		self.logger.debug(u'CALL setUpdatePluginPrefs, running: %s' % unicode(running))
		
		# Set log levels
		if running: setText = u'Changing'
		else: setText = u'Setting'
		self.indigo_log_handler.setLevel(self.pluginPrefs.get(u'logLevel', u'INFO'))
		self.plugin_file_handler.setLevel(u'DEBUG')
		self.extensiveDebug = self.pluginPrefs.get(u'extensiveDebug', False)
		self.logger.info(u'%s log level to %s' % (setText, self.pluginPrefs.get(u'logLevel', u'INFO')))
		self.logger.debug(u'Extensive debug logging set to %s' % unicode(self.extensiveDebug))
		self.logger.debug(u'%s file handler log level to DEBUG' % (setText))
		# DEBUG		: All debug info
		# INFO		: Informational messages relevant to the user
		# WARNING	: More critical information to the user, warnings
		# ERROR		: Errors not critical for plugin execution
		# CRITICAL	: Errors critical for plugin execution, plugin will stop
		
		self.checkForUpdatesInterval = self.pluginPrefs.get(u'checkForUpdatesInterval', 24)
		if self.checkForUpdatesInterval == u'':
			self.checkForUpdates = False
		else:
			self.checkForUpdates = True
			try:
				self.checkForUpdatesInterval = int(self.checkForUpdatesInterval)
			except:
				self.logger.error(u'Invalid plugin prefs value for update check frequency, defaulting to 24 hours')
				self.checkForUpdatesInterval = 24
				
			self.checkForUpdatesEmail = self.pluginPrefs.get(u'checkForUpdatesEmail', '')
		
		#self.autoUpdate = self.pluginPrefs.get(u'autoUpdate', False)
		# FIX, Indigo will ask for confirmation before plugin is updates, so best to leave as manual menu option
		self.autoUpdate = False
		
		self.keepStats = self.pluginPrefs.get(u'keepStats', False)
		if self.keepStats:
			self.nodeStats = self.load(self.pluginPrefs.get(u'nodeStats', self.store(dict()))) # see def emptyNodeStatList() for description
			
			# Update older versions of nodeStats
			for l in self.nodeStats:
				# after adding outNR
				if len(l) == 9:
					l = l[0:1] + [0] + l[2:]
					
		# Check plugin dependencies
		self.checkDependantPlugins()

	#####
	# Check for dependant plugins, if they are enabled and correct version is installed etc.
	#
	def checkDependantPlugins(self):
		self.logger.debug(u'Checking status of other plugins this plugin depends on')
		
		# [<plugin pref for enable of plugin>, <plugin id>, <Friendly name>, <min plugin version>]
		pluginList = []
			
		for plug in pluginList:
			
			usePlugin = self.pluginPrefs.get(plug[0], False)
			
			self.logger.debug(u'Checking plugin "%s"' % plug[2])
		
			try:
				if not usePlugin:
					raise
				try:
					indigoPlug = indigo.server.getPlugin(plug[1])
					if not indigoPlug.isRunning():
						raise ImportError(u'Plugin "%s" is not running, please install/enable, and re-enable in %s plugin preferences' % (plug[2], self.pluginName))
					if len(indigoPlug.pluginVersion) == 0 or indigoPlug.pluginVersion < plug[3]:
						raise ImportError(u'Plugin "%s" version %s is less than %s requires (%s), please update the plugin.\nUse of this plugin in %s has been disabled' % (plug[2], indigoPlug.pluginVersion, self.pluginName, plug[3], self.pluginName))
						
					# Plugin specific checks:
					if plug[1] == u'com.flyingdiver.indigoplugin.betteremail':
						smtpDevId = self.pluginPrefs.get(u'plugin-betteremail-smtpdevice', u'')
						if len(smtpDevId) == 0:
							raise ImportError(u'You need to specify a valid "%s" SMTP device in %s plugin preferences' % plug[2], self.pluginName)
						else:
							try:
								smtpDev = indigo.devices[int(smtpDevId)]
								if not smtpDev.enabled:
									raise
							except:
								raise ImportError(u'The specified "%s" SMTP device could not be loaded, please check\n%s plugin preferences and that the SMTP device is enabled' % (self.pluginName))					
				except ImportError as e:
					self.logger.error(e)
					raise
				except:
					self.logger.error(u'Could not load plugin "%s". Please install and re-enable in %s plugin preferences' % (plug[2], self.pluginName))
					raise
			except:
				# Common code for disabling use of the plugin
				if usePlugin: # configured to use plugin, so some error happened
					self.logger.debug(u'Disabling use of plugin "%s" in plugin prefs' % plug[2])
					if len(indigoPlug.pluginSupportURL) > 0:
						self.logger.info(u'"%s" support/install link: %s' % (plug[2], indigoPlug.pluginSupportURL))
				else:
					self.logger.debug(u'Not configured to use plugin "%s"' % plug[2])
				self.pluginPrefs[plug[0]] = False
				if plug[1] in self.dependantPlugins:
					del self.dependantPlugins[plug[1]]
			else:
				# Plugin is successfully initialized, add to dict of enabled plugins
				self.logger.debug(u'Plugin "%s" successfully checked' % plug[2])
				self.dependantPlugins[plug[1]] = indigoPlug

        def ping(self, ipOrUrl):
                rc = subprocess.call("/sbin/ping -t 1 -c 1 %s" \
                                     % (ipOrUrl),
                                     shell=True,
                                     stdout=subprocess.PIPE)
                if rc == 0:
                        return True
                else:
                        return False

	########################################
        def getPresenceDevices(self, filter="",
                                  valuesDict=None,
                                  typeId="",
                                  targetId=0):
            list = []
            for v in indigo.variables:
                if v.name.startswith("S50_PRESDT") \
                 and not v.name.endswith("_reached"):
                    list.append({'name' : v.name, 'value' : v.value})
            return list

	########################################
        def getPresenceDeviceList(self, filter="",
                                  valuesDict=None,
                                  typeId="",
                                  targetId=0):
                devList = self.getPresenceDevices()
                list = []
                for dev in devList:
                    list.append([dev['name'], dev['value']])
                return list

    
	########################################
	# UI List generators and callbackmethods
	########################################
	########################################
	# Actions
	########################################

	def pingOtherHouse(self, action):
		props = action.props
                varName = props[u'resultVarName']
                var = None
                if len(varName) > 0:
                        var = indigo.variables[varName]

                for i in range(0, int(props[u'numRetries'])):
                        reached = self.ping(props[u'ipOrUrl'])

                        if reached:
                                self.logger.debug("ping reached %s" % props[u'ipOrUrl'])
                                if var:
                                        indigo.variable.updateValue(var, value=unicode(True))
                                return True
                        else:
                                self.logger.debug("retry ping to %s" % props[u'ipOrUrl'])
                                time.sleep(int(props[u'retrySecs']))

                if  var:
                        indigo.variable.updateValue(var, value=unicode(False))
                return False

        def checkDevicePresence(self, arg1=None):
            devList = self.getPresenceDevices()
            deviceReached = False
            for d in devList:
                reachable = self.ping(d['value'])
                if not deviceReached and reachable:
                    deviceReached = True
                self.logger.debug("dev: %s: %s" % (d['name'], reachable))
                varName = d['name'] + "_reached"
                var = None
                if varName not in indigo.variables:
                    var = indigo.variable.create(varName, unicode(reachable))
                else:
                    var = indigo.variable.updateValue(varName, unicode(reachable))

            presenceVarName = 'DevicesPresent'
            if presenceVarName not in indigo.variables:
                var = indigo.variable.create(presenceVarName, unicode(deviceReached))
            else:
                var = indigo.variable.updateValue(presenceVarName, unicode(deviceReached))


        def iterate(self, iterable):
            iterator = iter(iterable)
            item = iterator.next()

            for next_item in iterator:
                yield item, next_item
                item = next_item

            
            yield item, None
    
        def readPropaneThresholds(self):
            global PropaneThresholds

            PropaneThresholds = {}
            
            path = CONFIG_FILE_DIR + "/" + RELAY_THRESHOLDS_FILENAME
            if os.path.exists(path):
                inputFile = open(path, 'r')
                for line in inputFile:
                    (pct, thresh) = line.split(',')
                    PropaneThresholds[pct] = thresh.strip()

            #for key in sorted(PropaneThresholds.iterkeys()):
            #    self.logger.debug("%s: %s" % (key, PropaneThresholds[key]))

            lastVal = 0
            for item, next_item in self.iterate(sorted(PropaneThresholds.iterkeys(), key=int)):
                if next_item is not None and \
                    PropaneThresholds[item] > PropaneThresholds[next_item]:
                    self.logger.warn("WARNING: propane thresholds out of order: %s(%d) < %s(%d)" \
                                     % (item, int(PropaneThresholds[item]),
                                        next_item, int(PropaneThresholds[next_item])))
                lastVal = PropaneThresholds[item]
                self.logger.debug("%s - next %s" % (str(item), str(next_item)))

        def writePropaneThresholds(self):
            path = CONFIG_FILE_DIR + "/" + RELAY_THRESHOLDS_FILENAME
            if os.path.exists(path):
                backup = path + "_" + datetime.datetime.today().strftime('%Y-%mvb-%d_%H:%M:%S')
                os.rename(path, backup)
                
            outFile = open(path, 'w')

            for key in sorted(PropaneThresholds.iterkeys(), key=int):
                outFile.write("%s,%s\n" % (key, PropaneThresholds[key]))

        def getPropaneSensorReading(self):
            relay = indigo.devices["Propane - Relay Output"]
            analog = indigo.devices["Propane - Analog Input"]

            indigo.device.turnOn(relay, duration=100)
            indigo.activePlugin.sleep(1)
            indigo.device.statusRequest(analog)
            self.logger.info("sensor value is: " + str(analog.sensorValue))
            return analog.sensorValue
            

        def getPropaneLevel(self, action):
            props = action.props
            testValStr = props[u'testSensorVal']
            testVal = None
            
            if testValStr.isdigit():
                testVal = int(float(testValStr))

            self.readPropaneThresholds()

            sensor = None

            if testVal is None:
                sensor = self.getPropaneSensorReading()
            else:
                sensor = testVal

            firstThreshold=True
            for pct, nextPct in self.iterate(sorted(PropaneThresholds.iterkeys(), key=int)):
                thresh = int(float(PropaneThresholds[pct]))
                nextThresh = -1
                if nextPct:
                    nextThresh = int(float(PropaneThresholds[nextPct]))
                self.logger.debug("%s(%d) - next %s(%d)" % (str(pct),
                                                            thresh,
                                                            str(nextPct), 
                                                            nextThresh))
                #                for t, threshold in enumerate(thresholds):
                calcPct = None
                if thresh <= sensor:
                    if nextPct is None:
                        # This reading is above the high

                        level = "> %s%%" % (pct)
                        calcPct = pct
                        break
                    if sensor <= nextThresh:
                        # The reading is between two thresholds

                        rangeBottom = thresh
                        rangeTop = nextThresh

                        range = (rangeTop - rangeBottom)
                        span = int(nextPct) - int(pct)
                        increment = 1
                        if range > span:
                            increment = float(range) / float(span)
                            
                        calcPct = int(pct) + ((sensor - rangeBottom) / increment)
                        self.logger.debug("range: %d span: %d increment: %f calcPct: %d" \
                                          % (range, span, increment, calcPct))
                        level = "%d%%" % (calcPct)
                        break
                else:
                    if firstThreshold:
                        # Reading is below the lowest
                        level = "< %s%%" % (pct)
                        calcPct = pct
                        break
                firstThreshold = False

            propaneVar = indigo.variables["PropaneLevel"]
            indigo.variable.updateValue(propaneVar, str(calcPct))
            propaneStrVar = indigo.variables["PropaneLevelStr"]
            indigo.variable.updateValue(propaneStrVar, level)

            self.logger.info("Propane level is %s" % level)
					
        def calibratePropaneLevel(self, action):
            props = action.props
            gaugePct = int(props[u'gaugePct'])
            self.readPropaneThresholds()

            testValStr = props[u'testSensorVal']
            testVal = None
            
            if testValStr.isdigit():
                testVal = int(testValStr)

            sensor = None
            if testVal is None:
                sensor = self.getPropaneSensorReading()
            else:
                sensor = testVal

            # Insert the new reading into the list, replacing the
            # cuyrrent pct reading if it already exists
            PropaneThresholds[str(gaugePct)] = sensor
            

            # Now, iterate through the list and remove entries that
            # cross over the new threshold out of order
            toRemove = []
            firstThreshold = True
            for pct, nextPct in self.iterate(sorted(PropaneThresholds.iterkeys(), key=int)):
                thresh = int(PropaneThresholds[pct])

                if int(pct) < gaugePct and thresh > sensor:
                    toRemove.append(pct)
                    self.logger.info("Existing threshold %d for %d%% is higher than new threshold %d, at %d%%, removing existing" \
                                          % (thresh, int(pct), sensor, gaugePct))

                if int(pct) > gaugePct and thresh < sensor:
                    toRemove.append(pct)
                    self.logger.info("Existing threshold %d for %d%% is lower than new threshold %d, at %d%%, removing existing" \
                                          % (thresh, int(pct), sensor, gaugePct))

            for pct in toRemove:
                del PropaneThresholds[pct]

            self.logger.info("After calibration:")
            for item, next_item in self.iterate(sorted(PropaneThresholds.iterkeys(), key=int)):
                prefix = ""
                if int(item) == gaugePct:
                    prefix = "NEW--> "

                self.logger.info("PRP: %s %s(%d)" % (prefix, item, int(PropaneThresholds[item])))

            self.writePropaneThresholds()

        def archivePriorMonthLogs(self):
            
            var = indigo.variables['LogArchiveDir']

            if not var:
                self.logger.error("LogArchiveDir variable not set")
                return

            archiveDir = var.value
        
            var = indigo.variables['LogDir']

            if not var:
                self.logger.error("LogDir variable not set")
                return

            logDir = var.value

            dtNow = datetime.datetime.now()
            dtLastMonth = dtNow + dateutil.relativedelta.relativedelta(months=-1)
     
            # dtMatch = "%4d-%02d.*Events.txt" % (dtLastMonth.year, dtLastMonth.day)

            # files = [f for f in os.listdir(logDir) if re.match(dtMatch, f)]

            # for f in files:
                # self.logger.debug(f)

            yearDir = "%s/%4d" % (archiveDir, dtLastMonth.year)

            self.logger.debug("YearDir=%s" % yearDir)
            if (not os.path.isdir(yearDir)):
                os.mkdir(yearDir)

            tarPath = "%s/%s.tar" % (yearDir, dtLastMonth.strftime("%Y-%b"))
            tarPathGz = "%s.gz" % tarPath

            if (os.path.exists(tarPathGz)):
                self.logger.info("Last month archive already created; no action taken")
                return
            else:
                self.logger.info("Creating last month archive: %s" % tarPath)
            
            tarPath    = tarPath.replace(" ","\ ")
            logDir     = logDir.replace(" ","\ ")

            tarcmd = "cd %s;tar -cvf %s %4d-%02d*" \
                      % (logDir,
                         tarPath,
                         dtLastMonth.year,
                         dtLastMonth.month)

            self.logger.debug(tarcmd)

            rc = subprocess.call(tarcmd, shell=True, stdout=subprocess.PIPE)

            gzcmd = "gzip %s" % tarPath

            rc = subprocess.call(gzcmd, shell=True, stdout=subprocess.PIPE)
                       

