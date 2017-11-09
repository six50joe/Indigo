#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################

import indigo

import os
import sys
import logging
#import json, operator
#import csv,codecs,cStringIO
#from lib.csvUnicode import unicodeReader, unicodeWriter, UTF8Recoder
#from lib.strVarTime import prettyDate, strToTime, timeToStr, timeDiff
from collections import defaultdict
#from tabulate import tabulate
#from texttable.texttable import Texttable
from operator import itemgetter
#from ghpu import GitHubPluginUpdater

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
			
	########################################
	def __del__(self):
		indigo.PluginBase.__del__(self)
				
	########################################
	def startup(self):
		self.logger.debug(u"startup called")

		# self.logger.debug(u'Subscribing to incoming Z-wave commands')
		# indigo.zwave.subscribeToIncoming()
		
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

				
		
	########################################
	# UI List generators and callbackmethods
	########################################
	########################################
	# Actions
	########################################

	def pingOtherHouse(self, action):
#		self.extDebug(u'CALL resetTriggerBatteryLevel')
#		self.extDebug(u'action: %s' % unicode(action))
		
		props = action.props
                self.logger.debug("HEEERE")
                self.loger.info(str(props))
				
#		try:
#			trigger = indigo.triggers[int(props[u'trigger'])]
#		except:
#			self.logger.error(u'Reset trigger battery level: Could not get selected trigger from Indigo')
#			return False
					
