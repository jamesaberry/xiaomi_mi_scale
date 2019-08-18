#############################################################################################
# Code to read weight measurements fom Xiaomi Scale V1
# Must be executed with Python 3 else body measurements are incorrect.
# Must be executed as root, therefore best to schedule via crontab every 5 min (so as not to drain the battery):
# */5 * * * * python3 /path-to-script/Xiaomi_Scale.py
# Multi user possible as long as weitghs do not overlap, see lines 117-131
#
# Thanks to @lolouk44 (https://github.com/lolouk44/xiaomi_mi_scale) from which this project is forked.
# Thanks to @syssi (https://gist.github.com/syssi/4108a54877406dc231d95514e538bde9) and @prototux (https://github.com/wiecosystem/Bluetooth) for their initial code
#
#############################################################################################

#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import binascii
import time
import os
import sys
from pymongo import MongoClient
from bluepy import btle
from datetime import datetime

import Xiaomi_Scale_Body_Metrics

MISCALE_MAC = 'REDACTED'

class ScanProcessor():

	def GetAge(self, d1):
		d1 = datetime.strptime(d1, "%Y-%m-%d")
		d2 = datetime.strptime(datetime.today().strftime('%Y-%m-%d'),'%Y-%m-%d')
		return abs((d2 - d1).days)/365

	def __init__(self):
		self.connected = False

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if dev.addr == MISCALE_MAC.lower() and isNewDev:
			for (sdid, desc, data) in dev.getScanData():
				### Xiaomi V1 Scale ###
				if data.startswith('1d18') and sdid == 22:
					measunit = data[4:6]
					measured = int((data[8:10] + data[6:8]), 16) * 0.01
					unit = ''
					if measunit.startswith(('03', 'a3')): unit = 'lbs'
					if measunit.startswith(('12', 'b2')): unit = 'jin'
					if measunit.startswith(('22', 'a2')): unit = 'kg' ; measured = measured / 2

					if unit:
						self._publish(round(measured, 2), unit, "", "")
					else:
						print("Scale is sleeping.")

				### Xiaomi V2 Scale ###
				if data.startswith('1b18') and sdid == 22:
					measunit = data[4:6]
					measured = int((data[28:30] + data[26:28]), 16) * 0.01
					unit = ''

					if measunit == "03": unit = 'lbs'
					if measunit == "02": unit = 'kg' ; measured = measured / 2
					mitdatetime = datetime.strptime(str(int((data[10:12] + data[8:10]), 16)) + " " + str(int((data[12:14]), 16)) +" "+ str(int((data[14:16]), 16)) +" "+ str(int((data[16:18]), 16)) +" "+ str(int((data[18:20]), 16)) +" "+ str(int((data[20:22]), 16)), "%Y %m %d %H %M %S")
					miimpedance = str(int((data[24:26] + data[22:24]), 16))

					if unit:
						self._publish(round(measured, 2), unit, str(mitdatetime), miimpedance)
					else:
						print("Scale is sleeping.")


			if not dev.scanData:
				print ('\t(no data)')
			print

	def _publish(self, weight, unit, mitdatetime, miimpedance):
		user="JohnDoe"
		height=175
		age=self.GetAge("1900-01-01")
		sex="male"

		lib = Xiaomi_Scale_Body_Metrics.bodyMetrics(weight, height, age, sex, 0)
		message  = {}
		message['user'] = user
		message['weight'] = "{:.2f}".format(weight)
		message['bmi'] = "{:.2f}".format(lib.getBMI())
		message['basal_metabolism'] = "{:.2f}".format(lib.getBMR())
		message['visceral_fat'] = "{:.2f}".format(lib.getVisceralFat())

		if miimpedance:
			lib = Xiaomi_Scale_Body_Metrics.bodyMetrics(weight, height, age, sex, int(miimpedance))
			message += ',"Lean Body Mass":"' + "{:.2f}".format(lib.getLBMCoefficient()) + '"'
			message += ',"Body Fat":"' + "{:.2f}".format(lib.getFatPercentage()) + '"'
			message += ',"Water":"' + "{:.2f}".format(lib.getWaterPercentage()) + '"'
			message += ',"Bone Mass":"' + "{:.2f}".format(lib.getBoneMass()) + '"'
			message += ',"Muscle Mass":"' + "{:.2f}".format(lib.getMuscleMass()) + '"'
			message += ',"Protein":"' + "{:.2f}".format(lib.getProteinPercentage()) + '"'

		print('JSON: %s' % (message))
		self._mongo(message, mitdatetime)

	def _mongo(self, message, mitdatetime):

		# Connect to Mongo
		client = MongoClient('mongodb://localhost:27017')
		db = client.scale_data
		scale_data = db.scale_data

		# Look for scale data that matches existing.
		duplicate_readings = scale_data.find(message)

		# Check if returned data matches within two days
		# Only add new entry if data or day doesnt match
		last_entry_today = False
		for reading in duplicate_readings:
			tdiff = datetime.now().timestamp() - float(reading['timestamp'])
			if ( tdiff < 172800 ):
				last_entry_today = True

		# Only insert if not duplicated in last 48 hours
		if not last_entry_today:
			if mitdatetime:
				message['timestamp'] = mitdatetime
			else:
				message['timestamp'] = str(datetime.now().timestamp())

			scale_data.insert_one(message)

def main():

	# while(True):
	scanner = btle.Scanner().withDelegate(ScanProcessor())

	devices = scanner.scan(5)

if __name__ == "__main__":
	main()
