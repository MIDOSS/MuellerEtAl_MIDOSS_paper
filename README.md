# A statistical representation of oil spill fate in the Salish Sea  <br />Code repository
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This repository contains the code developed during the MEOPAR-funded [MIDOSS project](https://midoss-docs.readthedocs.io/en/latest/index.html) and neccessary for reproducing the results and figures presented in: 

> Mueller, R. D., S. E. Allen, S. Chang, H. Nui, D. Latornell, S. Li, R.
Bagshaw, A. Bhudia, V. Do, K. Forysinski, B. Moore-Maley, C. Powers. A statistical representation of oil spill fate in the Salish Sea.  In prep.

The results evaluated in this study were generated with the following suite of software tools. 
- Creation of GeoTiffs and shapefiles from AIS ship track data [ADD ARCHIVE]
- Generation of 10,000 random oil spill scenarios (spill file) based on monte-carlo approach in [UBC-MOAD/moad_tool/MIDOSS](https://github.com/UBC-MOAD/moad_tools/tree/main/moad_tools/midoss)
- Attribution of oil types with [MIDOSS-MOHID-config](https://github.com/MIDOSS/MIDOSS-MOHID-config)
- Creation of `HDF5` forcing files for `MOHID` oil spill mode using [Make-MIDOSS-Forcing](https://github.com/MIDOSS/Make-MIDOSS-Forcing)
- Simulations of oil spill fate and transport using [MOHID-Cmd](https://github.com/MIDOSS/MOHID-Cmd?tab=readme-ov-file#license) and [MIDOSS-MOHID-CODE](https://github.com/MIDOSS/MIDOSS-MOHID-CODE).

2018 oil transfer data for Washington State can be accessed through a [Washington State Department of Ecology public records request](https://ecology.wa.gov/footer-pages/public-records-requests). 

## Licenses

This analysis and documentation are copyright 2018 by the [MIDOSS Project Contributors](https://midoss-docs.readthedocs.io/en/latest/CONTRIBUTORS.html) and The University of British Columbia.

They are licensed under the Apache License, Version 2.0.
http://www.apache.org/licenses/LICENSE-2.0
Please see the LICENSE file for details of the license.

