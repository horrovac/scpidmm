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
		self.m['VOLT'] =			Volt(self,0,"VDC")
		self.m['VOLT AC'] =		VoltAC(self,0,"VAC")
		self.m['CURR'] =			Curr(self,1,"ADC")
		self.m['CURR AC'] =		Curr(self,1,"AAC")
		self.m['RES'] =				Res(self,2,"Ω")
		self.m['CONT'] =			Cont(self,2,"Ω")
		self.m['DIOD'] =			Diod(self,2,"VDC")
		self.m['CAP'] =				Cap(self,3,"F")
		self.m['FREQ'] =			Freq(self,4,"Hz")
		self.m['TEMP'] =			Temp(self,5,"°C")
		self.m['OFFLINE'] =		Function(self,-1,"",None)

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
		self.p.range=self.p.query('RANGE?')
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
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		self.rng = {
			'AUTO':		lambda a,b : self.retval,
			'500 Ω':	lambda a,b : "{:06.2f} {}".format(a, b) if a < 5e2 else None,
			'5 KΩ':		lambda a,b : "{:06.4f} k{}".format(a * 1e-3, b) if a < 5e3 else None,
			'50 KΩ':	lambda a,b : "{:06.3f} k{}".format(a * 1e-3, b) if a < 5e4 else None,
			'500 KΩ':	lambda a,b : "{:06.2f} k{}".format(a * 1e-3, b) if a < 5e5 else None,
			'5 MΩ':		lambda a,b : "{:06.4f} M{}".format(a * 1e-6, b) if a < 5e6 else None,
			'50 MΩ':	lambda a,b : "{:06.3f} M{}".format(a * 1e-6, b) if a < 5e7 else None
			}

class Cont(Function):
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		self.thresh = 50
		self.retval = "    open    "

	def __str__(self):
		meas = self.p.measurement
		if ( meas < self.thresh ):
			return "{:06.1f} {}".format(meas, self.unit)
		return self.retval

class Diod(Function):
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		self.thresh = 0.5
		self.retval = "    open    "

	def __str__(self):
		meas = self.p.measurement
		if ( meas < self.thresh ):
			return "{:06.4f} {}".format(meas, self.unit)
		return self.retval

class Cap(Function):
	def __init__(self, p, btn, unit):
		super().__init__(p, btn, unit)
		self.rng = {
			'AUTO':		lambda a,b : self.retval,
			'50 nF':	lambda a,b : "{:05.2f} n{}".format(a * 1e9, b) if a < 5e-8 else None,
			'500 nF':	lambda a,b : "{:05.1f} n{}".format(a * 1e9, b) if a < 5e-7 else None,
			'5uF':		lambda a,b : "{:05.3f} µ{}".format(a * 1e6, b) if a < 5e-6 else None,
			'50uF':	lambda a,b : "{:05.2f} µ{}".format(a * 1e6, b) if a < 5e-5 else None,
			'500uF':	lambda a,b : "{:05.1f} µ{}".format(a * 1e6, b) if a < 5e-4 else None,
			'5 mF': 	lambda a,b : "{:05.3f} m{}".format(a * 1e3, b) if a < 5e-3 else None,
			'50 mF': 	lambda a,b : "{:05.2f} m{}".format(a * 1e3, b) if a < 5e-2 else None
			}

class Freq(Function):
	def __str__(self):
		meas = self.p.measurement
		return "{:06.4f} {}".format(meas, self.unit)

class Temp(Function):
	def __str__(self):
		meas = self.p.measurement
		return  "{:.1f} {}".format(meas, self.unit)
