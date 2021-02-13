#!/usr/bin/env python
from wavebender import *

def violin(amplitude=0.1):
    # simulates a violin playing G.
    return (damped_wave(400.0, amplitude=0.76*amplitude, length=44100 * 5),
            damped_wave(800.0, amplitude=0.44*amplitude, length=44100 * 5),
            damped_wave(1200.0, amplitude=0.32*amplitude, length=44100 * 5),
            damped_wave(3400.0, amplitude=0.16*amplitude, length=44100 * 5),
            damped_wave(600.0, amplitude=1.0*amplitude, length=44100 * 5),
            damped_wave(1000.0, amplitude=0.44*amplitude, length=44100 * 5),
            damped_wave(1600.0, amplitude=0.32*amplitude, length=44100 * 5))

			
def increasing_sine(fz=100):
    # simulates a violin playing G.
	
	rnge = 400.0
	retVal=list()
	retVal.append(sine_wave(fz, amplitude=1.00))
	#retVal.append(sine_wave(120.0, amplitude=1.00))
	#retVal.append(damped_wave(200.0, amplitude=0.76*amplitude, length=44100 * 5))
	#retVal.append(damped_wave(300.0, amplitude=0.76*amplitude, length=44100 * 5))
	#retVal.append(damped_wave(400.0, amplitude=1.0, length=44100 * 5))
	#retVal.append(damped_wave(500.0, amplitude=0.76*amplitude, length=44100 * 5))
	#retVal.append(damped_wave(600.0, amplitude=0.76*amplitude, length=44100 * 5))
	#iterations = int(22000 / range)
	#iterations = 10
	
	#for x in range(1):
#		print(rnge*x)
	#	retVal.append(damped_wave(rnge*x, amplitude, length=(44100 * 5)))
	return tuple(retVal)

#test()
samples = compute_samples((sine_wave(100),1.0), 44100 * 1 * 1)
write_wavefile(stdout, samples, 44100 * 60 * 1, nchannels=1)
samples = compute_samples((sine_wave(200),1.0), 44100 * 1 * 1)
write_wavefile(stdout, samples, 44100 * 60 * 1, nchannels=1)