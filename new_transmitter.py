
# coding: utf-8

# In[5]:

from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as mplib
import thinkdsp
import thinkplot
from array import array
from itertools import chain, repeat


# This function converts a string into a numpy array of bits
# note that it is assumed that each character is 7 bits long here
def string2NPArray(s):
    bits = np.array([])
    for a in bytearray(s, 'ascii'):
        for b in range(0,7):
            bits = np.append(bits,float((a>>(7-b-1))&1))
    return bits

# This function converts a numpy array of bits to a string
# note that it is assumed that each character is 7 bits long here
def NPbits2String(bits):
    S = ""
    for a in np.arange(0, np.ceil(len(bits)/7)):
        tmp = 0
        for k in np.arange(0,7):
            b = bits[a*7+k]
            tmp = tmp + (2**(6-k))*b
        S = S + chr(int(tmp))
    return S

# this function is used to help convert numpy array data into a format
# suitable for writing into a wave file
def convert_to_int16(sig):
    # convert into int16  to write as wave
    sig = (sig/np.max(sig))*(2**14)
    sig = sig.astype('int16')
    return sig
    

# this is a utility function that  finds the start and  end 
# of transmission in the numpy array of samples xf
# The function looks for the first instance where the entries of xf
# go above threshold and returns the index into xf where this happens
# in start_idx
# The function looks for the last instance where the entries of xf
# are above threshold and returns the index into xf where this happens
# in end_idx
# 
# You will probably have to do some trial and error to get the threshold right
# one possibility is to se the threshold equal to some factor of the maximum value
# in the input signal,  e.g. 0.3 * maximum value in xf
#
def find_start_and_end(xf, threshold = 2000): 
    import numpy as np    
    start_idx = -1
 
    for k in range(0, len(xf)):
        if(np.abs(xf[k])) > threshold:
            start_idx = k
            break

    if(start_idx  < 0):
        print "Unable to detect start of transmission"
        return -1
    
    end_idx = -1
    
    for k in range(0, len(xf)):
        if(np.abs(xf[len(xf)-k-1])) > threshold:
            end_idx = len(xf)-k-1
            break

    if(end_idx < 0):
        print "Unable to detect end of transmission"
        return -1

    return start_idx, end_idx

    


# bpsk is a module that is provided as python bytecode. bpsk.help() provides the syntax and definitions of the parameters of the functions that are included in the bpsk module

# The following cell generates a bpsk signal and plays it through the sound card
# Your job will be to make your own function that generates the transmitted signal, i.e. your own version of bpsk.generate_bpsk_signal. Run bpsk.help() to learn about what  bpsk.generate_bpsk_signal does. At a minimum, you should be able to transmit a 5 character word from one computer to another over the air.

# In[6]:


# convert a text string to a numpy array of 1s and 0s
bits = string2NPArray("Tiger")


def convert_to_bipolar_bitstream(bits,symbol_len):
    bipolar = [2*bit-1 for bit in (bits)]
#     extended = [x for item in l for x in repeat(item, symbol_len)]
    extended = list(chain.from_iterable(repeat(e, symbol_len) for e in bipolar))
#     zero_pad = list(repeat(0, symbol_len)).append(1).append(extended).append(list(repeat(0, symbol_len)))
    zero_pad = list(repeat(0, symbol_len)) + list(repeat(1, symbol_len)) + (extended) + list(repeat(0, symbol_len))
    return zero_pad

def generate_bpsk_signal(bits, rate, symbol_len, freq):
    stream = convert_to_bipolar_bitstream(bits,symbol_len)
    ts = np.arange(0, len(stream)*1/float(rate), 1/float(rate))
    sig = stream*np.cos(freq*2*np.pi*ts)
    return sig

# generate a BPSK signal with 8820 samples per second, and 250 sample long symbols, and carrier frequency of 1kHz
rate=8820
stream = convert_to_bipolar_bitstream(bits,250)
ts = np.arange(0, len(stream)*1/float(rate), 1/float(rate))
x = generate_bpsk_signal(bits, rate = 8820, symbol_len = 250, freq = 1000)
rate = 8820
# plot the signal to visualize
# first make a vector to represent the sampling times
# the times range from t = 0 up to the length of the data samples times the sampling period
# ts = np.arange(0, len(stream)*1/float(rate), 1/float(rate))
# plot the signal in the time domain
# you should zoom in to see the BPSK signal
mplib.plot(ts, x)
mplib.show()

###sig1_demod = sig*np.cos(2*np.pi*f1*ts)

# write the wave file for the first signal which is assumed
# to  be in stored in the numpy array x
wavfile.write('AcousticModemTx.wav', 8820, convert_to_int16(x))





# In[7]:

# use thinkdsp tools to play the wave file with the BPSK signal
wave = thinkdsp.read_wave('AcousticModemTx.wav')
wave.normalize()
wave.make_audio()


# In[7]:



