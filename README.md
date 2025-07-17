# A statistical representation of oil spill fate in the Salish Sea  <br />

Code repository <br />
---
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![image](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/assets/59846131/ac188cfe-d502-4048-96aa-2eff284e3b20)

This repository contains the code developed during the MEOPAR-funded [MIDOSS project](https://midoss-docs.readthedocs.io/en/latest/index.html) and neccessary for reproducing the results and figures presented in: 

1. Mueller, R.D., S.E. Allen, S. Chang, H. Niu, D. Latornell, S. Li, R. Bagshaw, A. Bhudia, V. Do, K. Forysinsky, B. Moore-Maley, C. Power, L. Vespaziani. In Review. A statistical representation of oil spill fate in the Salish Sea (Part 1). Submitted to Marine Pollution Bulletin’s special issue on Oil Spills in Aquatic Systems.  
2. Mueller, R.D., S.E. Allen, S. Chang, H. Niu, D. Latornell, S. Li, R. Bagshaw, A. Bhudia, V. Do, K. Forysinsky, B. Moore-Maley, C. Power, L. Vespaziani. Accepted. A statistical representation of oil spill fate in the Salish Sea (Part 2). Submitted to Marine Pollution Bulletin’s special issue on Oil Spills in Aquatic Systems.  

## Related repositories
- Creation of `HDF5` forcing files from, e.g., [SalishSeaCast](https://salishsea.eos.ubc.ca/erddap/index.html) for `MOHID` oil spill mode: [Make-MIDOSS-Forcing](https://github.com/MIDOSS/Make-MIDOSS-Forcing)
- Simulation of oil spill fate and transport using a modified version of the [MOHID oil spill model](http://www.mohid.com):
  
    1. [MOHID-Cmd](https://github.com/MIDOSS/MOHID-Cmd?tab=readme-ov-file#license), and
    2. [MIDOSS-MOHID-CODE](https://github.com/MIDOSS/MIDOSS-MOHID-CODE).
- Code developed by Casey Hilliard to generate voyages from individual ship tracks ([1_generate_tracks_from_AIS_DB_vectorized.py](https://github.com/casey-h/MEOPAR_AIS/blob/master/02_Segment_Development/1_generate_tracks_from_AIS_DB_vectorized.py))

## Records Archive 
Mueller, R., Allen, S., Chang, S., Niu, H., Latornell, D., Moore-Maley, B., Bhudia, A., Do, V., Forysinkski, K., Power, C., Bagshaw, R., Li, S. (2025). MuellerEtAl_MIDOSS_datasets. Federated Research Data Repository. [https://doi.org/10.20383/103.01353](https://doi.org/10.20383/103.01353)

- **GeoTiffs** derived from AIS ship track data
- **Yaml files** with weighting values derived from, e.g., 2018 oil transfer data for Washington State, aquired through a [Washington State Department of Ecology public records request](https://ecology.wa.gov/footer-pages/public-records-requests). 
- **Text files (.csv)** with sets of 10,000 random oil spill scenarios (spill file) based on monte-carlo approach in [UBC-MOAD/moad_tool/MIDOSS](https://github.com/UBC-MOAD/moad_tools/tree/main/moad_tools/midoss)


## Related data sources
- 2018 oil transfer data for Washington State can be accessed through a [Washington State Department of Ecology public records request](https://ecology.wa.gov/footer-pages/public-records-requests).
- AIS ship track data is from [SPIRE maritime](https://spire.com/maritime/) (formerly exactEarth)

## Contributors
1. Allen, Susan: Lead supervisor, co-developed script to [randomize oil spills](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/blob/main/moad_tools/random_oil_spills.py), co-developed MOHID oil spill fate model, developed post-processing tools. Edited manuscript. Lead grant proposal.
2. Bagshaw, Ryah: Researched past oil spills and developed a database used to assign spill fractions from cargo capacity.
3. Bhudia, Ashutosh: Developed [make_hdf5.py](https://github.com/MIDOSS/Make-MIDOSS-Forcing/blob/main/make_midoss_forcing/make_hdf5.py) code to re-sample HRDPS and WW3 to SalishSeaCast grid using SCRIP interpolation in [mohid_interpolate.py](https://github.com/MIDOSS/Make-MIDOSS-Forcing/blob/main/make_midoss_forcing/mohid_interpolate.py), evaluated surface conditions (e.g.: winds, currents, and tides), ran MOHID model.
4. Chang, Stephanie:  Social Science lead for stakeholder workshops and graphical displays of information as well as collaborator in developing methods. 
5. Do, Vy: Developed modules for the script to randomize oil spills [randomize oil spills](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/blob/main/moad_tools/random_oil_spills.py), ran MOHID oil spill model, and evaluated surface conditions (e.g.: winds, currents, and tides).
6. Forysinski, Krista: Researched ship and marine terminal information to inform and develop oil attribution.
7. Latornell, Doug: Developed MOHID modeling platform on Compute Canada machines [MOHID-Cmd](https://github.com/MIDOSS/MOHID-Cmd), managed software implementation, refined and co-developed the script to randomize oil spills [randomize oil spills](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/blob/main/moad_tools/random_oil_spills.py), provided software development support for the research team, general backbone for keeping all systems a ``go''.
8. Li, Shihan: Refined biodegradation parameterization in the MOHID oil spill fate model and developed MOHID to include Visser method as well as Salish Sea Cast, HRDPS, and WW3 inputs.
9. Moore-Maley, Ben: Evaluated surface wind forcing effects on surface currents.  Co-wrote grant proposal. Collaborated in developing project. Contributed code for [map graphic](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/blob/main/notebooks/Figure1_DomainMap.ipynb). 
10. Mueller, Rachael: Post-doctoral fellow in charge of coordinating research groups, supervising students, leading methods and development of the script to randomize oil spills [randomize oil spills](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/blob/main/moad_tools/random_oil_spills.py), managing the selection of oil weathering parameters, developing research, developing code, analyzing Department of Ecology data, running MOHID model, analyzing output, developing post-processing tools, documenting information, presenting research, creating the graphics for and writing the research manuscripts.
11. Niu, Haibo: Oil spill model lead in charge of oil spill modeling methods and parameterizations. 
12. Power, Cameron: Developed GIS platform and AIS data products used in the script to randomize oil spills [randomize oil spills](https://github.com/MIDOSS/MuellerEtAl_MIDOSS_paper/blob/main/moad_tools/random_oil_spills.py). Implemented origin and destination attribution of AIS ship tracks in shapefiles. Researched ship and marine terminal information to inform and develop oil attribution.

## Licenses

This analysis and documentation are copyright 2018 by the [MIDOSS Project Contributors](https://midoss-docs.readthedocs.io/en/latest/CONTRIBUTORS.html) and The University of British Columbia.

They are licensed under the Apache License, Version 2.0.
http://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.

