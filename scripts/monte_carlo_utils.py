import numpy 
import yaml
import pathlib
import pandas
import geopandas as gpd
from decimal import *

def decimal_divide(numerator, denominator, precision):
    """Returns a floating point representation of the 
        mathematically correct answer to division of 
        a numerator with a denominator, up to precision equal to 
        'precision'.
        
        Inputs: 
        numerator can be either a scalar value or vector.
        denominator must be a singular value. 
        precision defines the order of precision, e.g.,
          precision = 10 allows for ten orders of magnitude or 1e-10
          decimal places. 
          
        Note: No error catches are included.
        
        Python binary arithmatic errors occur for precisions greater 
        than 1e-9 decimal places and this method ensures that the sum 
        of weighted values is 1 (and not affected by binary arithmatic 
        errors). 
        """
    
    result_list = []
    
    fraction_decimal = numpy.around(
        numerator / denominator,
        decimals = precision
    )
#    fraction_float = fraction_decimal
#     if type(numerator) == int or type(numerator) == numpy.float64:
#         getcontext().prec = precision
#         fraction_decimal = Decimal(numerator)/Decimal(denominator)
#         result_list.append(
#             numpy.around(
#                 numpy.float(fraction_decimal),
#                 decimals = precision
#             )
#         )
        
#     else:
#         for value in numerator:
#             getcontext().prec = precision
#             fraction_decimal = Decimal(value)/Decimal(denominator)
#             result_list.append(
#                 numpy.around(
#                     numpy.float(fraction_decimal),
#                     decimals = precision
#                 )
#             )

    
#     fraction_float = numpy.array(result_list)    
#   return fraction_float

    return fraction_decimal

def make_bins(lower_bound, upper_bound, step_size):
    """ Returns an ascending list of tuples from start to stop, with
        an interval of width and the center point values for intervals
    
        A tuple bins[i], i.e. (bins[i][0], bins[i][1])  with i > 0 
        and i < quantity, satisfies the following conditions:
            (1) bins[i][0] + width == bins[i][1]
            (2) bins[i-1][0] + width == bins[i][0] and
                bins[i-1][1] + width == bins[i][1]
    """
    
    bins = []
    center_points = []
    for low in range(lower_bound, upper_bound, step_size):
        bins.append((low, low + step_size))
        center_points.append(low + step_size/2)
    return bins, center_points

def get_bin(value, bins):
    """ Returns the smallest index i of bins so that
        bin[i][0] <= value < bin[i][1], where
        bins is a list of tuples, like [(0,20), (20, 40), (40, 60)]
    """
    
    for i in range(0, len(bins)):
        if bins[i][0] <= value < bins[i][1]:
            return i
    return -1

def place_into_bins(sorting_data, data_to_bin, bins):
    """ Returns 'binned_data, a vector of same length as 'bins' that
        has the values of 'data_to_bin' sorted into bins according to
        values of 'sorting_data.'
        Sorting_data and data_to_bin are 1D arrays of the same length.
        In our case, they are different attributes of vessels identified 
        by MMSI.
        'bins' is the output variable of the function 'make_bins'. 
    """
    
    binned_data = numpy.zeros(len(bins))
    index = 0
    for value in sorting_data:
        # accounting for no-data: -99999
        if value > 0:
            bin_index = get_bin(value, bins)  
            binned_data[bin_index] += data_to_bin[index]    
        index += 1
    return binned_data

# 
def clamp(n, minn, maxn):
    """ Returns the number n after fixing min and max thresholds. 
        minn and maxn are scalars that represent min and max capacities.
        clamp ensures that capacities are within min/max thresholds
        and sets n to minn or maxn if outside of thresholds, such that
        minn < n < maxn
    """
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n
    
def concat_shp(ship_type, shapefile_path):
    """
      INPUT: 
          - ship_type ["tanker", "barge", "atb", etc]: 
            MIDOSS-name for ship type (see oil_attribution.yaml for list)
          - shapefile_path [Path]: e.g., on Salish,
            Path('/data/MIDOSS/shapefiles/') 
      OUTPUT: 
          - dataframe of all 2018 ship tracks for given ship_type
    """
    for months in range(1,13):
        # set file location and name
        shapefile = shapefile_path/f'{ship_type}_2018_{months:02d}.shp'
        # import shapefile using geopandas
        monthly_shp = gpd.read_file(shapefile)
        if months == 1:
            print(f'creating {ship_type} shapefile for 2018, starting with January data')
            allTracks = monthly_shp
        else:
            print(f'Concatenating {ship_type} data from month {months}')
            allTracks = gpd.GeoDataFrame(
                pandas.concat([allTracks, monthly_shp])
            )
    return allTracks

def get_ECY_tanker_byvessel(vessels,ECY_xls_path,fac_xls_path):
    """
        Inputs:
            - vessels [list]: List of vessel names, e.g.["AMERICAN FREEDOM","PELICAN STATE"]
            - ECY_xls_path [path]: Location and name of ECY data spreadsheet
            - fac_xls_path [path]: Location and name of facilities transfer spreadsheet
        Outputs:
            - cargo_transfers [dataframe]: 2018 cargo transfers to/from the vessels and 
               the marine terminals used in this study, in liters.  Transfers are grouped by AntID
    """
    # conversion factor
    gal2liter = 3.78541
    # load dept. of ecology data
    ECY_df = get_ECY_df(
        ECY_xls_path, 
        fac_xls_path,
        group = 'no'
    )
    # extract tanker cargo transfers
    if isinstance(vessels, list):
        cargo_transfers = ECY_df.loc[
            (ECY_df.TransferType == 'Cargo') &
            (ECY_df.Deliverer.isin(vessels) |
             ECY_df.Receiver.isin(vessels)),
            ['TransferQtyInGallon', 'Deliverer','Receiver','StartDateTime','AntID']
        ].groupby('AntID').agg(
            {'TransferQtyInGallon':'sum',
             'Deliverer':'first', 
             'Receiver':'first',
             'StartDateTime':'first'}
            ).sort_values(by='TransferQtyInGallon',ascending=False)
    else: # if a string
         cargo_transfers = ECY_df.loc[
            (ECY_df.TransferType == 'Cargo') &
            (ECY_df.Deliverer.str.contains(vessels) |
             ECY_df.Receiver.str.contains(vessels)),
            ['TransferQtyInGallon', 'Deliverer','Receiver','StartDateTime','AntID']
        ].groupby('AntID').agg(
            {'TransferQtyInGallon':'sum',
             'Deliverer':'first', 
             'Receiver':'first',
             'StartDateTime':'first'}
            ).sort_values(by='TransferQtyInGallon',ascending=False)
    # convert to liters
    cargo_transfers['TransferQtyInGallon'] = gal2liter*cargo_transfers['TransferQtyInGallon']
    cargo_transfers=cargo_transfers.rename(
        columns={"TransferQtyInGallon":"TransferQtyInLiters"}
    ).reset_index()

    return cargo_transfers

def split_ECY_transfers(ECY_df):
    """
    split dataframe of ECY transfers into two-way transfers (import and export) and one-way transfers
    """
    one_way=pandas.DataFrame({})
    two_way=pandas.DataFrame({})
    count = 0
    idx_taken = 0
    # order transfers by time
    ECY_df = ECY_df.sort_values(by='StartDateTime').reset_index(drop=True)
    # categorize transfers
    for idx,deliverer in enumerate(ECY_df['Deliverer']):
        if idx != ECY_df['Deliverer'].shape[0]-1:
            if ((ECY_df['Deliverer'][idx] == ECY_df['Receiver'][idx+1]) &
                (ECY_df['Deliverer'][idx+1] == ECY_df['Receiver'][idx])):
                # count number of cases where there is a delivery both ways
                count += 1
                two_way = two_way.append(ECY_df.iloc[[idx]])
                idx_taken = 1
            else:
                if idx_taken:
                    two_way = two_way.append(ECY_df.iloc[[idx]])
                    idx_taken = 0
                else:
                    one_way = one_way.append(ECY_df.iloc[[idx]])
                    idx_taken = 0
        else:
            # categorize the last entry by comparing with the end - 1 values
            if ((ECY_df['Deliverer'][idx] == ECY_df['Receiver'][idx-1]) &
                (ECY_df['Deliverer'][idx-1] == ECY_df['Receiver'][idx])):
                count += 1
                two_way = two_way.append(ECY_df.iloc[[idx]])
    return one_way, two_way

def get_oil_type_cargo(yaml_file, facility, ship_type, random_generator):
    """ Returns oil for cargo attribution based on facility and vessel
        by querying information in input yaml_file
    """
    with open(yaml_file,"r") as file:
            
            # load fraction_of_total values for weighting 
            # random generator
            cargo = yaml.safe_load(file)
            ship = cargo[facility][ship_type]
            probability = [ship[fuel]['fraction_of_total'] 
                           for fuel in ship] 
            
            # First case indicates no cargo transfer to/from terminal 
            # (and a mistake in origin/destination analysis).
            # 
            # Second case ensures neccessary conditions for 
            # random_generator
        
            if sum(probability) == 0:
                fuel_type = []
            else:
                try:
                    fuel_type = random_generator.choice(
                              list(ship.keys()), p = probability)
                except ValueError:
                    # I was getting an error when including a '\' at the
                    # end of first line, so I removed it....
                    raise Exception(['Error: fraction of fuel transfers ' 
                                    + f'for {ship_type} servicing {facility} '\
                                    + f'ECYs not sum to 1 in {yaml_file}'])
                
            return fuel_type


