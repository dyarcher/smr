# Magnetic Resonance Module (SMR) for use with Smoldyn
Last Updated: 2026-01-30

## Directory Map
[compiled_versions](compiled_versions) contains SMR precompiled with Smoldyn for Windows and Linux. Current versions are compiled with Smoldyn dev version 2.65.

[configs](configs) contains example configuration files for various experiments.

[scripts](scripts) contains scripts for installation, for creating configurations and sequences, and  forprocessing output data.

[sequences](sequences) contains sequence files needed to run the example configurations.

[smoldyn_docs](smoldyn_docs) contains documentation for Smoldyn (not SMR), including license information.

[source](source) contains Smoldyn source code (including extensions) from the most recent compatible version. The main SMR code is contained in the Smoldyn subdirectory in the file smr.cpp. SMR requires modifications to some other Smoldyn source files, all in the Smoldyn subdirectory; previous versions are stored in dated folders for reference, starting with v202311 (the version used for the original SMR paper).

## Compilation
To compile SMR for Windows, create and enter a build directory, and run:

```msbuild smoldyn.sln /p:Configuration=Release```

To compile SMR for Linux (with gcc), enter the build folder and run:

```
cmake ..
make
optional: make install
```

Note: on Linux it may be convenient to avoid compatibility issues with certain libraries by turning off compilation of Smoldyn's graphics modules. This can be done by ensuring the following lines in CMakeLists.txt (located in SMR's base directory) are set to OFF:

```
option(OPTION_USE_OPENGL "Build with OpenGL support" ON)
option(OPTION_USE_LIBTIFF "Build with LibTiff support" ON)
```
		
## Configuration Commands
SMR uses the standard Smoldyn configuration format for defining all aspects of the biochemical simulation (i.e. spaces, particles species, surfaces, reactions, etc - see Smoldyn documentation for full details), but adds several commands for configuring the MR component of the simulation. These commands should be included as follows, with square brackets indicating a configurable parameter (the brackets should not be included in the statement):

```cmd b smrsetMR γ T1 T2 CS```

This command sets the gyromagnetic ratio in MHz/T, longitudinal (T1) and transverse (T2) relaxation time in seconds, and chemical shift (Larmor frequency offset) in Hz for each particle species.

```cmd b smrsetHPMR BasePol HPT1```

This command sets the base polarization of a hyperpolarized substrate (unitless, should be >1) and the T1 decay time of hyperpolarized magnetization.
	
These two commands must be included once per defined particle species; the corresponding values will be added to lists in the same order that the species are created. To avoid parameter mismatch, it is best to include these lines immediately after each Smoldyn command defining a new particle species.

```cmd b smrparseq filename seqtype seqchunk```

The filename argument should reference the location (relative to the SMR program directory, not the configuration file directory) of a single file defining the pulse sequence to be applied during the simulation. The seqtype argument is a string, where "discrete" indicates that a text file containing discrete RF and gradient amplitudes will be used, and "pulseq" indicates that a pulseq format file will be used. For seqtype=discrete, the file should be a series of lines composed of space-delimited values: each line should contain first the time (in seconds), then the RF, Gx, Gy, and Gz amplitudes for that timepoint. For seqtype=pulseq, standard pulseq files are supported up to version 1.3.1. If a discrete sequence is used, the optional argument seqchunk is an integer which specifies how many timepoints of the sequence are read into timecourse work arrays at once; higher values require more local memory but are faster as they do not require reading the sequence file as often.

```cmd a smrwritereadout filename```

The filename argument should reference the location of a text file where readout values will be written at the end of the simulation.

```cmd b smrinfo filename infotype writefreq```

The filename argument should reference the location of a text file where monitoring/debugging information will be written. The infotype argument is a string specifying what information will be written: infotype=debug provides primary debug information and infotype=ktraj (or infotype=kspace) provides k-space coordinates. Primary debug information for SMR encompasses every global or ensemble value relevant to the Bloch model, and will be written as a series of lines containing space-delimited values as follows: time (in seconds), RF amplitude, Gx amplitude, Gy amplitude, Gz amplitude, ADC state (on/off), total x-magnetization, total y-magnetization, and total z-magnetization. Both primary information and k-space coordinates can be written during a simulation by using two smrdebug commands with different infotypes. The writefreq argument is an integer specifying how often the information will be written relative to the total number of simulation timesteps. For example, setting writefreq=100 means that the information will be written every 100 timesteps. Debug commands, especially with low values for writefreq, will cause significant slowdown of the simulation, so simulation time and/or particle count should be dramatically reduced for debugging.
	

```
cmd @ t smrsetxmag Mx
cmd @ t smrsetymag My
cmd @ t smrsetzmag Mz
```

These commands directly set the magnetization value on the given axis for all particles in the simulation, which can be useful for debugging.

## How to Cite

If you use SMR in your research, please cite the following paper:

* Dingwell, D. A., & Cunningham, C. H. (2025). *Particle-based MR modeling with diffusion, microstructure, and enzymatic reactions*. Magnetic Resonance in Medicine, 93(1), 369–383.

Please also cite the original Smoldyn paper:

* Andrews, S. S., & Bray, D. (2004). *Stochastic simulation of chemical reactions with spatial resolution and single molecule detail*. Physical Biology, 1(3), 137–151.