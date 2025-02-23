#!/usr/bin/env python
# vim: ts=4 sw=4 noexpandtab

DEBUG=False

import serial
import time

class DMM:
	"""Communication with a multimeter"""
	port='/dev/ttyUSB0'
	measurement=0
	function1=""
	function2=0
	meas_range=0
	ac=False
	def __init__(self):
		global ser
		ser=serial.Serial()
		ser.port=self.port
		ser.baudrate=115200
		ser.timeout=1
		ser.open()

	def get(self):
		msg=("MEAS?\n".encode('utf-8'))
		ser.write(msg)
		result=ser.readline().decode('utf-8')
		try:
			[num,exp] = result.split("E")
		except:
			num = result
			exp = 0
		self.measurement=float(num) * pow(10,int(exp))
		#for command in ["MEAS?", "function1?", "range?"]:
		#	msg=(command+"\n").encode('utf-8')
		#	ser.write(msg)
		#	result=ser.readline().decode('utf-8')
		#	print ( "{}".format(result))
		msg=("FUNCTION?\n".encode('utf-8'))
		ser.write(msg)
		function1=ser.readline().decode('utf-8').strip()
		function1=function1.strip('" ')
		self.function1=function1[0:4]
		if ( function1[-2:] == "AC" ):
			self.ac = True
		else:
			self.ac = False
		msg=("FUNCTION2?\n".encode('utf-8'))
		ser.write(msg)
		function2=ser.readline().decode('utf-8')

	def switch_mode(self, mode):
		if ( self.ac == True ):
			msg=("CONF:{}:AC".format((mode.upper())))
		else:
			msg=("CONF:{}:DC".format((mode.upper())))
		ser.write((msg+"\n").encode('utf-8'))
		DEBUG and print ( msg )

#ser.close()

