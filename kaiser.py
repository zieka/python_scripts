#!/usr/bin/env python

import scipy.signal
import numpy

a = scipy.signal.firwin(256,0.015625,window=('kaiser', 3.75))

numpy.savetxt("kaiser_result.csv",a,fmt='%3.70f',delimiter=",")

