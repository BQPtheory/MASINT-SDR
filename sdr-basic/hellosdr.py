import SoapySDR
from SoapySDR import * #SOAPY_SDR_ constants
import numpy #use numpy for buffers
import pycuda
import numpy as np

import sys
print(sys.path)

#enumerate devices
# results = SoapySDR.Device.enumerate()
# for result in results: print(result)

#create device instance
#args can be user defined or from the enumeration result
args = dict(driver="lime")
sdr = SoapySDR.Device(args)

#query device info
print(sdr.listAntennas(SOAPY_SDR_RX, 0))
print(sdr.listGains(SOAPY_SDR_RX, 0))
freqs = sdr.getFrequencyRange(SOAPY_SDR_RX, 0)
for freqRange in freqs: print(freqRange)

# #apply settings
# sdr.setSampleRate(SOAPY_SDR_RX, 0, 5e6)
# sdr.setFrequency(SOAPY_SDR_RX, 0, 912.3e6)

# #setup a stream (complex floats)
# rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
# sdr.activateStream(rxStream) #start streaming

fc = 104.0e6
fs = 5e6
bandwidth = fs

sdr.setAntenna(SOAPY_SDR_RX, 0, 'LNAL')
sdr.setFrequency(SOAPY_SDR_RX, 0, fc)
sdr.setSampleRate(SOAPY_SDR_RX, 0, fs)
sdr.setBandwidth(SOAPY_SDR_RX, 0, bandwidth)
sdr.setDCOffsetMode(SOAPY_SDR_RX, 0, True)

if sdr.hasGainMode(SOAPY_SDR_RX, 0):
    sdr.setGainMode(SOAPY_SDR_RX, 0, False)

gains = {"LNA": 30, "TIA": 0, "PGA": -12}
for gain, value in gains.items():
    sdr.setGain(SOAPY_SDR_RX, 0, gain, value)

rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)#SOAPY_SDR_CS16)
sdr.activateStream(rx_stream)


#create a re-usable buffer for rx samples
# buff = numpy.array([0]*1024, numpy.complex64)
packet_size = 1024
nsamples = 100
rx_buff = np.empty(shape=(nsamples, packet_size), dtype=np.complex64)

#receive some samples
for i in range(nsamples):
    sr = sdr.readStream(rx_stream, [rx_buff[i]], packet_size)
    if sr.ret != packet_size:
        print(sr.ret)
        print('Bad samples from remote!')
    # print("Samples", sr.ret) #num samples or error code
    # print(sr.flags) #flags set by receive operation
    print("Timestamp: %f ns" % sr.timeNs) #timestamp for receive buffer

# print(len(rx_buff), len(rx_buff[0]))

# with open("iq_data.txt", "w") as fo:
# 	fo.write("frequency=%2.2f\n" % fc)
# 	fo.write("sample_rate=%2.2f\n" % fs)
# 	fo.write("bandwidth=%2.2f\n" % bandwidth)
# 	fo.write("\n")
# 	for i in range(nsamples):
# 		for j in range(packet_size):
# 			fo.write("%f,%f " % (rx_buff[i][j].real, rx_buff[i][j].imag))
	

#shutdown the stream
sdr.deactivateStream(rx_stream) #stop streaming
sdr.closeStream(rx_stream)