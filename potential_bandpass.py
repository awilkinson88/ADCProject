from __future__ import print_function, division

import thinkdsp
import thinkplot
import math
import numpy

%matplotlib inline

highCutoff = 510

lowCuttoff = 490

wave = thinkdsp.read_wave('recievedfile.wav')

wave.normalize()

wave.make_audio()

wave.plot(high=1000)

for i in range(len(wave.hs)):
  if wave.fs[i] > highCutoff or wave.fs[i] < lowCutoff:
    wave.hs[i] *= 0

wave.plot(high=1000)
