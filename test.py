#!/usr/bin/env python

import owon
from time import sleep


mm = owon.DMM()

mm.get()

while ( True ):
	mm.get()
	print (mm.value())
	sleep(0.1)