def get_oil_type_cargo_generic_US(yaml_file, ship_type, random_generator):
    """ Returns oil for cargo attribution based on facility and vessel
        by querying information in input yaml_file.  This is essentially
        the same as 'get_oil_type_cargo' but is designed for yaml files
        that lack facility names
    """
    
    with open(yaml_file,"r") as file:
            
            # load fraction_of_total values for weighting random generator
            cargo = yaml.safe_load(file)
            ship = cargo[ship_type]
            probability = [ship[fuel]['fraction_of_total'] for fuel in ship] 
            
            # First case indicates no cargo transfer to/from terminal 
            # (and a mistake in origin/destination analysis).
            # 
            # Second case ensures neccessary conditions for random_generator
        
            if sum(probability) == 0:
                fuel_type = []
            else:
                try:
                    fuel_type = random_generator.choice(
                        list(ship.keys()), p = probability)
                except ValueError:
                    # I was getting an error when including a '\' at the
                    # end of first line, so I removed it....
                    raise Exception('Error: fraction of fuel transfers ' 
                                    f'for {ship_type} servicing {facility} '\
                                    f'ECYs not sum to 1 in {yaml_file}')
                
            return fuel_type


def get_montecarlo_oil_byregion(monte_carlo_csv, oil_attribution_file, fac_xls,
                                direction = 'export', vessel='tanker'):
    """
    PURPOSE: Return dataframe of monte carlo attributions to facilities by 
        import, export, combined and vessel-type
        
    INPUTS:
        directions['import','export','combined']
        vessel['tanker','atb','barge']
        
    OUTPUT:
        capacities DataFrame.  For import or export, this dataframe has a Region 
        attribution based on the location of the facility.  For combined, the 
        Region attribution is based on the location of the spill (as a US facility
        can be both an origin or a destination with conflicting region).
        
    TODO: 
         - Update method for attributing spill region so it's by mask 
           rather than by latitude
    
    """    
    # open montecarlo spills file
    mcdf = get_montecarlo_df(monte_carlo_csv)
    # Load oil Attribution File
    with open(oil_attribution_file) as file:
            oil_attrs = yaml.load(file, Loader=yaml.Loader)
    # Read in facility names
    facility_names_mc = oil_attrs['categories']['US_origin_destination']  
    # Load facility information
    facdf = assign_facility_region(fac_xls)
    # Add region based on spill location
    mcdf = assign_spill_region(mcdf)
    
    # ~~~~~ COMBINED ~~~~~
    # query dataframe for information on imports & exports by vessel
    # and oil types
    if direction == 'import':
        capacities = mcdf.loc[
            (mcdf.fuel_cargo == 'cargo') &
            (mcdf.vessel_type == vessel) &
            (mcdf.vessel_dest.isin(facility_names_mc)),
            ['cargo_capacity', 'vessel_dest', 'oil_type']
        ]
        # Create a new "Regions" column to assing region tag, using 
        # 'not attributed' to define transfers at locations not included 
        # in our evaluation
        capacities['ImportRegion'] = 'not attributed'
        # Find locations with transfers in our facility list and 
        # assign region tag.
        for idx,facility in enumerate(facdf['FacilityName']): 
            capacities['ImportRegion'] = numpy.where(
                (capacities['vessel_dest'] == facility), # ID transfer location
                facdf['Region'][idx],                    # assign region, or 
                capacities['ImportRegion']# keep NA attribution
            )
            
    elif direction == 'export':
        capacities = mcdf.loc[
            (mcdf.fuel_cargo == 'cargo') &
            (mcdf.vessel_type == vessel) &
            (mcdf.vessel_origin.isin(facility_names_mc)),
            ['cargo_capacity', 'vessel_origin','oil_type', 'SpillRegion']
        ]
        # Create a new "Regions" column to assing region tag, using 
        # 'not attributed' to define transfers at locations not included 
        # in our evaluation
        capacities['ExportRegion'] = 'not attributed'
        # Find locations with transfers in our facility list and 
        # assign region tag.
        for idx,facility in enumerate(facdf['FacilityName']): 
            capacities['ExportRegion'] = numpy.where(
                (capacities['vessel_origin'] == facility), # ID transfer location
                facdf['Region'][idx],                    # assign region, or 
                capacities['ExportRegion']# keep NA attribution
            )
    elif direction == 'combined':
        capacities = mcdf.loc[
            (mcdf.fuel_cargo == 'cargo') &
            (mcdf.vessel_type == vessel) &
            (mcdf.vessel_dest.isin(facility_names_mc) | 
             mcdf.vessel_origin.isin(facility_names_mc)),
            ['cargo_capacity', 'vessel_dest', 'vessel_origin',
             'oil_type', 'SpillRegion']
        ]
    else:
        # update this error statement!
        print('get_montecarlo_oil_byregion[ERROR]: direction can only be import, export, or combined.')

    return capacities
    
def assign_spill_region(mc_df):
    """
    Reads in a monte-carlo spills DataFrame (from on file or combination of files)
    and creates a Region attribution based on oil spill region
    
    TODO: Update to use region masks (Ask Ben or Tereza)
    """
    
    # define latitude bins
    lat_partition = [46.9, 48.3, 48.7]

    # define conditions used to bin facilities by latitude
    conditions = [
        (mc_df.spill_lat < lat_partition[0]),
        (mc_df.spill_lat >= lat_partition[0]) & 
        (mc_df.spill_lat < lat_partition[1]),
        (mc_df.spill_lat >= lat_partition[1]) & 
        (mc_df.spill_lat < lat_partition[2]),
        (mc_df.spill_lat >= lat_partition[2])
    ]

    # regional tags
    values = ['Columbia River','Puget Sound','Anacortes','Whatcom']

    # create a new column and assign values to it using 
    # defined conditions on latitudes
    mc_df['SpillRegion'] = numpy.select(conditions, values)

    return mc_df
        
def assign_facility_region(facilities_xlsx):
    """
    Loads the facilities excel spreadsheet and returns a dataframe with 
    that identifies the region the facility is in
    """
    # Facility information 
    facdf = pandas.read_excel(
        facilities_xlsx,
        sheet_name = 'Washington',
        usecols="B,D,J,K"
    )

    # define latitude bins
    lat_partition = [46.9, 48.3, 48.7]

    # define conditions used to bin facilities by latitude
    conditions = [
        (facdf.DockLatNumber < lat_partition[0]),
        (facdf.DockLatNumber >= lat_partition[0]) & 
        (facdf.DockLatNumber < lat_partition[1]),
        (facdf.DockLatNumber >= lat_partition[1]) & 
        (facdf.DockLatNumber < lat_partition[2]),
        (facdf.DockLatNumber >= lat_partition[2])
    ]

    # regional tags
    values = ['Columbia River','Puget Sound','Anacortes','Whatcom County']
    # create a new column and assign values to it using 
    # defined conditions on latitudes
    facdf['Region'] = numpy.select(conditions, values)

    return facdf

def get_voyage_transfers(voyage_xls, fac_xls):
    """
    PURPOSE: Read in voyage transfers for tankers, atbs, and barges
        and assign region attribution to voyages
    INPUT: 
        voyage_xls: Path to Origin_Destination_Analysis_updated.xlsx
        fac_xls: Path to Oil_Transfer_Facilities.xlsx
    OUTPUT:
        dataframe with columns for atbs, tankers, barges and region
    """
    # create dataframe for voyage transfers (From ECY_transfers.ipynb)
    # read in data
    tankers_df = pandas.read_excel(
        voyage_xls,
        sheet_name="VoyageCountsbyFacility_MR", 
        usecols="M,N,O",
        skiprows = 1
    )
    barge_atb_df = pandas.read_excel(
        voyage_xls,
        sheet_name="VoyageCountsbyFacility_MR", 
        usecols="E,F,G,J",
        skiprows = 1
    )

    # tidy-up column names
    tankers_df=tankers_df.rename(
        columns={"LOCATION.3":"LOCATION", 
                 "TRANSFERS.3":"tanker_transfers", 
                 "FACILITY CATEGORY.3":"CATEGORY"
                }
    )
    barge_atb_df=barge_atb_df.rename(
        columns={"LOCATION.1":"LOCATION", 
                 "TRANSFERS.1":"atb_transfers", 
                 "FACILITY CATEGORY.1":"CATEGORY", 
                 "TRANSFERS.2":"barge_transfers"}
    )
    # extract voyage transfers from WA
    tankers_df = tankers_df.loc[
        tankers_df.CATEGORY == 'WA',
        ['LOCATION','tanker_transfers']
    ]
    barges_df = barge_atb_df.loc[
        barge_atb_df.CATEGORY == 'WA',
        ['LOCATION','barge_transfers']
    ]
    atbs_df = barge_atb_df.loc[
        barge_atb_df.CATEGORY == 'WA',
        ['LOCATION','atb_transfers']
    ]
    # combine into one dataframe
    voyages = pandas.merge(
        left=tankers_df, 
        right=barges_df,
        on='LOCATION',
        how='left'
    )
    voyages = pandas.merge(
        left=voyages, 
        right=atbs_df,
        on='LOCATION',
        how='left'
    )    
    # Create a new "Regions" column to assing region tag, using 
    # 'not attributed' to define transfers at locations not included 
    # in our evaluation
    voyages['Region'] = 'not attributed'
    # Load facility information
    facdf = assign_facility_region(fac_xls)
    # Find locations with transfers in our facility list and 
    # assign region tag.
    for idx,facility in enumerate(facdf['FacilityName']): 
        voyages['Region'] = numpy.where(
            (voyages['LOCATION'] == facility), # identify transfer location
            facdf['Region'][idx],              # assign region to transfer
            voyages['Region']                  # or keep the NA attribution
        )
    voyages=voyages.set_index('LOCATION')   
    return voyages

