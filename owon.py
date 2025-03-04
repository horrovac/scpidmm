# vim: tabstop=2 shiftwidth=2 smartindent noexpandtab

DEBUG=False

import serial
import time

class DMM:
	"""Communication with a multimeter"""

	port='/dev/ttyUSB1'
	#port = '/dev/pts/10'
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
		self.m['VOLT'] =	Volt(self,0,"VDC")
		self.m['VOLT AC'] =	VoltAC(self,0,"VAC")
		self.m['CURR'] =	Curr(self,1,"ADC")
		self.m['CURR AC'] =	Function(self,1,"AAC")
		self.m['RES'] =		Function(self,2,"Ω")
		self.m['CONT'] =	Function(self,2,"Ω","OPEN")
		self.m['DIOD'] =	Function(self,2,"VDC","OPEN")
		self.m['CAP'] =		Function(self,3,"F")
		self.m['FREQ'] =	Function(self,4,"Hz")
		self.m['TEMP'] =	Function(self,5,"°C")
		self.m['OFFLINE'] =	Function(self,-1,"",None)

	def query(self, query):
		ser.reset_input_buffer()
		msg="{}\n".format(query).encode('utf-8')
		ser.write(msg)
		answer=ser.readline().decode('utf-8').strip()
		answer=answer.strip('\"')
		return answer

	def get(self):
		self.func_name=self.query('FUNCTION?') 
		self.range=self.query('RANGE?')
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
	"""class representing current function of the multimeter"""

	def __init__(self, p, btn, unit, msg = "    0L.     "):
		self.btn = btn
		self.p=p
		self.unit = unit
		self.retval = msg
		self.range = 'AUTO'

	def normalised_value(self):
		meas = self.p.measurement
		if (meas == 1e9): # 1e9 is always overload
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

	def __str__(self):
		meas = self.p.measurement
		retval = self.rng[self.p.range](meas, self.unit)
		if ( retval == None ):
			retval = self.retval
		return retval

class Volt(Function):
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		self.rng = {
			'AUTO':		lambda a,b : self.retval,
			'50 mV':	lambda a,b : "{:07.3f} m{}".format(a * 1e3, b) if a < 5e-2 else None,
			'500 mV':	lambda a,b : "{:06.2f} m{}".format(a * 1e3, b) if a < 5e-1 else None,
			'5 V':		lambda a,b : "{:07.4f}  {}".format(a, b) if a < 5 else None,
			'50 V':		lambda a,b : "{:07.3f}  {}".format(a, b) if a < 50 else None,
			'500 V':	lambda a,b : "{:07.2f}  {}".format(a, b) if a < 500 else None,
			'1000 V':	lambda a,b : "{:07.1f}  {}".format(a, b) if a < 1000 else None
			}

class VoltAC(Volt):
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		del(self.rng['50 mV'])
		del(self.rng['1000 V'])
		self.rng['750 V'] =	lambda a,b : "{:07.1f}  {}".format(a, b) if a < 750 else None

class Curr(Function):
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		self.rng = {
			'AUTO':		lambda a,b : self.retval,
			'500 uA':	lambda a,b : "{:07.2f} µ{}".format(a * 1e6, b) if a < 5e-4 else None,
			'5 mA':		lambda a,b : "{: 7.4f} m{}".format(a * 1e3, b) if a < 5e-3 else None,
			'50 mA':	lambda a,b : "{:07.3f}  {}".format(a * 1e3, b) if a < 5e-2 else None,
			'500 mA':	lambda a,b : "{:07.2f}  {}".format(a * 1e3, b) if a < 5e-1 else None,
			'5 A':		lambda a,b : "{:07.4f}  {}".format(a, b) if a < 5 else None,
			'10 A':		lambda a,b : "{:07.3f}  {}".format(a, b) if a < 10 else None
			}

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
