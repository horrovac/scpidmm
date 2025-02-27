#!/usr/bin/env python

import owon
from time import sleep

mm = owon.DMM()

mm.get()

print ( mm.i[mm.function1] )
print (mm.measurement)

mode = owon.Cap(mm, 2, "F")
while ( True ):
	mm.get()
	print (mode)
	sleep(0.1)