def get_ECY_transfers(ECY_xls, fac_xls):
    """
    PURPOSE: Tally transfers to/from marine terminals used in our study.
        Currently this just tallies cargo transfers but could easily be 
        modified to tally fuel or cargo + fuel
    INPUTS: 
    - ECY_xls: Path to Dept. of Ecology data file, 'MuellerTrans4-30-20.xlsx'
    - fac_xls: Path to facilities data (simply because it's used by 
        get_ECY_df()), Oil_Transfer_Facilities.xlsx
    OUTPUTS:
    - Dataframe with total number of import, export and combined (import 
        + export) Cargo transfers for each marine terminal, sorted by vessel 
        type receiving or delivering product.  Format: df[vessel_type].
    """

    # Facility information for assinging regions
    facdf = assign_facility_region(fac_xls)
    facility_names = facdf['FacilityName']
    
    # Load ECY data
    ECY_df = get_ECY_df(
        ECY_xls, 
        fac_xls,
        group = 'no'
    )

    # Tally transfers for imports and exports, combined below
    imports = {}
    exports = {}    
    #~~~~~~~  TANKERS ~~~~~~~~~~~~~~~~~~~~~~~
    vessel_type = 'tanker'
    transfer_type = 'Cargo'
    type_description = ['TANK SHIP']
    imports[vessel_type] = ECY_df.loc[
        (ECY_df.TransferType == transfer_type) &
        (ECY_df.DelivererTypeDescription.isin(type_description)) & 
        (ECY_df.Receiver.isin(facility_names)),
        ['Receiver', 'TransferType']
    ].groupby('Receiver').count().rename(columns={'TransferType':'imports'})
    imports[vessel_type].index.names=['LOCATIONS']

    exports[vessel_type] = ECY_df.loc[
        (ECY_df.TransferType == transfer_type) &
        (ECY_df.ReceiverTypeDescription.isin(type_description)) & 
        (ECY_df.Deliverer.isin(facility_names)),
        ['Deliverer', 'TransferType']
    ].groupby('Deliverer').count().rename(columns={'TransferType':'exports'})
    exports[vessel_type].index.names=['LOCATIONS']

    #~~~~~~~  ATBs ~~~~~~~~~~~~~~~~~~~~~~~
    vessel_type = 'atb'
    transfer_type = 'Cargo'
    imports[vessel_type] = ECY_df.loc[
        (ECY_df.TransferType == transfer_type) &
        (ECY_df.Receiver.isin(facility_names)) &
        (ECY_df.Deliverer.str.contains('ITB') | 
         ECY_df.Deliverer.str.contains('ATB')), 
        ['Receiver', 'TransferType']
    ].groupby('Receiver').count().rename(columns={'TransferType':'imports'})
    imports[vessel_type].index.names=['LOCATIONS']

    exports[vessel_type] = ECY_df.loc[
        (ECY_df.TransferType == transfer_type) &
        (ECY_df.Deliverer.isin(facility_names)) &
        (ECY_df.Receiver.str.contains('ITB') | 
         ECY_df.Receiver.str.contains('ATB')), 
        ['Deliverer', 'TransferType']
    ].groupby('Deliverer').count().rename(columns={'TransferType':'exports'})
    exports[vessel_type].index.names=['LOCATIONS']


    #~~~~~~~  BARGES ~~~~~~~~~~~~~~~~~~~~~~~
    vessel_type = 'barge'
    transfer_type = 'Cargo'
    type_description = ['TANK BARGE','TUGBOAT']
    imports[vessel_type] = ECY_df.loc[
        (ECY_df.TransferType == transfer_type) &
        (ECY_df.DelivererTypeDescription.isin(type_description)) & 
        (~ECY_df.Deliverer.str.contains('ITB')) & 
        (~ECY_df.Deliverer.str.contains('ATB')) &
        (ECY_df.Receiver.isin(facility_names)), 
        ['Receiver', 'TransferType']
    ].groupby('Receiver').count().rename(columns={'TransferType':'imports'})
    imports[vessel_type].index.names=['LOCATIONS']

    exports[vessel_type] = ECY_df.loc[
        (ECY_df.TransferType == transfer_type) &
        (ECY_df.ReceiverTypeDescription.isin(type_description)) & 
        (~ECY_df.Receiver.str.contains('ITB')) & 
        (~ECY_df.Receiver.str.contains('ATB')) &
        (ECY_df.Deliverer.isin(facility_names)), 
        ['Deliverer', 'TransferType']
    ].groupby('Deliverer').count().rename(columns={'TransferType':'exports'})
    exports[vessel_type].index.names=['LOCATIONS']

    ECY={}
    for vessel in ['tanker','atb','barge']:
        ECY[vessel] = pandas.DataFrame(0,index=facility_names, columns={'combined'})
        ECY[vessel].index.name='LOCATIONS'
        ECY[vessel] = pandas.merge(
            left=ECY[vessel], 
            right=exports[vessel],
            left_index = True,
            right_index=True,
            how='left'
        ).fillna(0)
        ECY[vessel] = pandas.merge(
            left=ECY[vessel], 
            right=imports[vessel],
            left_index = True,
            right_index=True,
            how='left'
        ).fillna(0)
        ECY[vessel]['combined'] = (ECY[vessel]['imports'] + 
                                   ECY[vessel]['exports'])
    
    # Now assign regions to dataframe for each vessel "spreadsheet"
    for vessel in ['tanker','atb','barge']:
        ECY[vessel]['Region'] = 'not attributed'
        for idx,facility in enumerate(facdf['FacilityName']): 
            ECY[vessel]['Region'] = numpy.where(
                (ECY[vessel].index == facility), # identify transfer location
                facdf['Region'][idx],            # assign region to transfer
                ECY[vessel]['Region']            # or keep the NA attribution
            )
    return ECY

def get_montecarlo_df(MC_csv):
    """
    PURPOSE: Read in monte-carlo csv file and re-name Lagrangian_template to 
        oil_type with Lagrangian file names changed to oil-type name
    INPUT: 
        MC_csv[Path(to-mc-file)]
    """
    # define names used for Lagrangian files
    oil_template_names = [
        'Lagrangian_akns.dat','Lagrangian_bunker.dat',
         'Lagrangian_diesel.dat','Lagrangian_gas.dat',
         'Lagrangian_jet.dat','Lagrangian_dilbit.dat',
         'Lagrangian_other.dat'
    ]
    # define desired, end-product names for oil-types
    oil_types = [
        'ANS','Bunker-C',
        'Diesel','Gasoline',
        'Jet Fuel', 'Dilbit', 
        'Other'
    ]
    # open montecarlo spills file
    mc_df = pandas.read_csv(MC_csv)
    # replace Lagrangian template file names with oil type tags
    mc_df['oil_type'] = mc_df['Lagrangian_template'].replace(
        oil_template_names, 
        oil_types
    )
    # remove Lagrangian_template column
    mc_df = mc_df.drop(columns='Lagrangian_template')
    
    return mc_df

