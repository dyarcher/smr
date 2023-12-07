# Convert SMR data to ISMRMRD format
import sys
import numpy as np

# arguments should be [readout filename] [number of readout lines]
f = open(sys.argv[1],'r')
fl = f.readlines()
f.close()
ro_segments = int(sys.argv[2])

# work arrays
arrs = [l.replace('\n','').split(' ') for l in fl if len(l)>10]
t = [float(a[0]) for a in arrs]
x = [float(a[1]) for a in arrs]
y = [float(a[2]) for a in arrs]
z = [float(a[3]) for a in arrs]

# resize oversampled readout data
adc_segments = []
adc_segment = []
prevgap = 0
i = 0
while i < len(t) and len(adc_segments) < ro_segments:
	if i > 1 and t[i] - t[i-1] > prevgap * 1.2:
		rightsized = []
		wrongsized = []
		redfactor = len(adc_segment)/ro_segments
		j = 0
		k = 1
		while j < len(adc_segment):
			if j >= k*redfactor:
				rightsized.append(np.mean(wrongsized)) #wsmean
				wrongsized = []
				k += 1
			wrongsized.append(adc_segment[j])
			j += 1
		rightsized.append(np.mean(wrongsized)) #wsmean
		adc_segments.append(np.array(rightsized))
		adc_segment = []
	if i > 0:
		prevgap = t[i] - t[i-1]
	adc_segment.append(-x[i] - 1j*y[i])
	i += 1
	
# correct array size
i = ro_segments - len(adc_segments)
while i > 0:
	adc_segments.append(np.zeros(ro_segments))
	i = ro_segments - len(adc_segments)

# store raw k-space data
kdata = np.array(adc_segments, dtype=complex)

# write raw k-space data in ISMRMRD acquisition format
f = open('ismrm-'+sys.argv[1]+'.txt','w')
for arr in kdata:
	for k in arr:
		f.write(str(k.real))
f.close()