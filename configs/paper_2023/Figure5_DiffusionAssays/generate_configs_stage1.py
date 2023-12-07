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

def genpospackedspheres(write_mode, layeri, sphcens, xmin, xmax, ymin, ymax, zmin, zmax, sph_rad, species, counts, ofile):
	excluded_sph = []+sphcens[layeri]
	if layeri > 0:
		excluded_sph += sphcens[layeri-1]
	if layeri < len(sphcens)-1:
		excluded_sph += sphcens[layeri+1]
	particles_placed = 0
	f = open(ofile, write_mode)
	for i in np.arange(0,len(species)):
		tot = int(counts[i])
		n = 0
		while n < tot:
			posfound = False
			posx = 0
			posy = 0
			posz = 0
			while not posfound:
				posx = nr.rand(1,1)[0][0] * (xmax-xmin) + xmin
				posy = nr.rand(1,1)[0][0] * (ymax-ymin) + ymin
				posz = nr.rand(1,1)[0][0] * (zmax-zmin) + zmin
				hitsph = False
				for sph in excluded_sph:
					if np.sqrt((posx-sph[0])**2+(posy-sph[1])**2+(posz-sph[2])**2) < sph_rad:
						hitsph = True
						break
				if not hitsph:
					posfound = True
			line = "mol 1 " + species[i] + " " + str(posx) + " " + str(posy) + " " + str(posz)
			f.write(line)
			f.write("\n")
			n += 1
			particles_placed += 1
		f.close()
	return particles_placed

