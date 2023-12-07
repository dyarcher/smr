import sys
import numpy as np
import numpy.random as nr
	
def genposrectslab(write_mode, xmin, xmax, ymin, ymax, zmin, zmax, species, counts, ofile):
	xwidth = xmax-xmin
	ywidth = ymax-ymin
	zwidth = zmax-zmin
	f = open(ofile, write_mode)
	for i in np.arange(0,len(species)):
		tot = counts[i]
		p = 0
		while p < int(tot):
			posx = ((nr.rand(1,1)-0.5)*2) * xwidth/2
			posy = ((nr.rand(1,1)-0.5)*2) * ywidth/2
			posz = ((nr.rand(1,1)-0.5)*2) * zwidth/2 + (zmax+zmin)/2
			line = "mol 1 " + species[i] + " " + str(posx[0][0]) + " " + str(posy[0][0]) + " " + str(posz[0][0])
			f.write(line)
			f.write("\n")
			p += 1
	f.close()

def gen_config(num_layers, lacs, cfg_idx):
	# parameters
	fname_base = 'config-bdrvfv_base.txt'
	fname_pref = 'rvfv_'
	timestep = '1e-3'
	timestop = '80'
	kpl = '192e4'
	klp = '192e3'
	difcpyr = '11e2'
	difclac = '10e2'
	difcldh = '10e1'
	xlength = 9000
	ylength = 9000
	basez = 15225
	num_lac = lacs # total pyr
	num_pyr = 2560-num_lac # total pyr
	num_ldh_nadh = num_pyr*1 # total ldh/nadh
	num_ldh_nad = num_lac*1 # total ldh/nad

	# filename
	fname = fname_pref + 'd' + difcpyr + '_k' + str(kpl) + '_n' + str(num_layers) + '_' + str(cfg_idx)

	# read in base config
	f = open('../config/'+fname_base,'r')
	fr = f.read()
	f.close()
	fr = fr.replace('OUTPUTFNAME',fname,10).replace('TIMESTOP',timestop,10).replace('TIMESTEP',timestep,10).replace('DIFCPYR12',difcpyr,10).replace('DIFCLAC12',difclac,10).replace('DIFCLDH',difcldh,10).replace('KPLVAL',kpl,10).replace('KLPVAL',klp,10).replace('EPPWIDTHHALF',str(int(xlength/2)),10).replace('EPPWIDTH',str(int(xlength)),10)
	fr = fr.replace('EPPHEIGHT',str(int(basez)),10)

	# write config
	f = open('../config/config-'+fname+'.txt','w')
	f.write(fr)
	f.close()
	# add particles
	genposrectslab('a', -xlength/2, xlength/2, -ylength/2, ylength/2, 0, basez, ['pyr12'],[num_pyr],'../config/config-'+fname+'.txt')
	genposrectslab('a', -xlength/2, xlength/2, -ylength/2, ylength/2, 0, basez, ['lac12'],[num_lac],'../config/config-'+fname+'.txt')
	genposrectslab('a', -xlength/2, xlength/2, -ylength/2, ylength/2, 0, basez, ['ldh_nadh'],[num_ldh_nadh],'../config/config-'+fname+'.txt')
	genposrectslab('a', -xlength/2, xlength/2, -ylength/2, ylength/2, 0, basez, ['ldh_nad'],[num_ldh_nad],'../config/config-'+fname+'.txt')

	# end file
	f = open('../config/config-'+fname+'.txt','a')
	f.write("\nend_file")
	f.close()

	# return fname
	print('start "" smoldyn.exe config/config-'+fname+'.txt')
	return "'lm2-"+fname+"',",fname

# create slurm configs
def write_configs(cfg_layers, lac):
	j = 0
	for a in range(0,1,1):
		j += 1
		gen_config(int(cfg_layers), lac, str(j))
	#print(cfg_layers, lac)

# write configs based on system arguments
cfg_start = int(sys.argv[1])
cfg_end = int(sys.argv[2])+1
cfg_step = int(sys.argv[3])

lacs = [] # input final lactate populations from stage 1
for c in range(cfg_start, cfg_end, cfg_step):
	write_configs(c, lacs[int(c/cfg_step)])