# vim: ts=4 sw=4 noexpandtab

DEBUG=True

import serial
import time

class DMM:
	"""Communication with a multimeter"""

    # NAME:[button_index, "display unit", index]
	global m
	m = {
		'VOLT':		[0,"VDC",0],
		'VOLT AC':	[1,"VAC",0],
		'CURR':		[2,"ADC",1],
		'CURR AC':	[3,"AAC",1],
		'RES':		[4,"Ω",2],
		'CONT':		[5,"Ω",2],
		'DIOD':		[6,"V",2],
		'CAP':		[7,"F",3],
		'FREQ':		[8,"Hz",4],
		'TEMP':		[9,"°C",5],
		'OFFLINE':	[10,"OFFLINE",-1,lambda:'OFFLINE']
	}
	i=list(m.keys())

	port='/dev/ttyUSB0'
	measurement=0
	global function1
	function2=0
	meas_range=0

	def __init__(self):
		global ser
		ser=serial.Serial()
		ser.port=self.port
		ser.baudrate=115200
		ser.timeout=1
		ser.open()
		self.idn=self.query('*IDN?')
		self.function1 = 0

	def query(self, query):
		msg="{}\n".format(query).encode('utf-8')
		ser.write(msg)
		answer=ser.readline().decode('utf-8').strip()
		answer=answer.strip('\"')
		return answer

	def get(self):
		function1=self.query('FUNCTION?')
		if (function1 == '' ):
			self.function1 = m['OFFLINE'][0]
			self.measurement = 0
		else:
			self.function1 = m[function1][0]
			msg=("MEAS?\n".encode('utf-8'))
			ser.write(msg)
			result=ser.readline().decode('utf-8')
			print ( result )	
			try:
				[num,exp] = result.split("E")
			except:
				try:
					num = result.strip("'")
				except:
					num = 0;
				finally:
					exp = 0
			self.measurement=float(num) * pow(10,int(exp))
	
	def value(self):
		return m[self.i[self.function1]][3]()
		measurement = self.measurement
		function1 = self.function1
		if (function1 == m['OFFLINE'][0] ):
			return 'OFFLINE'

		if (measurement < 0.0000001 ):
			retval = "{:06.2f} {}".format(measurement * 1e9, "n")
		elif (measurement < 0.0001 ):
			retval = "{:06.3f} {}".format(measurement * 1000000, "µ")
		elif (measurement < 0.1 ):
			retval = "{:06.3f} {}".format(measurement * 1000, "m")
		return retval

	def switch_mode(self, mode):
		msg=("CONF:{}".format((mode)))
		ser.write((msg+"\n").encode('utf-8'))
		DEBUG and print ( msg )

class Mode:
	"""class representing current mode of the multimeter"""

	def __init__(self, p, mode, unit):
		self.mode = mode
		self.p=p
		self.unit = unit

class Cap(Mode):

	def __str__(self):
		meas = self.p.measurement
		print ( meas )
		if ( meas < 0 ):
			meas = 0
		#return "{:07.4f} {}".format(meas, self.unit)
		return self.unit


