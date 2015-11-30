
# coding: utf-8

# In[5]:

from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as mplib
import thinkdsp
from array import array


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



def record_from_mic_windows(duration = 10, filename = 'AcousticModemRx.wav'):

    import subprocess
    import time
    cmd = "SoundRecorder /FILE %s /DURATION 0000:00:%2d" % (filename, duration)
    print subprocess.check_output(cmd, shell=True)

    # wait for the recording to complete
    time.sleep(duration+2)
  
    # because soundrecorder in windows cannot set the sample rate 
    # we have to manually resample here

    # read the wave file into sig      
    fs, sig = wavfile.read(filename)
    
    
    # if fs not 44100, return an error
    if (fs != 44100):
        print "Sample rate must be 44100. Found it to be %d" % fs
        print "Please change it in Windows Control Panel -> Sound -> Recording -> Microphone -> Advanced"
        return
    
    # discard one of the stereo channels
    sig = sig[:,0]
    
    # make a lowpass filter with cutoff 4410
    # this is going to be our anti-aliasing filter
    ts = np.arange(0, len(sig)/float(fs), 1/float(fs))
    filt = np.sinc(np.arange(-64/float(fs), 64/float(fs), 1/float(fs))/np.pi * 4410.0*2*np.pi)
    
    # lowpass filter the signal to avoid inadvertent aliasing
    sig_down = np.convolve(filt, sig)
    
    # Downsample by 5 to go from 44100 -> 8820Hz
    sig_down = sig_down[0:len(sig_down): 5]
     
    return (8820, sig_down)



def record_from_mic_linux(duration = 10, filename = 'AcousticModemRx.wav', rate = 8820):
    import subprocess
    import time
    
    # call arecord
    cmd = "arecord -d %d -r %d %s" %(duration, rate, filename)   
    subprocess.check_output(cmd, shell=True)
    # wait for the recording to complete
    time.sleep(duration+2)
    fs, x = wavfile.read(filename)
    return (fs,x)


# You should first generate a BPSK transmitted signal on a different computer using AcousticModemTransmitter-NoPyAudio
# Before you hit play the audio signal on that computer, you should start recording the microphone input on your receiver computer (i.e. this one).  This will ensure that you do not miss the beginning of the transmission. 
# 
# You can record the audio signal using an audio recording program such as audacity (windows/linux), or arecord(linux if you have ALSA) and save it to AcousticModemRx.wav You should use 16bit-PCM data, a sample rate of 8820Hz and mono to make the recording. If you are running on windows, you can use record_from_mic_windows defined above.
# 
# In Linux if you have ALSA installed, you can run arecord AcousticModemRx.wav to record and hit control-C to stop recording. 

# In the following cell, the received BPSK audio signal is processed to decode the message. It is assumed that the audio signal is stored in AcousticModemRx.wav
# 
# The BPSK bits are decoded using decode_bpsk_signal from the bpsk module. 
# 
# Your job is to design your own version of the  transmitter and decode_bpsk_signal. 
# 
# You will likely have to tweak the detection_threshold_factor here to make it work reliably for your set of computers/physical environment.

# In[6]:

fs, x = wavfile.read('MadAnnetest3.wav')
ts = np.arange(0, float(len(x))/float(fs), 1.0/fs)
mplib.plot(ts,x)
mplib.show()


# In[7]:

# if you are running on windows, you can uncomment this line to record from the mic for 10s
# using windows soundrecorder. Make sure that windows soundrecorder is not already running
# and set the sample rate in Control Panel -> Sound -> Recording -> Microphone -> Advanced
# to 44100
# you can then comment out the subsequent line 

# fs, x = record_from_mic_windows(duration = 10, filename = 'AcousticModemRx.wav')
def sig_to_bits(demodsig,symbol_len,threshold):
    res = []
    for i in range(125,len(demodsig),symbol_len):
        if demodsig[i] > threshold:
            res.append(1)
        elif demodsig[i] < -threshold:
            res.append(0)
        else:
            res.append(3)
    print res
    if res[0] == 0:
        array =[1-x for x in res]
    else:
        array = res
    return array[1:len(array)]


def decode_bpsk_signal(x,freq, rate , symbol_len, detection_threshold_factor, LPFbw, phase):
    fs = rate
    threshold = detection_threshold_factor
    Wc = LPFbw
    start_idx, end_idx = find_start_and_end(x, threshold)
    # create a vector of the sampling times
    ts = np.arange(0, float(len(x))/float(fs), 1.0/fs)

    # create a vector of frequencies
    freqs = np.linspace(-np.pi*fs, np.pi*fs*(float(len(x))-1)/float(len(x)), len(x))
    f1 = 1000
    Wc = 500
    # this is a vector of the sampling times for the signal
    ts = np.arange(0, len(x)*1/float(fs), 1/float(fs))
    # make a new vector of sampling times for the low-pass filter
    # it doesn't need to be as long as the signal vector as most
    # of the energy of the sinc function is concentrated around zero
    ts_filt = np.arange(-64*1/float(fs),63*1/float(fs),1/float(fs))
    filt = np.sinc(ts_filt/np.pi*Wc*2*np.pi)

    sig1_demod = x*np.cos(2*np.pi*f1*ts+phase)
    mplib.plot(ts,sig1_demod)
    mplib.show()
    sig1_demod = np.convolve(sig1_demod, filt)
    sym_time = rate/sym_length
    start_idx, end_idx = find_start_and_end(sig1_demod, threshold)
    chopped_demod = sig1_demod[start_idx:end_idx]
    print start_idx, end_idx
    array = np.array(sig_to_bits(chopped_demod,symbol_len,threshold))
    Word = NPbits2String(array)
    return Word


#record_from_mic_linux(duration = 10, filename = 'AcousticModemRxTest.wav', rate = 8820)


rate, x = wavfile.read('MadAnnetest3.wav')

phase = np.pi/2
freq = 1000
symbol_len = 250
sym_length = 250
detection_threshold_factor = 200
LPFbw=500
print decode_bpsk_signal(x,freq, rate, symbol_len, detection_threshold_factor, LPFbw, phase)


# In[7]:




# In[7]:



