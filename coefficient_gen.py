#!/usr/bin/env python

import sys
import scipy.signal
import numpy
from numpy import binary_repr

try:
	t=sys.argv[1]
except IndexError:
	print("missing argument for out_to_in_ration")
	sys.exit()

try:
	float(sys.argv[1])
except ValueError:	
	print("Argument should be float")
	sys.exit()

out_to_in_ratio = float(sys.argv[1])

phases = 64
taps = 4
number_of_fractional_bits = 14 #16-bit coefficients have 14 fractional bits
filter_cutoff = out_to_in_ratio/phases 

array = scipy.signal.firwin((phases*taps),filter_cutoff,window=('kaiser',3.75))

fir_taps = numpy.zeros((phases,taps))
for x in xrange(0,taps):
	for y in xrange(0,phases):	
		fir_taps[y,x] = array[(phases*x)+y]

gain_corrected_coefficients = numpy.zeros((phases,taps))
gain_corrected_coefficients = fir_taps*phases

coefficient_sums_before_gain_equalization = numpy.zeros(phases)
for m in xrange(0,phases):	
	coefficient_sums_before_gain_equalization[m] = gain_corrected_coefficients[m,0]+gain_corrected_coefficients[m,1]+gain_corrected_coefficients[m,2]+gain_corrected_coefficients[m,3]

unity_sum_coefficients = numpy.zeros((phases,taps))
for x in xrange(0,taps):
	for y in xrange(0,phases):	
		unity_sum_coefficients[y,x] = gain_corrected_coefficients[y,x]/coefficient_sums_before_gain_equalization[y]


#coefficient_sums_after_gain_equalization = numpy.zeros(phases)
#for m in xrange(0,phases):	
#	coefficient_sums_after_gain_equalization[m] = unity_sum_coefficients[m,0]+unity_sum_coefficients[m,1]+unity_sum_coefficients[m,2]+unity_sum_coefficients[m,3]

shifted_real_coefficients = numpy.zeros((phases,taps))
shifted_real_coefficients = unity_sum_coefficients*(2**(number_of_fractional_bits))

rounded_coefficients = numpy.rint(shifted_real_coefficients)

rounded_coefficient_sums = numpy.zeros(phases)
for m in xrange(0,phases):	
	rounded_coefficient_sums[m] = rounded_coefficients[m,0]+rounded_coefficients[m,1]+rounded_coefficients[m,2]+rounded_coefficients[m,3]


rounded_coefficient_error_per_phase = numpy.zeros(phases)
for m in xrange(0,phases):	
	rounded_coefficient_error_per_phase[m] = rounded_coefficient_sums[m]-(2**(number_of_fractional_bits))

fpga_coefficients_bin = numpy.zeros((phases,taps))
fpga_coefficients_int = numpy.zeros((phases,taps))

for x in xrange(0,taps):
	for y in xrange(0,phases):	
		fpga_coefficients_bin[y,x] = binary_repr(int(rounded_coefficients[y,x]), width=16)
		fpga_coefficients_int[y,x] = int(rounded_coefficients[y,x])

for y in xrange(0,(phases/2)):	
		fpga_coefficients_bin[y,1] = binary_repr(int(rounded_coefficients[y,1]-rounded_coefficient_error_per_phase[y]), width=16)
		fpga_coefficients_int[y,1] = int(rounded_coefficients[y,1]-rounded_coefficient_error_per_phase[y])

for z in xrange(0,(phases/2)):	
		fpga_coefficients_bin[z+(phases/2),2] = binary_repr(int(rounded_coefficients[z+(phases/2),2]-rounded_coefficient_error_per_phase[z+(phases/2)]), width=16)
		fpga_coefficients_int[z+(phases/2),2] = int(rounded_coefficients[z+(phases/2),2]-rounded_coefficient_error_per_phase[z+(phases/2)])


filename1 = "coefficients_binary_"
filename1+= str(out_to_in_ratio)
filename1+= str(".txt")

filename2 = "coefficients_integer_"
filename2+= str(out_to_in_ratio)
filename2+= str(".txt")

filename3 = "coefficients_vhdl_formatted_"
filename3+= str(out_to_in_ratio)
filename3+= str(".txt")

numpy.savetxt(filename1,fpga_coefficients_bin,fmt='%016d',delimiter='')
numpy.savetxt(filename2,fpga_coefficients_int,fmt='%1.0f',delimiter=',')

first_file = open(filename1, "r" )
second_file = open(filename3, "w")

for line in first_file:
	s = ""
	s+=str("     rom_word'(")
	s+=str('"')
	s+=str( line.rstrip('\n') )
	s+=str( '"),\n')
	second_file.write( s )

first_file.close()
second_file.close()