def get_ECY_atb(ECY_xls, fac_xls, transfer_type = 'cargo', facilities='selected'):
    """
    Returns transfer data for ATBs.
    ECY_xls[Path obj. or string]: Path(to Dept. of Ecology transfer dataset)
    facilities_xls[Path obj. or string]: Path(to spreadsheet with facilities information)
    transfer_type [string]: 'fuel', 'cargo', 'cargo_fuel'
    facilities [string]: 'all' or 'selected', 
    """
    # load ECY data
    ECY_df = get_ECY_df(
        ECY_xls, 
        fac_xls,
        group = 'yes'
    )

    # convert inputs to lower-case
    transfer_type = transfer_type.lower()
    facilities = facilities.lower()

    if transfer_type not in ['fuel', 'cargo', 'cargo_fuel']:
        raise ValueError('transfer_type options: fuel,cargo or cargo_fuel.')

    #  SELECTED FACILITIES
    if facilities == 'selected':

        # Facility information 
        facdf = pandas.read_excel(
            fac_xls,
            sheet_name = 'Washington',
            usecols="D"
        )
        # This list was copied from oil_attribution.yaml on 07/02/21
        # Eventually will update to read in from oil_attribution
        facility_names = facdf['FacilityECYName']
        
        if transfer_type == 'cargo':
            import_df = ECY_df.loc[
                (ECY_df.Receiver.isin(facility_names)) &
                (ECY_df.TransferType == 'Cargo') &   
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
            export_df = ECY_df.loc[
                (ECY_df.Deliverer.isin(facility_names)) &
                (ECY_df.TransferType == 'Cargo') &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]

        elif transfer_type == 'fuel':
            import_df = ECY_df.loc[
                (ECY_df.Receiver.isin(facility_names)) &
                (ECY_df.TransferType == 'Fueling') &  
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
            export_df = ECY_df.loc[
                (ECY_df.Deliverer.isin(facility_names)) &
                (ECY_df.TransferType == 'Fueling') &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]

        elif transfer_type == 'cargo_fuel':
            import_df = ECY_df.loc[
                (ECY_df.Receiver.isin(facility_names)) &
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
            export_df = ECY_df.loc[
                (ECY_df.Deliverer.isin(facility_names)) &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]         
        
    elif facilities == 'all':
        if transfer_type == 'cargo':
            import_df = ECY_df.loc[
                (ECY_df.TransferType == 'Cargo') & 
                (ECY_df.Deliverer.str.contains('ITB') |
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
            export_df = ECY_df.loc[
                (ECY_df.TransferType == 'Cargo') &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]

        elif transfer_type == 'fuel':
            import_df = ECY_df.loc[
                (ECY_df.TransferType == 'Fueling') & 
                (ECY_df.Deliverer.str.contains('ITB') |
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
            export_df = ECY_df.loc[
                (ECY_df.TransferType == 'Fueling') &
                (ECY_df.Receiver.str.contains('ITB') |
                 ECY_df.Receiver.str.contains('ATB')),
            ]

        elif transfer_type == 'cargo_fuel':
            import_df = ECY_df.loc[
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
            export_df = ECY_df.loc[
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]           
        
    return import_df, export_df

def get_ECY_df(ECY_xls, fac_xls, group='no'):
    """
    group['yes','no']: Specificies whether or not terminals ought to be re-named to 
     the names used in our monte carlo grouping
    """
    # Import columns are: (A) AndID, (E) StartDateTime, (G) Deliverer, 
    # (H) Receiver, (O) Region, 
    # (P) Product, (Q) Quantity in Gallons, (R) Transfer Type 
    # (oiling, Cargo, or Other)', (w) DelivererTypeDescription, 
    # (x) ReceiverTypeDescription 
    
    # define floating point precision for transfer quanitities
    precision = 5
    
    # read in data
    df = pandas.read_excel(
        ECY_xls,
        sheet_name='Vessel Oil Transfer', 
        usecols="A,E,G,H,P,Q,R,W,X"
    )

    # convert to float (though I'm not sure if this is still needed)
    df.TransferQtyInGallon = (
        df.TransferQtyInGallon.astype(float).round(precision)
    )

    # Housekeeping: Force one name per marine transfer site
    df = df.replace(
        to_replace = "US Oil Tacoma ",
        value = "U.S. Oil & Refining"
    )
    df = df.replace(
        to_replace = "TLP",
        value = "TLP Management Services LLC (TMS)"
    )
    # Housekeeping: Convert ECY terminal names to the names
    #  used in our monte-carlo, if different. 
    df = df.replace(
        to_replace = "Maxum (Rainer Petroleum)",
        value = "Maxum Petroleum - Harbor Island Terminal"
    )
    df = df.replace(
        to_replace = "Andeavor Anacortes Refinery (formerly Tesoro)",
        value = "Marathon Anacortes Refinery (formerly Tesoro)"
    )
    
    # Consolidate (if selected by group='yes'):
    # Apply terminal groupings used in our monte-carlo by
    # renaming terminals to the names used in our
    # origin-destination attribution
    if group == 'yes':
        df = df.replace(
            to_replace = "Maxum Petroleum - Harbor Island Terminal",
            value = "Kinder Morgan Liquids Terminal - Harbor Island"
        )
        df = df.replace(
            to_replace = "Shell Oil LP Seattle Distribution Terminal",
            value = "Kinder Morgan Liquids Terminal - Harbor Island"
        )
        df = df.replace(
            to_replace = "Nustar Energy Tacoma",
            value = "Phillips 66 Tacoma Terminal"
        )

    # Create a new "Regions" column to assing region tag, using 
    # 'not attributed' to define transfers at locations not included 
    # in our evaluation
    df['ImportRegion'] = 'not attributed'
    df['ExportRegion'] = 'not attributed'
    # Load facility information
    facdf = assign_facility_region(fac_xls)
    # Find locations with transfers in our facility list and 
    # assign region tag.
    for idx,facility in enumerate(facdf['FacilityName']): 
        df['ImportRegion'] = numpy.where(
            (df['Receiver'] == facility), # identify transfer location
            facdf['Region'][idx],         # assign region to transfer
            df['ImportRegion']            # or keep the NA attribution
        )
        df['ExportRegion'] = numpy.where(
            (df['Deliverer'] == facility), # identify transfer location
            facdf['Region'][idx],          # assign region to transfer
            df['ExportRegion']             # or keep the NA attribution
        )
    return df

def rename_ECY_df_oils(ECY_df, ECY_xls):
    """
    Reads in ECY dataframe with original 'Product' names and converts
    them to the names we use in our monte-carlo
    
    ECY_df: Department of Ecolody data in DataFrame format, 
        as in output from get_ECY_df 
    ECY_xls: The original ECY oil transfer spreadsheet, the same as is
        read into get_ECY_df
    """
    # I'm sure there is a better way of allowing name flaxibilitye
    # and preventing unnecessary memory hogging, but...I'm choosing
    # ease and efficiency right now....
    df = ECY_df.copy()
    
    # read in monte-carlo oil classifications
    oil_classification = get_ECY_oilclassification(ECY_xls)

    # Rename oil types to match our in-house naming convention
    for oil_mc in oil_classification.keys():
        for oil_ECY in oil_classification[oil_mc]:
            df['Product'] = df['Product'].replace(oil_ECY, oil_mc)
    # Now convert from our in-house names to our presentation names
    conditions = [
        (df['Product']=='akns'), 
        (df['Product']=='bunker'),
        (df['Product']=='dilbit'),
        (df['Product']=='jet'),
        (df['Product']=='diesel'),
        (df['Product']=='gas'),
        (df['Product']=='other') 
    ]
    # regional tags
    new_values = [
        'ANS' ,'Bunker-C','Dilbit','Jet Fuel','Diesel','Gasoline','Other'
    ]
    # create a new column and assign values to it using 
    # defined conditions on oil types
    df['Product'] = numpy.select(conditions, new_values)
    
    return df

def get_oil_classification(ECY_transfer_xlsx):
    """ Returns the list of all the names in the ECY database that are 
        attributed to our oil types.  
        INPUT['string' or Path]: 
            location/name of 2018 ECY oil transfer excel spreadsheet
        OUTPUT[dictionary]:
            Oil types attributed in our study to: AKNS, Bunker, Dilbit, 
            Diesel, Gas, Jet and Other. 
    """
    # Import columns are: 
    #   (G) Deliverer, (H) Receiver, (O) Region, (P) Product, 
    #   (Q) Quantity in Gallons, (R) Transfer Type (Fueling, Cargo, or Other)', 
    #   (w) DelivererTypeDescription, (x) ReceiverTypeDescription 
    #2018
    df = pandas.read_excel(
        ECY_transfer_xlsx,
        sheet_name='Vessel Oil Transfer', 
        usecols="G,H,P,Q,R,W,X"
    )
    # oil types used in our study
    oil_types = [
        'akns', 'bunker', 'dilbit', 'jet', 'diesel', 'gas', 'other'
    ]
    # initialize oil dictionary
    oil_classification = {}
    for oil in oil_types:
        oil_classification[oil] = []

    [nrows,ncols] = df.shape
    for row in range(nrows):
        if ('CRUDE' in df.Product[row] and 
            df.Product[row] not in 
            oil_classification['akns']
           ):
            oil_classification['akns'].append(df.Product[row])
        elif ('BAKKEN' in df.Product[row] and 
              df.Product[row] not in oil_classification['akns']
             ):
            oil_classification['akns'].append(df.Product[row])
        elif ('BUNKER' in df.Product[row] and 
              df.Product[row] not in oil_classification['bunker']
             ):
            oil_classification['bunker'].append(df.Product[row])
        elif ('BITUMEN' in df.Product[row] and 
              df.Product[row] not in oil_classification['dilbit']
             ):
            oil_classification['dilbit'].append(df.Product[row])
        elif ('DIESEL' in df.Product[row] and 
              df.Product[row] not in oil_classification['diesel']
             ):
            oil_classification['diesel'].append(df.Product[row])
        elif ('GASOLINE' in df.Product[row] and 
              df.Product[row] not in oil_classification['gas']
             ):
            oil_classification['gas'].append(df.Product[row])
        elif ('JET' in df.Product[row] and df.Product[row] not in 
              oil_classification['jet']
             ):
            oil_classification['jet'].append(df.Product[row])
        elif ('CRUDE' not in df.Product[row] and
              'BAKKEN' not in df.Product[row] and
              'BUNKER' not in df.Product[row] and
              'BITUMEN' not in df.Product[row] and
              'DIESEL' not in df.Product[row] and
              'GASOLINE' not in df.Product[row] and
              'JET' not in df.Product[row] and
              df.Product[row] not in oil_classification['other']):
            oil_classification['other'].append(df.Product[row])

    return oil_classification

def get_ECY_barges(ECY_xls,fac_xls, direction='combined',facilities='selected',transfer_type = 'cargo_fuel'):
    """
    THIS CODE HAS A LOT OF REDUNDANCY. I PLAN TO UPDATE BY USING 
    COMBINED INPUT/OUTPUT TO RETURN EITHER IMPORT OR OUTPUT, IF SELECTED
    
    ALSO CHANGE NAME TO get_ECY_BARGES_TRANSFERS TO MATCH ATB FUNCTION
    Returns number of transfers to/from WA marine terminals used in our study
    ECY_xls[Path obj. or string]: Path(to Dept. of Ecology transfer dataset)
    marine_terminals [string list]: list of US marine terminals to include
    direction [string]: 'import','export','combined', where:
        'import' means from vessel to marine terminal
        'export' means from marine terminal to vessel
        'combined' means both import and export transfers
    facilities [string]: 'all' or 'selected', 
    transfer_type [string]: 'fuel','cargo','cargo_fuel'
    """
    print('get_ECY_barges: not yet tested with fac_xls as input')
    
    # load ECY data
    ECY_df = get_ECY_df(
        ECY_xls, 
        fac_xls,
        group = 'yes'
    )
    
    # convert inputs to lower-case
    direction = direction.lower()
    transfer_type = transfer_type.lower()
    facilities = facilities.lower()
    
    # 
    if transfer_type not in ['fuel', 'cargo', 'cargo_fuel']:
        raise ValueError('transfer_type options: fuel,cargo or cargo_fuel.')
    if direction not in ['import', 'export', 'combined']:
        raise ValueError('direction options: import, export or combined.')
    
    #  SELECTED FACILITIES
    if facilities == 'selected':
        
        # This list was copied from oil_attribution.yaml on 07/02/21
        # Eventually will update to read in from oil_attribution
        facility_names = [ 
            'BP Cherry Point Refinery', 
            'Shell Puget Sound Refinery', 
            'Tidewater Snake River Terminal', 
            'SeaPort Sound Terminal', 
            'Tesoro Vancouver Terminal',
            'Phillips 66 Ferndale Refinery', 
            'Phillips 66 Tacoma Terminal', 
            'Marathon Anacortes Refinery (formerly Tesoro)',
            'Tesoro Port Angeles Terminal',
            'U.S. Oil & Refining',
            'Naval Air Station Whidbey Island (NASWI)',
            'NAVSUP Manchester', 
            'Alon Asphalt Company (Paramount Petroleum)', 
            'Kinder Morgan Liquids Terminal - Harbor Island',
            'Nustar Energy Vancouver',
            'Tesoro Pasco Terminal', 
            'REG Grays Harbor, LLC', 
            'Tidewater Vancouver Terminal',
            'TLP Management Services LLC (TMS)'
        ]


        # get transfer records for imports, exports and both imports and exports
        # imports
        if direction == 'import':
            print('import')
            if transfer_type == 'cargo':
                import_df = ECY_df.loc[
                    (ECY_df.Receiver.isin(facility_names)) &
                    (ECY_df.TransferType == 'Cargo') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'fuel':
                import_df = ECY_df.loc[
                    (ECY_df.Receiver.isin(facility_names)) &
                    (ECY_df.TransferType == 'Fueling') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'cargo_fuel':
                import_df = ECY_df.loc[
                    (ECY_df.Receiver.isin(facility_names)) &
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]
            return import_df    
        if direction == 'export':
            print('export')
            #exports
            if transfer_type == 'cargo':
                export_df = ECY_df.loc[
                    (ECY_df.Deliverer.isin(facility_names)) &
                    (ECY_df.TransferType == 'Cargo') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'fuel':
                export_df = ECY_df.loc[
                    (ECY_df.Deliverer.isin(facility_names)) &
                    (ECY_df.TransferType == 'Fueling') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'cargo_fuel':
                export_df = ECY_df.loc[
                    (ECY_df.Deliverer.isin(facility_names)) &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            return export_df
        # Now combine both imports and exports for 
        if direction == 'combined':
            print('combined')
            #import
            if transfer_type == 'cargo':
                print('cargo')
                import_df = ECY_df.loc[
                    (ECY_df.Receiver.isin(facility_names)) &
                    (ECY_df.TransferType == 'Cargo') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'fuel':
                print('fuel')
                import_df = ECY_df.loc[
                    (ECY_df.Receiver.isin(facility_names)) &
                    (ECY_df.TransferType == 'Fueling') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'cargo_fuel':
                print('cargo_fuel')
                import_df = ECY_df.loc[
                    (ECY_df.Receiver.isin(facility_names)) &
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]
            #export
            if transfer_type == 'cargo':
                print('cargo')
                export_df = ECY_df.loc[
                    (ECY_df.Deliverer.isin(facility_names)) &
                    (ECY_df.TransferType == 'Cargo') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'fuel':
                print('fuel')
                export_df = ECY_df.loc[
                    (ECY_df.Deliverer.isin(facility_names)) &
                    (ECY_df.TransferType == 'Fueling') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'cargo_fuel':
                print('cargo_fuel')
                export_df = ECY_df.loc[
                    (ECY_df.Deliverer.isin(facility_names)) &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            #combine import and export
            importexport_df = import_df.append(export_df)
            importexport_df.reset_index(inplace=True)
            return importexport_df
        
    elif facilities == 'all':
        # get transfer records for imports, exports and both imports and exports
        # imports
        if direction == 'import':
            print('import')
            if transfer_type == 'cargo':
                import_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Cargo') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'fuel':
                import_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Fueling') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'cargo_fuel':
                import_df = ECY_df.loc[
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]
            return import_df    
        if direction == 'export':
            print('export')
            #exports
            if transfer_type == 'cargo':
                export_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Cargo') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'fuel':
                export_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Fueling') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'cargo_fuel':
                export_df = ECY_df.loc[
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            return export_df
        # Now combine both imports and exports for 
        if direction == 'combined':
            print('combined')
            #import
            if transfer_type == 'cargo':
                print('cargo')
                import_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Cargo') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'fuel':
                print('fuel')
                import_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Fueling') &  
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]

            elif transfer_type == 'cargo_fuel':
                print('cargo_fuel')
                import_df = ECY_df.loc[
                    (ECY_df.DelivererTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Deliverer.str.contains('ITB')) & 
                    (~ECY_df.Deliverer.str.contains('ATB')),
                ]
            #export
            if transfer_type == 'cargo':
                print('cargo')
                export_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Cargo') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'fuel':
                print('fuel')
                export_df = ECY_df.loc[
                    (ECY_df.TransferType == 'Fueling') &
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            elif transfer_type == 'cargo_fuel':
                print('cargo_fuel')
                export_df = ECY_df.loc[
                    (ECY_df.ReceiverTypeDescription.isin(
                        ['TANK BARGE','TUGBOAT'])) & 
                    (~ECY_df.Receiver.str.contains('ITB')) & 
                    (~ECY_df.Receiver.str.contains('ATB')),
                ]
            #combine import and export
            importexport_df = import_df.append(export_df)
            importexport_df.reset_index(inplace=True)
            return importexport_df

        
        
def get_ECY_atb_transfers(ECY_xls,fac_xls,transfer_type = 'cargo',facilities='selected'):
    """
    Returns number of transfers to/from WA marine terminals used in our study
    ECY_xls[Path obj. or string]: Path(to Dept. of Ecology transfer dataset)
    direction [string]: 'import','export','combined', where:
        'import' means from vessel to marine terminal
        'export' means from marine terminal to vessel
        'combined' means both import and export transfers
    facilities [string]: 'all' or 'selected', 
    
    TO-DO: Update to count transfers with the same AntID as one
    """
    print('this code not yet tested with fac_xls as input')
    # load ECY data
    ECY_df = get_ECY_df(
        ECY_xls, 
        fac_xls,
        group = 'yes'
    )

    # convert inputs to lower-case
    transfer_type = transfer_type.lower()
    facilities = facilities.lower()

    if transfer_type not in ['fuel', 'cargo', 'cargo_fuel']:
        raise ValueError('transfer_type options: fuel,cargo or cargo_fuel.')

    #  SELECTED FACILITIES
    if facilities == 'selected':

        # This list was copied from oil_attribution.yaml on 07/02/21
        # Eventually will update to read in from oil_attribution
        facility_names = [ 
            'BP Cherry Point Refinery', 
            'Shell Puget Sound Refinery', 
            'Tidewater Snake River Terminal', 
            'SeaPort Sound Terminal', 
            'Tesoro Vancouver Terminal',
            'Phillips 66 Ferndale Refinery', 
            'Phillips 66 Tacoma Terminal', 
            'Marathon Anacortes Refinery (formerly Tesoro)',
            'Tesoro Port Angeles Terminal',
            'U.S. Oil & Refining',
            'Naval Air Station Whidbey Island (NASWI)',
            'NAVSUP Manchester', 
            'Alon Asphalt Company (Paramount Petroleum)', 
            'Kinder Morgan Liquids Terminal - Harbor Island',
            'Nustar Energy Vancouver',
            'Tesoro Pasco Terminal', 
            'REG Grays Harbor, LLC', 
            'Tidewater Vancouver Terminal',
            'TLP Management Services LLC (TMS)'
        ]
        #import
        if transfer_type == 'cargo':
            print('cargo')
            import_df = ECY_df.loc[
                (ECY_df.Receiver.isin(facility_names)) &
                (ECY_df.TransferType == 'Cargo') &   
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]

        elif transfer_type == 'fuel':
            print('fuel')
            import_df = ECY_df.loc[
                (ECY_df.Receiver.isin(facility_names)) &
                (ECY_df.TransferType == 'Fueling') &  
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]

        elif transfer_type == 'cargo_fuel':
            print('cargo_fuel')
            import_df = ECY_df.loc[
                (ECY_df.Receiver.isin(facility_names)) &
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
        import_count = import_df['Deliverer'].count()
        print(f'{import_count} {transfer_type}'
              ' transfers to monte carlo terminals')
        #export
        if transfer_type == 'cargo':
            print('cargo')
            export_df = ECY_df.loc[
                (ECY_df.Deliverer.isin(facility_names)) &
                (ECY_df.TransferType == 'Cargo') &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]
        elif transfer_type == 'fuel':
            print('fuel')
            export_df = ECY_df.loc[
                (ECY_df.Deliverer.isin(facility_names)) &
                (ECY_df.TransferType == 'Fueling') &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]
        elif transfer_type == 'cargo_fuel':
            print('cargo_fuel')
            export_df = ECY_df.loc[
                (ECY_df.Deliverer.isin(facility_names)) &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]
        export_count = export_df['Deliverer'].count()
        print(f'{export_count} {transfer_type}'
              ' transfers from monte carlo terminals')
        #combine import and export
        importexport_df = import_df.append(export_df)
        importexport_df.reset_index(inplace=True)
        count = importexport_df['Deliverer'].count()
        return count

    elif facilities == 'all':
        #import
        if transfer_type == 'cargo':
            print('cargo')
            import_df = ECY_df.loc[
                (ECY_df.TransferType == 'Cargo') & 
                (ECY_df.Deliverer.str.contains('ITB') |
                 ECY_df.Deliverer.str.contains('ATB')),
            ]

        elif transfer_type == 'fuel':
            print('fuel')
            import_df = ECY_df.loc[
                (ECY_df.TransferType == 'Fueling') & 
                (ECY_df.Deliverer.str.contains('ITB') |
                 ECY_df.Deliverer.str.contains('ATB')),
            ]

        elif transfer_type == 'cargo_fuel':
            print('cargo_fuel')
            import_df = ECY_df.loc[
                (ECY_df.Deliverer.str.contains('ITB') | 
                 ECY_df.Deliverer.str.contains('ATB')),
            ]
        import_count = import_df['Deliverer'].count()
        print(f'{import_count} {transfer_type}'
              ' transfers from all sources')
        #export
        if transfer_type == 'cargo':
            print('cargo')
            export_df = ECY_df.loc[
                (ECY_df.TransferType == 'Cargo') &
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]
        elif transfer_type == 'fuel':
            print('fuel')
            export_df = ECY_df.loc[
                (ECY_df.TransferType == 'Fueling') &
                (ECY_df.Receiver.str.contains('ITB') |
                 ECY_df.Receiver.str.contains('ATB')),
            ]
        elif transfer_type == 'cargo_fuel':
            print('cargo_fuel')
            export_df = ECY_df.loc[
                (ECY_df.Receiver.str.contains('ITB') | 
                 ECY_df.Receiver.str.contains('ATB')),
            ]
        export_count = export_df['Deliverer'].count()
        print(f'{export_count} {transfer_type}'
              ' transfers from all sources')
        #combine import and export
        importexport_df = import_df.append(export_df)
        importexport_df.reset_index(inplace=True)
        count = importexport_df['Deliverer'].count()
        return count
        
def get_montecarlo_oil_byvessel(vessel, monte_carlo_csv):
    
    # Currently use hard-coded file location for oil_attribution.yaml
    # This won't work for distribution and will need to be fixed. 
    
    # Oil Attribution file location
    oil_attribution_file = (
        '/Users/rmueller/Data/MIDOSS/marine_transport_data/'
        'oil_attribution.yaml'
    )
    # Load oil Attribution File
    with open(oil_attribution_file) as file:
            oil_attrs = yaml.load(file, Loader=yaml.Loader)
    # Read in facility names
    facility_names_mc = oil_attrs['categories']['US_origin_destination']
    
    oil_template_names = [
        'Lagrangian_akns.dat','Lagrangian_bunker.dat',
         'Lagrangian_diesel.dat','Lagrangian_gas.dat',
         'Lagrangian_jet.dat','Lagrangian_dilbit.dat',
         'Lagrangian_other.dat'
    ]
    oil_types = [
        'ANS','Bunker-C',
        'Diesel','Gasoline',
        'Jet Fuel', 'Dilbit', 
        'Other'
    ]
    
    # open montecarlo spills file
    mcdf = pandas.read_csv(monte_carlo_csv)
    # replace Lagrangian template file names with oil type tags
    mcdf['Lagrangian_template'] = mcdf['Lagrangian_template'].replace(
        oil_template_names, 
        oil_types
    )
    # ~~~~~ EXPORTS ~~~~~
    # query dataframe for information on oil export types by vessel
    export_capacity = mcdf.loc[
        (mcdf.vessel_type == vessel) &
        (mcdf.fuel_cargo == 'cargo') &
        (mcdf.vessel_origin.isin(facility_names_mc)),
        ['cargo_capacity', 'vessel_origin', 'Lagrangian_template']
    ]
    # add up oil capacities by vessel and oil types
    montecarlo_export_byoil = (
        export_capacity.groupby(
            'Lagrangian_template'
        ).cargo_capacity.sum()
    )
    # ~~~~~ IMPORTS ~~~~~
    # query dataframe for information on oil export types by vessel
    import_capacity = mcdf.loc[
        (mcdf.vessel_type == vessel) &
        (mcdf.fuel_cargo == 'cargo') &
        (mcdf.vessel_dest.isin(facility_names_mc)),
        ['cargo_capacity', 'vessel_dest', 'Lagrangian_template']
    ]
    # add up oil capacities by vessel and oil types
    montecarlo_import_byoil = (
        import_capacity.groupby(
            'Lagrangian_template'
        ).cargo_capacity.sum()
    )
    
    # ~~~~~ COMBINED ~~~~~
    # query dataframe for information on imports & exports by vessel
    # and oil types
    net_capacity = mcdf.loc[
        (mcdf.vessel_type == vessel) &
        (mcdf.fuel_cargo == 'cargo') &
        (mcdf.vessel_dest.isin(facility_names_mc) | 
         mcdf.vessel_origin.isin(facility_names_mc)),
        ['cargo_capacity', 'vessel_dest', 'Lagrangian_template']
    ]
    # add up oil capacities by vessel and oil types
    montecarlo_byoil = (
        net_capacity.groupby(
            'Lagrangian_template'
        ).cargo_capacity.sum()
    )
    return montecarlo_export_byoil, montecarlo_import_byoil, montecarlo_byoil

def get_montecarlo_oil(vessel, monte_carlo_csv):
    """
    Same as get_montecarlo_oil_byfac but generalized to return quantities of 
    oil by oil type for all US attribution (inclusive of US general and facilities)
    
    INPUTS:
    - vessel ['string']: ['atb','barge','tanker']
    - monte_carlo_csv['Path' or 'string']: Path and file name for csv file
    """
    
    # VERIFY THIS LIST IS SAME AS IN OIL_ATTRIBUTION.YAML 
    # AND GET FACILITY NAMES FROM THERE
    # list of facility names to query monte-carlo csv file, with:
    # 1) Marathon Anacortes Refinery (formerly Tesoro) instead of Andeavor 
    #    Anacortes Refinery (formerly Tesoro) 
    # 2) Maxum Petroleum - Harbor Island Terminal instead of 
    #    Maxum (Rainer Petroleum)
    origin_dest_names = [ 
        'BP Cherry Point Refinery', 'Shell Puget Sound Refinery',
        'Tidewater Snake River Terminal', 
        'SeaPort Sound Terminal', 'Tesoro Vancouver Terminal',
        'Phillips 66 Ferndale Refinery', 'Phillips 66 Tacoma Terminal', 
        'Marathon Anacortes Refinery (formerly Tesoro)',
        'Tesoro Port Angeles Terminal','U.S. Oil & Refining',
        'Naval Air Station Whidbey Island (NASWI)',
        'NAVSUP Manchester', 'Alon Asphalt Company (Paramount Petroleum)', 
        'Kinder Morgan Liquids Terminal - Harbor Island',
        'Tesoro Pasco Terminal', 'REG Grays Harbor, LLC', 
        'Tidewater Vancouver Terminal',
        'TLP Management Services LLC (TMS)',
        'US'
    ]
    oil_template_names = [
        'Lagrangian_akns.dat','Lagrangian_bunker.dat',
         'Lagrangian_diesel.dat','Lagrangian_gas.dat',
         'Lagrangian_jet.dat','Lagrangian_dilbit.dat',
         'Lagrangian_other.dat'
    ]
    oil_types = [
        'ANS','Bunker-C',
        'Diesel','Gasoline',
        'Jet Fuel', 'Dilbit', 
        'Other'
    ]
    
    # open montecarlo spills file
    mcdf = pandas.read_csv(monte_carlo_csv)
    # replace Lagrangian template file names with oil type tags
    mcdf['Lagrangian_template'] = mcdf['Lagrangian_template'].replace(
        oil_template_names, 
        oil_types
    )

    # query dataframe for infromation on oil capacities by types and vessel
    mc_capacity = mcdf.loc[
        (mcdf.vessel_type == vessel) &
        (mcdf.fuel_cargo == 'cargo') &
        (mcdf.vessel_origin.isin(origin_dest_names) | 
         mcdf.vessel_dest.isin(origin_dest_names) ),
        ['cargo_capacity', 'vessel_origin', 'vessel_dest', 'Lagrangian_template']
    ]
    # add up oil capacities by vessel and oil types
    mc_capacity_byoil = (
        mc_capacity.groupby(
            'Lagrangian_template'
        ).cargo_capacity.sum()
    )
    
    return mc_capacity_byoil
            
def get_ECY_oilclassification(ECY_xls):
    """
    PURPOSE: To identify all the names of oils in ECY database that we attribute 
        to our oil type classifications. 
    ECY_xls: Path to ECY spreadsheet (MuellerTrans4-30-20.xlsx, for our study) 
    
    TO DO: 
        Replace for-loop with more pythonic dataframe query method
    """
    
    # list names of oil classifications used in our study
    oil_types    = [
        'akns', 'bunker', 'dilbit', 
        'jet', 'diesel', 'gas', 'other'
    ]
    # initialize output
    oil_classification = {}
    for oil in oil_types:
        oil_classification[oil] = []
    # read in data
    df = pandas.read_excel(
        ECY_xls,
        sheet_name='Vessel Oil Transfer', 
        usecols="G,H,P,Q,R,W,X"
    )
    # Loop through data and identify names of oils in the ECY database that 
    # we classify as being in one of our oil-type categories.
    [nrows,ncols] = df.shape
    for row in range(nrows):
        if 'CRUDE' in df.Product[row] and df.Product[row] not in oil_classification['akns']:
            oil_classification['akns'].append(df.Product[row])
        elif 'BAKKEN' in df.Product[row] and df.Product[row] not in oil_classification['akns']:
            oil_classification['akns'].append(df.Product[row])
        elif 'BUNKER' in df.Product[row] and df.Product[row] not in oil_classification['bunker']:
            oil_classification['bunker'].append(df.Product[row])
        elif 'BITUMEN' in df.Product[row] and df.Product[row] not in oil_classification['dilbit']:
            oil_classification['dilbit'].append(df.Product[row])
        elif 'DIESEL' in df.Product[row] and df.Product[row] not in oil_classification['diesel']:
            oil_classification['diesel'].append(df.Product[row])
        elif 'GASOLINE' in df.Product[row] and df.Product[row] not in oil_classification['gas']:
            oil_classification['gas'].append(df.Product[row])
        elif 'JET' in df.Product[row] and df.Product[row] not in oil_classification['jet']:
            oil_classification['jet'].append(df.Product[row])
        elif ('CRUDE' not in df.Product[row] and
              'BAKKEN' not in df.Product[row] and
              'BUNKER' not in df.Product[row] and
              'BITUMEN' not in df.Product[row] and
              'DIESEL' not in df.Product[row] and
              'GASOLINE' not in df.Product[row] and
              'JET' not in df.Product[row] and
              df.Product[row] not in oil_classification['other']):
            oil_classification['other'].append(df.Product[row])
    return oil_classification            
            
def get_ECY_exports(ECY_xls, fac_xls, facilities='selected'):
    """
    Returns total gallons exported by vessel type and oil classification 
    to/from WA marine terminals used in our study
    ECY_xls[Path obj. or string]: Path(to Dept. of Ecology transfer dataset)
    facilities [string]: 'all' or 'selected'
    """
    # convert inputs to lower-case
    #transfer_type = transfer_type.lower()
    facilities = facilities.lower() 
    
    print('get_ECY_exports: not yet tested with fac_xls as input')
    # Import Department of Ecology data: 
    df = get_ECY_df(ECY_xls,fac_xls)
    
    # get list of oils grouped by our monte_carlo oil types
    oil_types = [
        'akns', 'bunker', 'dilbit', 
        'jet', 'diesel', 'gas', 'other'
    ]
    oil_classification = get_ECY_oilclassification(ECY_xls)
    
    #  SELECTED FACILITIES
    export={}
    if facilities == 'selected':
        
        # The following list includes facilities used in Casey's origin/destination 
        # analysis with names matching the Dept. of Ecology (ECY) database.  
        # For example, the shapefile "Maxum Petroleum - Harbor Island Terminal" is 
        # labeled as 'Maxum (Rainer Petroleum)' in the ECY database.  I use the 
        # Ecology language here and will need to translate to Shapefile speak

        # If facilities are used in output to compare with monte-carlo transfers
        # then some terminals will need to be grouped, as they are in the monte carlo. 
        # Terminal groupings in the voyage joins are: (1)
        # 'Maxum (Rainer Petroleum)' and 'Shell Oil LP Seattle Distribution Terminal' 
        # are represented in
        #  ==>'Kinder Morgan Liquids Terminal - Harbor Island', and 
        # (2) 'Nustar Energy Tacoma' => 'Phillips 66 Tacoma Terminal'
        facility_names = [ 
            'Alon Asphalt Company (Paramount Petroleum)',
            'Andeavor Anacortes Refinery (formerly Tesoro)',
            'BP Cherry Point Refinery', 
            'Kinder Morgan Liquids Terminal - Harbor Island' ,  
            'Maxum (Rainer Petroleum)',
            'Naval Air Station Whidbey Island (NASWI)',
            'NAVSUP Manchester',
            'Nustar Energy Tacoma',
            'Phillips 66 Ferndale Refinery', 
            'Phillips 66 Tacoma Terminal',      
            'SeaPort Sound Terminal', 
            'Shell Oil LP Seattle Distribution Terminal',
            'Shell Puget Sound Refinery', 
            'Tesoro Port Angeles Terminal','U.S. Oil & Refining',        
            'Tesoro Pasco Terminal', 'REG Grays Harbor, LLC', 
            'Tesoro Vancouver Terminal',
            'Tidewater Snake River Terminal', 
            'Tidewater Vancouver Terminal',
            'TLP Management Services LLC (TMS)'
        ]
        for vessel_type in ['tanker','atb','barge']:
            if vessel_type == 'barge':
                export[vessel_type]={}
                # get exports by oil type
                type_description = ['TANK BARGE','TUGBOAT']
                for oil in oil_types:
                    export[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.ReceiverTypeDescription.isin(type_description)) & 
                    (~df.Receiver.str.contains('ITB')) & 
                    (~df.Receiver.str.contains('ATB')) &
                    (df.Deliverer.isin(facility_names)) & 
                    (df.Product.isin(oil_classification[oil])), 
                    ['TransferQtyInGallon', 'Product']
                ].TransferQtyInGallon.sum()

            elif vessel_type == 'tanker':
                export[vessel_type]={}
                # get exports by oil type
                type_description = ['TANK SHIP']
                for oil in oil_types:
                    export[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.ReceiverTypeDescription.isin(type_description)) &
                        (df.Deliverer.isin(facility_names)) &
                        (df.Product.isin(oil_classification[oil])),
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()

            elif vessel_type == 'atb':
                export[vessel_type]={}
                # get exports by oil type
                type_description = ['TANK BARGE','TUGBOAT']  
                for oil in oil_types:
                    export[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.ReceiverTypeDescription.isin(type_description)) &
                        (df.Receiver.str.contains('ITB') | 
                         df.Receiver.str.contains('ATB')) & 
                        (df.Deliverer.isin(facility_names))&
                        (df.Product.isin(oil_classification[oil])),
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()

    return export

def get_ECY_quantity_byfac(ECY_xls, fac_xls, facilities='selected'):
    """
    Returns total gallons of combined imports and exports 
    by vessel type and oil classification to/from WA marine terminals 
    used in our study.
    
    ECY_xls[Path obj. or string]: Path(to Dept. of Ecology transfer dataset)
    facilities [string]: 'all' or 'selected'
    """
    
    # convert inputs to lower-case
    #transfer_type = transfer_type.lower()
    facilities = facilities.lower() 
      
    # Import Department of Ecology data: 
    print('get_ECY_quantity_byfac: not yet tested with fac_xls as input')
    df = get_ECY_df(ECY_xls, fac_xls)
    
    # get list of oils grouped by our monte_carlo oil types
    oil_types = [
        'akns', 'bunker', 'dilbit', 
        'jet', 'diesel', 'gas', 'other'
    ]
    # names of oil groupings that we want for our output/graphics
    oil_types_graphics = [
        'ANS', 'Bunker-C', 'Dilbit',
        'Jet Fuel', 'Diesel', 'Gasoline',
        'Other'
    ]
    oil_classification = get_ECY_oilclassification(ECY_xls)
    
    #  SELECTED FACILITIES
    exports={}
    imports={}
    combined={}
    if facilities == 'selected':
        
        # The following list includes facilities used in Casey's origin/destination 
        # analysis with names matching the Dept. of Ecology (ECY) database.  
        # For example, the shapefile "Maxum Petroleum - Harbor Island Terminal" is 
        # labeled as 'Maxum (Rainer Petroleum)' in the ECY database.  I use the 
        # Ecology language here and will need to translate to Shapefile speak

        # If facilities are used in output to compare with monte-carlo transfers
        # then some terminals will need to be grouped, as they are in the monte carlo. 
        # Terminal groupings in the voyage joins are: (1)
        # 'Maxum (Rainer Petroleum)' and 'Shell Oil LP Seattle Distribution Terminal' 
        # are represented in
        #  ==>'Kinder Morgan Liquids Terminal - Harbor Island', and 
        # (2) 'Nustar Energy Tacoma' => 'Phillips 66 Tacoma Terminal'
        facility_names = [ 
            'Alon Asphalt Company (Paramount Petroleum)',
            'Andeavor Anacortes Refinery (formerly Tesoro)',
            'BP Cherry Point Refinery', 
            'Kinder Morgan Liquids Terminal - Harbor Island' ,  
            'Maxum (Rainer Petroleum)',
            'Naval Air Station Whidbey Island (NASWI)',
            'NAVSUP Manchester',
            'Nustar Energy Tacoma',
            'Phillips 66 Ferndale Refinery', 
            'Phillips 66 Tacoma Terminal',      
            'SeaPort Sound Terminal', 
            'Shell Oil LP Seattle Distribution Terminal',
            'Shell Puget Sound Refinery', 
            'Tesoro Port Angeles Terminal','U.S. Oil & Refining',        
            'Tesoro Pasco Terminal', 'REG Grays Harbor, LLC', 
            'Tesoro Vancouver Terminal',
            'Tidewater Snake River Terminal', 
            'Tidewater Vancouver Terminal',
            'TLP Management Services LLC (TMS)'
        ]
        for vessel_type in ['atb','barge','tanker']:
            exports[vessel_type]={}
            imports[vessel_type]={}
            combined[vessel_type]={}
            if vessel_type == 'barge':
                print('Tallying barge quantities')
                # get transfer quantities by oil type
                type_description = ['TANK BARGE','TUGBOAT']
                for oil in oil_types:
                    # exports
                    exports[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.ReceiverTypeDescription.isin(type_description)) & 
                        (~df.Receiver.str.contains('ITB')) & 
                        (~df.Receiver.str.contains('ATB')) &
                        (df.Deliverer.isin(facility_names)) & 
                        (df.Product.isin(oil_classification[oil])), 
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()
                    # imports
                    imports[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.DelivererTypeDescription.isin(type_description)) & 
                        (~df.Deliverer.str.contains('ITB')) & 
                        (~df.Deliverer.str.contains('ATB')) &
                        (df.Receiver.isin(facility_names)) & 
                        (df.Product.isin(oil_classification[oil])), 
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()

            elif vessel_type == 'tanker':
                print('Tallying tanker quantities')
                # get transfer quantities by oil type
                type_description = ['TANK SHIP']
                for oil in oil_types:
                    # exports
                    exports[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.ReceiverTypeDescription.isin(type_description)) &
                        (df.Deliverer.isin(facility_names)) &
                        (df.Product.isin(oil_classification[oil])),
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()
                    # imports
                    imports[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.DelivererTypeDescription.isin(type_description)) &
                        (df.Receiver.isin(facility_names)) &
                        (df.Product.isin(oil_classification[oil])),
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()

            elif vessel_type == 'atb': 
                print('Tallying atb quantities')
                # get transfer quantities by oil type
                type_description = ['TANK BARGE','TUGBOAT']  
                for oil in oil_types:
                    # exports
                    exports[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.ReceiverTypeDescription.isin(type_description)) &
                        (df.Receiver.str.contains('ITB') | 
                         df.Receiver.str.contains('ATB')) & 
                        (df.Deliverer.isin(facility_names))&
                        (df.Product.isin(oil_classification[oil])),
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()
                    # imports
                    imports[vessel_type][oil] = df.loc[
                        (df.TransferType == 'Cargo') &
                        (df.DelivererTypeDescription.isin(type_description)) &
                        (df.Deliverer.str.contains('ITB') | 
                         df.Deliverer.str.contains('ATB')) & 
                        (df.Receiver.isin(facility_names))&
                        (df.Product.isin(oil_classification[oil])),
                        ['TransferQtyInGallon', 'Product']
                    ].TransferQtyInGallon.sum()
            
            # combine imports and exports and convert oil type names to 
            # those we wish to use for graphics/presentations
            # The name change mostly matters for AKNS -> ANS.
            for idx,oil in enumerate(oil_types):                                              
                
                # convert names
                exports[vessel_type][oil_types_graphics[idx]] = (
                    exports[vessel_type][oil]
                )
                imports[vessel_type][oil_types_graphics[idx]] = (
                    imports[vessel_type][oil]
                )
        
                # remove monte-carlo names
                exports[vessel_type].pop(oil)
                imports[vessel_type].pop(oil)
                
                # combine imports and exports
                combined[vessel_type][oil_types_graphics[idx]] = (
                    imports[vessel_type][oil_types_graphics[idx]] + \
                    exports[vessel_type][oil_types_graphics[idx]]
                )
                
    return exports, imports, combined

def get_ECY_quantity(ECY_xls, fac_xls):
    """
    Returns total gallons of all WA transfers by vessel type and oil classification .
    
    ECY_xls[Path obj. or string]: Path(to Dept. of Ecology transfer dataset)
    facilities [string]: 'all' or 'selected'
    """
    
    # Import Department of Ecology data: 
    df = get_ECY_df(ECY_xls, fac_xls)
    
    # get list of oils grouped by our monte_carlo oil types
    oil_types = [
        'akns', 'bunker', 'dilbit', 
        'jet', 'diesel', 'gas', 'other'
    ]
    # names of oil groupings that we want for our output/graphics
    oil_types_graphics = [
        'ANS', 'Bunker-C', 'Dilbit',
        'Jet Fuel', 'Diesel', 'Gasoline',
        'Other'
    ]
    oil_classification = get_ECY_oilclassification(ECY_xls)
    
    #  SELECTED FACILITIES
    imports={}
    exports={}
    combined={}

    for vessel_type in ['atb','barge','tanker']:
        combined[vessel_type]={}
        imports[vessel_type]={}
        exports[vessel_type]={}
        if vessel_type == 'barge':
            print('Tallying barge quantities')
            # get transfer quantities by oil type
            type_description = ['TANK BARGE','TUGBOAT']
            for oil in oil_types:
                # exports
                exports[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.ReceiverTypeDescription.isin(type_description)) & 
                    (~df.Receiver.str.contains('ITB')) & 
                    (~df.Receiver.str.contains('ATB')) & 
                    (df.Product.isin(oil_classification[oil])), 
                    ['TransferQtyInGallon', 'Product', 'Region']
                ].TransferQtyInGallon.sum()
                # imports
                imports[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.DelivererTypeDescription.isin(type_description)) & 
                    (~df.Deliverer.str.contains('ITB')) & 
                    (~df.Deliverer.str.contains('ATB')) & 
                    (df.Product.isin(oil_classification[oil])), 
                    ['TransferQtyInGallon', 'Product', 'Region']
                ].TransferQtyInGallon.sum()

        elif vessel_type == 'tanker':
            print('Tallying tanker quantities')
            # get transfer quantities by oil type
            type_description = ['TANK SHIP']
            for oil in oil_types:
                # exports
                exports[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.ReceiverTypeDescription.isin(type_description)) &
                    (df.Product.isin(oil_classification[oil])),
                    ['TransferQtyInGallon', 'Product', 'Region']
                ].TransferQtyInGallon.sum()
                # imports
                imports[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.DelivererTypeDescription.isin(type_description)) &
                    (df.Product.isin(oil_classification[oil])),
                    ['TransferQtyInGallon', 'Product', 'Region']
                ].TransferQtyInGallon.sum()

        elif vessel_type == 'atb': 
            print('Tallying atb quantities')
            # get transfer quantities by oil type
            type_description = ['TANK BARGE','TUGBOAT']  
            for oil in oil_types:
                # exports
                exports[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.ReceiverTypeDescription.isin(type_description)) &
                    (df.Receiver.str.contains('ITB') | 
                     df.Receiver.str.contains('ATB')) &
                    (df.Product.isin(oil_classification[oil])),
                    ['TransferQtyInGallon', 'Product', 'Region']
                ].TransferQtyInGallon.sum()
                # imports
                imports[vessel_type][oil] = df.loc[
                    (df.TransferType == 'Cargo') &
                    (df.DelivererTypeDescription.isin(type_description)) &
                    (df.Deliverer.str.contains('ITB') | 
                     df.Deliverer.str.contains('ATB')) &
                    (df.Product.isin(oil_classification[oil])),
                    ['TransferQtyInGallon', 'Product', 'Region']
                ].TransferQtyInGallon.sum()

        # combine imports and exports and convert oil type names to 
        # those we wish to use for graphics/presentations
        # The name change mostly matters for AKNS -> ANS.
        for idx,oil in enumerate(oil_types):                                              

            # convert names
            exports[vessel_type][oil_types_graphics[idx]] = (
                exports[vessel_type][oil]
            )
            imports[vessel_type][oil_types_graphics[idx]] = (
                imports[vessel_type][oil]
            )

            # remove monte-carlo names
            exports[vessel_type].pop(oil)
            imports[vessel_type].pop(oil)

            # combine imports and exports
            combined[vessel_type][oil_types_graphics[idx]] = (
                imports[vessel_type][oil_types_graphics[idx]] + \
                exports[vessel_type][oil_types_graphics[idx]]
            )
                
    return exports, imports, combined