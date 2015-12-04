from __future__ import print_function, division

import thinkdsp
import thinkplot
import math
import numpy

%matplotlib inline

zeroHighCutoff = 510

zeroLowCuttoff = 490

wave = thinkdsp.read_wave('receivedfile.wav')

wave.normalize()

wave.make_audio()

windowSize = 0.5

results = [];

for i in range(0, math.round(wave.duration / windowSize)):
    segment = wave.segment(i * windowSize, windowSize)
    segmentSpectrum = segment.make_spectrum()
    segmentSpectrum.low_pass(510)
    segmentSpectrum.high_pass(490)
    segmentSpectrum.apodize()
    if segementSpectrum[500] > .1:
        results[i] = 1

print(results)
