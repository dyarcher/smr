Bloch Equation Modelling Applied to Hyperpolarized Magnetic Resonance (BEMATHMR) for Smoldyn Instructions
Current as of 2023-10-18

1. Installation

	To compile BEMATHMR for Smoldyn on Windows, enter the build folder in Developer Command Prompt for Visual Studio, and run:
		msbuild smoldyn.sln /p:Configuration=Release

	To compile BEMATHMR on Linux, enter the build folder and run:
		cmake ..
		make
		sudo make install
		
	Note: on Linux it is may be convenient to avoid compatibility issues with certain libraries by turning off compilation of Smoldyn's graphics modules. This can be done by ensuring the following lines in CMakeLists.txt (located in BEMATHMR's base directory) are set to OFF:
		option(OPTION_USE_OPENGL "Build with OpenGL support" ON)
		option(OPTION_USE_LIBTIFF "Build with LibTiff support" ON)
		
2. Configuration

	BEMATHMR uses the standard Smoldyn configuration format for defining all aspects of the biochemical simulation (i.e. spaces, particles species, surfaces, reactions, etc - see Smoldyn documentation for full details), but adds several commands for configuring the MR component of the simulation. These commands should be included as follows, with square brackets indicating a configurable parameter (the brackets should not be included in the statement):
		
		cmd b bemathmrsetT1 [T1]
		cmd b bemathmrsetT2 [T2]
		cmd b bemathmrsetHPT1 [HP T1]
		cmd b bemathmrsetBasePol [M0]
		cmd b bemathmrsetGyro [y]
		cmd b bemathmrsetCS [CS]
			These commands respectively set the longitudinal (T1) and transverse (T2) relaxation time in seconds, the T1 decay rate of hyperpolarized (non-recoverable) magnetization, the initial magnitude of polarization for a single particle (M0, generally set to 1), the gyromagnetic ratio in MHz/T, and the chemical shift (Larmor frequency offset) in Hz. Each of these commands must be included once per particle species (configured with a "species [name]" Smoldyn command); the corresponding values will be added to lists in the same order that the species are created. To avoid parameter mismatch, it is best to include these three lines immediately after each Smoldyn command defining a new particle species.
			
		cmd @ t bemathmrsetxmag [value]
		cmd @ t bemathmrsetymag [value]
		cmd @ t bemathmrsetzmag [value]
			These commands directly set the magnetization value on the given axis for all particles in the simulation.
			
		cmd b bemathmrparseq [filename] [seqtype] [seqchunk]
			The filename argument should reference the location (relative to the BEMATHMR program directory, not the configuration file directory) of a single file defining the pulse sequence to be applied during the simulation. The seqtype argument is a string, where "discrete" indicates that a text file containing discrete RF and gradient amplitudes will be used, and "pulseq" indicates that a pulseq format file will be used. For seqtype=discrete, the file should be a series of lines composed of space-delimited values: each line should contain first the time (in seconds), then the RF, Gx, Gy, and Gz amplitudes for that timepoint. For seqtype=pulseq, standard pulseq files are supported up to version 1.3.1. If a discrete sequence is used, the optional argument seqchunk is an integer which specifies how many timepoints of the sequence are read into timecourse work arrays at once; higher values require more local memory but are faster as they do not require reading the sequence file as often.
			
		cmd b bemathmrreadadc [filename]
			The filename argument should reference the location of a text file containing the readout (ADC) timings for the experiment. Each line of this text file must contain a single time value (in seconds) at which a readout value should be recorded.
			
		cmd a bemathmrwritereadout [filename]
			The filename argument should reference the location of a text file where readout values will be written at the end of the simulation.
			
		cmd b bemathmrinfo [filename] [infotype] [writefreq]
			The filename argument should reference the location of a text file where monitoring/debugging information will be written. The infotype argument is a string specifying what information will be written: infotype=debug provides primary debug information and infotype=ktraj (or infotype=kspace) provides k-space coordinates. Primary debug information for BEMATHMR encompasses every global or ensemble value relevant to the Bloch model, and will be written as a series of lines containing space-delimited values as follows: time (in seconds), RF amplitude, Gx amplitude, Gy amplitude, Gz amplitude, ADC state (on/off), total x-magnetization, total y-magnetization, and total z-magnetization. Both primary information and k-space coordinates can be written during a simulation by using two BEMATHMRdebug commands with different infotypes. The writefreq argument is an integer specifying how often the information will be written relative to the total number of simulation timesteps. For example, setting writefreq=100 means that the information will be written every 100 timesteps. Debug commands, especially with low values for writefreq, will cause significant slowdown of the simulation, so simulation time and/or particle count should be dramatically reduced for debugging.