def gen_config(num_layers, cfg_idx):
	# parameters
	fname_base = 'config-bdrv_base.txt'
	fname_pref = 'rv_'
	timestep = '1e-3'
	timestop = '60'
	kpl = '192e4'
	klp = '192e3'
	difcpyr = '11e2'
	difclac = '10e2'
	difcldh = '10e1'
	basex = 9000
	basey = 9000
	xlength = basex*1
	ylength = basey*1
	basez = 15000
	sphrad = 1025/4
	num_pyr = 1 # total pyr
	num_ldh_nadh = 1 # total ldh/nadh
	pyrvolpct = 90 # percentage of volume containing pyruvate
	lxnvolpct = 95 # percentage of volume containing enzyme
	bead_odds = 0.95
	
	# calculated properties
	free_volume_tot = xlength * ylength * basez
	vol_sphere = 4/3*np.pi*(sphrad**3)

	# filename
	fname = fname_pref + 'd' + difcpyr + '_k' + str(kpl) + '_o' + str(pyrvolpct) + '-' + str(lxnvolpct) + '_n' + str(num_layers) + '_' + str(cfg_idx)

	# read in base config
	f = open('../config/'+fname_base,'r')
	fr = f.read()
	f.close()
	fr = fr.replace('OUTPUTFNAME',fname,10).replace('TIMESTOP',timestop,10).replace('TIMESTEP',timestep,10).replace('DIFCPYR12',difcpyr,10).replace('DIFCLAC12',difclac,10).replace('DIFCLDH',difcldh,10).replace('KPLVAL',kpl,10).replace('KLPVAL',klp,10).replace('EPPWIDTHHALF',str(int(xlength/2)),10).replace('EPPWIDTH',str(int(xlength)),10)

	# add spheres
	num_spheres = 0
	sphi = 0
	sphtext = ""
	height = sphrad
	sphcens = []
	startoffset = 0
	vol_spheres = 0
	mass_spheres = 0
	layervols = []
	layerheights = []
	layerheightrange = []
	layerdims = []
	totalvolfilled = []
	height_inc = sphrad
	total_fv_added = 0
	while sphi < num_layers:
		vol_sph_layer = 0
		xlength = 3600 + 0.3*height
		xlength = min(xlength,basex)
		ylength = xlength
		layerdims.append(xlength)
		sphcens.append([])
		sphcen = [-xlength/2+startoffset,-ylength/2,height]
		xoffset = 0
		while sphcen[0] <= xlength/2 and sphcen[1] <= ylength/2:
			# add spheres sparsely
			if nr.rand(1,1)[0][0] <= bead_odds:
				sphtext += 'panel sph ' + str(sphcen[0]) + ' ' + str(sphcen[1]) + ' ' + str(sphcen[2]) + ' ' + str(sphrad) + ' 20 20\n'
				sphcens[sphi].append(sphcen)
				# calculate volume contributed by sphere
				if np.abs(sphcen[0])+sphrad <= xlength/2 and np.abs(sphcen[1])+sphrad <= ylength/2:
					vol_sph_layer += vol_sphere
				elif np.abs(sphcen[0])+sphrad > xlength/2 and np.abs(sphcen[1])+sphrad <= ylength/2:
					x = xlength/2 - np.abs(sphcen[0])
					a = np.sqrt(sphrad**2 - x**2)
					h = np.abs(sphcen[0])+sphrad - xlength/2
					outside_vol = 1/6 * np.pi * h * (3*a**2 + h**2)
					vol_sph_layer += vol_sphere - outside_vol
				elif np.abs(sphcen[0])+sphrad <= xlength/2 and np.abs(sphcen[1])+sphrad > ylength/2:
					y = ylength/2 - np.abs(sphcen[1])
					a = np.sqrt(sphrad**2 - y**2)
					h = np.abs(sphcen[1])+sphrad - ylength/2
					outside_vol = 1/6 * np.pi * h * (3*a**2 + h**2)
					vol_sph_layer += vol_sphere - outside_vol
				else:
					x = xlength/2 - np.abs(sphcen[0])
					a = np.sqrt(sphrad**2 - x**2)
					h = np.abs(sphcen[0])+sphrad - xlength/2
					outside_vol1 = 1/6 * np.pi * h * (3*a**2 + h**2)
					y = ylength/2 - np.abs(sphcen[1])
					a = np.sqrt(sphrad**2 - y**2)
					h = np.abs(sphcen[1])+sphrad - ylength/2
					outside_vol2 = 1/6 * np.pi * h * (3*a**2 + h**2)
					outside_vol_est = outside_vol1 + outside_vol2 - np.mean(outside_vol1/2+outside_vol2/2)
					vol_sph_layer += vol_sphere - outside_vol_est
				num_spheres += 1
			sphcen[0] += sphrad*2
			if sphcen[0] > xlength/2:
				xoffset = sphrad if xoffset == 0 else 0
				sphcen[0] = -xlength/2 + xoffset + startoffset if xoffset + startoffset < sphrad*2 else -xlength/2
				sphcen[1] += np.tan(np.pi/3) * sphrad
		layerheights.append([height - sphrad, height + sphrad])		
		layerheightrange.append([height - np.sqrt(3-(np.tan(np.pi/3)/3)**2) * sphrad/2, height + np.sqrt(3-(np.tan(np.pi/3)/3)**2) * sphrad/2])
		startoffset = sphrad if startoffset == 0 else 0
		vol_sph_layer *= 0.8
		vol_spheres += vol_sph_layer
		mass_spheres += vol_sph_layer/0.8 * 2.23e-9
		layervols.append(vol_sph_layer)
		new_vol_added = height_inc*xlength*ylength
		new_vol_filled = new_vol_added - vol_sph_layer
		total_fv_added += new_vol_filled
		totalvolfilled.append(new_vol_filled)
		height_inc = np.sqrt(3-(np.tan(np.pi/3)/3)**2) * sphrad
		height += height_inc
		sphi += 1
	
	# calculate volume to add due to beads
	pyrvol = max(total_fv_added, free_volume_tot*pyrvolpct/100)
	lnvol = max(free_volume_tot-total_fv_added, free_volume_tot*lxnvolpct/100)
	ppv = num_pyr/pyrvol
	lnpv = num_ldh_nadh/lnvol
	stickybeads_pyr = 4
	stickybeads_lxn = 1

	# add free volume layers
	while total_fv_added < free_volume_tot:
		xlength = 3600 + 0.3*height
		xlength = min(xlength,basex)
		ylength = xlength
		layerdims.append(xlength)
		layerheights.append([height - sphrad, height + sphrad])		
		layerheightrange.append([height - np.sqrt(3-(np.tan(np.pi/3)/3)**2) * sphrad/2, height + np.sqrt(3-(np.tan(np.pi/3)/3)**2) * sphrad/2])
		new_vol_added = height_inc*xlength*ylength
		total_fv_added += new_vol_added
		totalvolfilled.append(new_vol_added)
		height_inc = np.sqrt(3-(np.tan(np.pi/3)/3)**2) * sphrad
		height += height_inc
	
	# adjust total height
	zlength = height + sphrad * (1-np.sqrt(3-(np.tan(np.pi/3)/3)**2))

	fr = fr.replace('SPHEREDEFS',sphtext)
	fr = fr.replace('EPPHEIGHT',str(int(zlength)),10)

	# write config
	f = open('../config/config-'+fname+'.txt','w')
	f.write(fr)
	f.close()
	
	# add particles
	total_pyr_placed = 0
	total_lxn_placed = 0
	total_vol_filled_pyr = 0.0
	total_vol_filled_lxn = 0.0
	parti = 0
	# add particles in packed layers
	vol_filled_particles = 0
	while parti < num_layers:
		vol_per_layer = totalvolfilled[parti]
		if total_pyr_placed < num_pyr:
			pyr_to_place = vol_per_layer * ppv*stickybeads_pyr
			total_vol_filled_pyr += vol_per_layer
			total_pyr_placed += genpospackedspheres('a',parti,sphcens,-layerdims[parti]/2,layerdims[parti]/2,-layerdims[parti]/2,layerdims[parti]/2,layerheightrange[parti][0],layerheightrange[parti][1],sphrad,['pyr12'],[min(int(pyr_to_place),num_pyr-total_pyr_placed)],'../config/config-'+fname+'.txt')
			if int(ppv*stickybeads_pyr*total_vol_filled_pyr-total_pyr_placed) > 1 and total_pyr_placed < num_pyr:
				total_pyr_placed += genpospackedspheres('a',parti,sphcens,-layerdims[parti]/2,layerdims[parti]/2,-layerdims[parti]/2,layerdims[parti]/2,layerheightrange[parti][0],layerheightrange[parti][1],sphrad,['pyr12'],[min(int(ppv*stickybeads_pyr*total_vol_filled_pyr-total_pyr_placed),num_pyr-total_pyr_placed)],'../config/config-'+fname+'.txt')
		if total_vol_filled_pyr-vol_per_layer >= free_volume_tot*(100-lxnvolpct)/100 and total_lxn_placed < num_ldh_nadh:
			lxn_to_place = vol_per_layer * lnpv/stickybeads_lxn
			total_vol_filled_lxn += vol_per_layer
			total_lxn_placed += genpospackedspheres('a',parti,sphcens,-layerdims[parti]/2,layerdims[parti]/2,-layerdims[parti]/2,layerdims[parti]/2,layerheightrange[parti][0],layerheightrange[parti][1],sphrad,['ldh_nadh'],[min(int(lxn_to_place),num_ldh_nadh-total_lxn_placed)],'../config/config-'+fname+'.txt')
			if int(lnpv/stickybeads_lxn*total_vol_filled_lxn-total_lxn_placed) > 1 and total_lxn_placed < num_ldh_nadh:
				total_lxn_placed += genpospackedspheres('a',parti,sphcens,-layerdims[parti]/2,layerdims[parti]/2,-layerdims[parti]/2,layerdims[parti]/2,layerheightrange[parti][0],layerheightrange[parti][1],sphrad,['ldh_nadh'],[min(int(lnpv/stickybeads_lxn*total_vol_filled_lxn-total_lxn_placed),num_ldh_nadh-total_lxn_placed)],'../config/config-'+fname+'.txt')
		vol_filled_particles += vol_per_layer
		parti += 1
	
	# add particles in free volume layers
	while parti < len(layerheights):
		vol_per_layer = totalvolfilled[parti]
		if total_pyr_placed < num_pyr:
			pyr_to_place = int(min(vol_per_layer * ppv, num_pyr-total_pyr_placed))
			if parti+1 == len(layerheights):
				pyr_to_place = num_pyr-total_pyr_placed
			genposrectslab('a', -layerdims[parti]/2,layerdims[parti]/2,-layerdims[parti]/2,layerdims[parti]/2,layerheightrange[parti][0], layerheightrange[parti][1], ['pyr12'], [pyr_to_place], '../config/config-'+fname+'.txt')
			total_pyr_placed += pyr_to_place
		if total_lxn_placed < num_ldh_nadh and vol_filled_particles >= free_volume_tot*(100-lxnvolpct)/100:
			lxn_to_place = int(min(vol_per_layer * lnpv, num_ldh_nadh-total_lxn_placed))
			if parti+1 == len(layerheights):
				lxn_to_place = num_pyr-total_lxn_placed
			genposrectslab('a', -layerdims[parti]/2,layerdims[parti]/2,-layerdims[parti]/2,layerdims[parti]/2,layerheightrange[parti][0], layerheightrange[parti][1], ['ldh_nadh'], [lxn_to_place], '../config/config-'+fname+'.txt')
			total_lxn_placed += lxn_to_place
		vol_filled_particles += vol_per_layer
		parti += 1

	# end file
	f = open('../config/config-'+fname+'.txt','a')
	f.write("\nend_file")
	f.close()

	# return fname
	print('start "" smoldyn.exe config/config-'+fname+'.txt')
	return "'lm2-"+fname+"',", fname, mass_spheres/(free_volume_tot*1e-9)

# create batch configs for slurm
def write_configs(cfg_layers):
	bmr = 0
	j = 0
	for a in range(0,40,1):
		j += 1
		f1, f2, bmrj = gen_config(int(cfg_layers), str(j))
		bmr += bmrj

# write configs based on system arguments
cfg_start = int(sys.argv[1])
cfg_end = int(sys.argv[2])+1
cfg_step = int(sys.argv[3])

print('bead layers', 'bead mass ratio')
for c in range(cfg_start, cfg_end, cfg_step):
	#write_configs(c) # write for slurm
	f1, f2, bead_mass_ratio = gen_config(int(c), str(0)) # single config per layers
	#print(c, bead_mass_ratio)
	