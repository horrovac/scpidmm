#!/usr/bin/env python

import owon
from time import sleep

with ( open('/dev/pts/9', 'rb') as ifle):
	val = 1e-7
	with ( open('/dev/pts/9', 'wb', buffering=0) as ofle):
		line = ifle.readline().decode('utf-8')
		while(True):
			print ( "{:f}".format(val), flush=True )
			line = ifle.readline().decode('utf-8').strip()
			if ( line == "FUNCTION?"):
				ofle.write('VOLT\n'.encode('utf-8'))
			elif ( line == "MEAS?" ):
				msg = "{}\n".format(val).encode('utf-8')
				ofle.write(msg)
			if ( val > 2e3 ):
				val = 1e-7
			if ( val < 50e-2 ):
				val = val + 11e-4
			elif (val < 5):
				val = val + 11e-3
			elif (val < 50):
				val = val + 1
			else:
				val = val +10


mm = owon.DMM()

mm.get()

while ( True ):
	mm.get()
	print (mm.value())
	sleep(0.1)
