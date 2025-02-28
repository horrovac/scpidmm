# vim: ts=4 sw=4 noexpandtab

DEBUG=True

import serial
import time

class DMM:
	"""Communication with a multimeter"""

	port='/dev/ttyUSB0'
	measurement=0
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
		self.m = {}
		self.m['VOLT'] = Volt(self,0,"VDC")
		self.m['VOLT AC'] = Volt(self,1,"VAC")
		self.m['CURR'] = Curr(self,1,"ADC")
		self.m['CURR AC'] = Curr(self,1,"AAC")
		self.m['RES'] = Res(self,2,"Ω")
		self.m['CONT'] = Cont(self,2,"Ω")
#		'VOLT':		[0,"VDC",0],
#		'VOLT AC':	[1,"VAC",0],
#		'CURR':		[2,"ADC",1],
#		'CURR AC':	[3,"AAC",1],
#		'RES':		[4,"Ω",2],
#		'CONT':		[5,"Ω",2],
#		'DIOD':		[6,"V",2],
#		'CAP':		[7,"F",3],
#		'FREQ':		[8,"Hz",4],
#		'TEMP':		[9,"°C",5],
#		'OFFLINE':	[10,"OFFLINE",-1,lambda:'OFFLINE']
#	self.function1 = "foo"

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
			self.function1 = self.m[function1]
			self.func1 = self.function1
			result = self.query("MEAS?")
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
		return self.func1

	def switch_mode(self, mode):
		msg=("CONF:{}".format((mode)))
		ser.write((msg+"\n").encode('utf-8'))
		DEBUG and print ( msg )

class Function:
	"""class representing current mode of the multimeter"""

	def __init__(self, p, mode, unit):
		self.mode = mode
		self.p=p
		self.unit = unit

	def normalised_value(self):
		meas = self.p.measurement
		if (meas == 1e9):
			retval = None
		elif(meas > 1e6):
			retval = [meas / 1e6, "M"]
		elif(meas > 1e3):
			retval = [meas / 1e3, "k"]
		elif (meas < 1e-9):
			retval = [meas * 1e9, "n"]
		elif (meas < 1e-6 ):
			retval = [meas * 1e6, "µ"]
		elif (meas < 0.1 ):
			retval = [meas * 1e3, "m"]
		else:
			retval = [meas, ""]
		return retval

	def button(self):
		return self.mode

class Volt(Function):
	def __str__(self):
		meas = self.p.measurement
		try:
			[num, prefix] = self.normalised_value()
			if (meas < 1e-3):
				retval = "{:.4f} {}".format(meas, self.unit)
			else:
				retval = "{:.4f} {}{}".format(num, prefix, self.unit)
		except TypeError:
			retval = "OVERLOAD"
		return retval

class Curr(Function):
	def __str__(self):
		meas = self.p.measurement
		try:
			[num, prefix] = self.normalised_value()
			if (meas < 1e-6):
				retval = "{:.2f} µ{}".format(meas, self.unit)
			else:
				retval = "{:.2f} {}{}".format(num, prefix, self.unit)
		except TypeError:
				retval = "OVERLOAD"
		return retval

class Res(Function):
	def __str__(self):
		meas = self.p.measurement
		try:
			[val, prefix] = self.normalised_value()
			if (meas < 1e-3):
				retval = "{:.2f} {}".format(meas, self.unit)
			else:
				retval = "{:.2f} {}{}".format(val, prefix, self.unit)
		except TypeError:
				retval = "OVERLOAD"
		return retval

class Cont(Function):
	def __str__(self):
		meas = self.p.measurement
		try:
			[val, prefix] = self.normalised_value()
			if (meas > 50):
				retval = "OPEN"
			else:
				retval = "{:.1f} {}{}".format(val, prefix, self.unit)
		except TypeError:
				retval = "OPEN"
		return retval
