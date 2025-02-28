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
		self.m['VOLT AC'] = Volt(self,0,"VAC")
		self.m['CURR'] = Curr(self,1,"ADC")
		self.m['CURR AC'] = Curr(self,1,"AAC")
		self.m['RES'] = Res(self,2,"Ω")
		self.m['CONT'] = Cont(self,2,"Ω")
		self.m['DIOD'] = Diod(self,2,"V")
		self.m['CAP'] = Cap(self,3,"F")
		self.m['FREQ'] = Freq(self,4,"Hz")
		self.m['TEMP'] = Temp(self,5,"°C")
		self.m['OFFLINE'] = Function(self,-1,"")
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
#	self.func = "foo"

	def query(self, query):
		ser.reset_input_buffer()
		msg="{}\n".format(query).encode('utf-8')
		ser.write(msg)
		answer=ser.readline().decode('utf-8').strip()
		answer=answer.strip('\"')
		return answer

	def get(self):
		self.func_name=self.query('FUNCTION?')
		try:
			self.func = self.m[self.func_name]
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
		except KeyError:
			self.func = self.m['OFFLINE']
			self.measurement = 0
	
	def value(self):
		return self.func

	def name(self):
		return self.func_name

	def switch_mode(self, button):
		msg=("CONF:{}".format((button)))
		ser.write((msg+"\n").encode('utf-8'))
		DEBUG and print ( msg )

class Function:
	"""class representing current button of the multimeter"""

	def __init__(self, p, btn, unit):
		self.btn = btn
		self.p=p
		self.unit = unit
		self.retval = "overload"

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
		return self.btn

class Volt(Function):
	def __str__(self):
		meas = self.p.measurement
		resp = self.normalised_value()
		if ( resp != None ):
			[num, prefix] = resp
			if (meas < 1e-3):
				self.retval = "{:.4f} {}".format(meas, self.unit)
			else:
				self.retval = "{:.4f} {}{}".format(num, prefix, self.unit)
		return self.retval

class Curr(Function):
	def __str__(self):
		meas = self.p.measurement
		resp = self.normalised_value()
		if ( resp != None ):
			[num, prefix] = resp
			if (meas < 1e-6):
				self.retval = "{:.2f} µ{}".format(meas, self.unit)
			else:
				self.retval = "{:.2f} {}{}".format(num, prefix, self.unit)
		return self.retval

class Res(Function):
	def __str__(self):
		meas = self.p.measurement
		resp = self.normalised_value()
		if ( resp != None ):
			[num, prefix] = resp
			if (meas < 1e-3):
				self.retval = "{:.2f} {}".format(meas, self.unit)
			else:
				self.retval = "{:.2f} {}{}".format(num, prefix, self.unit)
				print (retval)
		return self.retval

class Cont(Function):
	def __str__(self):
		self.retval = "OPEN"
		meas = self.p.measurement
		resp = self.normalised_value()
		if (resp != None):
			[val, prefix] = resp
			if (meas > 50):
				self.retval = "OPEN"
			else:
				self.retval = "{:.1f} {}{}".format(val, prefix, self.unit)
		return self.retval

class Diod(Function):
	def __str__(self):
		meas = self.p.measurement
		resp = self.normalised_value()
		if (resp != None):
			[val, prefix] = resp
			if (meas > 0.5):
				self.retval = "OPEN"
			else:
				self.retval = "{:.1f} {}{}".format(val, prefix, self.unit)
		return self.retval

class Cap(Function):
	def __str__(self):
		meas = self.p.measurement
		resp = self.normalised_value()
		if (resp != None):
			[val, prefix] = resp
			if (meas > 0.5):
				self.retval = "OPEN"
			else:
				self.retval = "{:.1f} {}{}".format(val, prefix, self.unit)
		return self.retval

class Freq(Function):
	def __str__(self):
		meas = self.p.measurement
		resp = self.normalised_value()
		if (resp != None):
			[val, prefix] = resp
			if (meas < 1e-4):
				self.retval = "{:.4f} {}".format(meas, self.unit)
			else:
				self.retval = "{:.4f} {}{}".format(val, prefix, self.unit)
		return self.retval

class Temp(Function):
	def __str__(self):
		meas = self.p.measurement
		retval = "{:.1f} {}".format(meas, self.unit)
		return retval
