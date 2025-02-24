#!/usr/bin/env python
# vim: ts=4 sw=4 noexpandtab

DEBUG=True

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
		msg=("FUNCTION?\n".encode('utf-8'))
		ser.write(msg)
		function1=ser.readline().decode('utf-8').strip()
		function1=function1.strip('" ')
		if (function1 == '' ):
			self.function1 = "OFFLINE"
			self.measurement = 0
		else:
			self.function1 = function1
			msg=("MEAS?\n".encode('utf-8'))
			ser.write(msg)
			result=ser.readline().decode('utf-8')
			DEBUG and print("MEAS? result:", result)
			try:
				[num,exp] = result.split("E")
			except:
				try:
					num = float(result.strip("'"))
				except:
					num = 0;
				finally:
					exp = 0
			self.measurement=float(num) * pow(10,int(exp))
		DEBUG and print ( "Function1:", self.function1 )

	def switch_mode(self, mode):
		msg=("CONF:{}".format((mode)))
		ser.write((msg+"\n").encode('utf-8'))
		DEBUG and print ( msg )

#ser.close()

