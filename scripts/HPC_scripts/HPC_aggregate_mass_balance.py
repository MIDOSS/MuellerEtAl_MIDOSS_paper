#Oil type is identified by the Lagrangian output file name in create_SOILED_sro_runlist.ipynb. At this point, I preserve all oil type categories that I created from the Department of Ecology data.
#The script for sorting oil mass is called aggregate_sro_mass_byoil in aggregate_sro_mass.py, line 157. An oil dictionary is used to group the mass balance output values in the *.sro files (see line 209 of aggregate_sro_mass.py). Some of the variables are then grouped to create the surface, water column, beach, and air locations seen there.

    
import sys
sys.path.insert(1, '../../scripts/HPC_scripts')

from aggregate_sro_mass import aggregate_sro_mass_byoil
from aggregate_sro_mass import aggregate_sro_mass_all

# file path for the dictionay containing the list of .sro filenames by oil
file_paths = '/scratch/rmueller/MIDOSS/Results/MOHID_results_locations_try3_14062022_00:35:21.yaml'

# create new mass aggregation file
 with open(file_paths) as file:
     fnames = yaml.safe_load(file)
 for fname in fnames['diesel']:
     data = pandas.read_csv(fname, sep="\s+", skiprows=4)
     # remove first entry of NaN values
     data = data.drop([0], axis=0)
     length = len(data)
     if length>4:
         data = data.drop([length-3, length-2, length-1, length], axis=0)
         data_last = data[-1:]
         MBeached = (data['VolOilBeached'][1].item()*data['Density'][1].item()/
             (1-data['VWaterContent'][1].item())*
             (1-data['MWaterContent'][1].item()))
         MInitial = (
             data['MEvaporated'][1].item() + data['MDispersed'][1].item() + 
             data['MDissolved'][1].item() + data['MBio'][1].item() + 
             data['MassOil'][1].item() + MBeached
         )
         print(MInitial, MBeached, MInitial - data['MassOil'][1].item())

output_dir = Path('/scratch/rmueller/MIDOSS/Results/try3')
sro = aggregate_sro_mass_all(file_paths, output_dir)

df={}
df['ANS'] = pandas.DataFrame(sro['ANS'])
df['Bunker-C'] = pandas.DataFrame(sro['Bunker-C'])
df['Diesel'] = pandas.DataFrame(sro['Diesel'])
df['Dilbit'] = pandas.DataFrame(sro['Dilbit'])