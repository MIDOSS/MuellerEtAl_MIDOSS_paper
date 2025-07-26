
# oil attributions 
vessels = [
    'atb', 'barge','tanker','cargo','cruise',
    'ferry','fishing','other','smallpass'
]

vesselcolors={
    'atb': 'olive',
    'barge':"darkolivegreen",
    'tanker':'darkslategrey',
    'cargo':"darkgoldenrod",
    'cruise':"darkkhaki",
    'ferry':"cadetblue",
    'fishing':"steelblue",
    'smallpass':"orchid",
    'other':"goldenrod"
}

# *** types, labels, and fnames need to be ordered in the same way ***
types = [
    'akns', 
    'bunker', 
    'dilbit', 
    'diesel',  
    'gas',
    'jet', 
    'other'
]
labels = [
    'ANS', 
    'Bunker-C', 
    'Dilbit', 
    'Diesel', 
    'Gasoline',
    'Jet Fuel', 
    'Other'
]
oil_labels_dict = {"akns":"ANS",
            "oils":"all oils",
           "bunker":"Bunker-C",
           "diesel":"Diesel",
           "dilbit":"Dilbit",
           "gas":"Diesel",
           "jet":"Diesel",
           "other":"Bunker-C"}

oil_types = ["Bunker-C", "Diesel", "Dilbit", "ANS"]

colors = [
    'darkslategrey',
    'teal',
    'slategrey',
    'cornflowerblue',
    'cornflowerblue',
    'cornflowerblue',
    'teal'
]
# fnames = [
#     'Lagrangian_akns.dat',
#     'Lagrangian_bunker.dat',
#     'Lagrangian_dilbit.dat',
#     'Lagrangian_diesel.dat',
#     'Lagrangian_gas.dat',
#     'Lagrangian_jet.dat',
#     'Lagrangian_other.dat'
# ]
# MIDOSSlabels=[
#     'ANS',
#     'Bunker-C',
#     'Dilbit',
#     'Diesel',
#     'Diesel',
#     'Diesel',
#     'Bunker-C'
# ]

# define names used for Lagrangian files
oil_grouping_dict = {
    'Lagrangian_akns.dat':'ANS',
    'Lagrangian_bunker.dat':'Bunker-C',
     'Lagrangian_diesel.dat':'Diesel',
    'Lagrangian_gas.dat':'Diesel',
     'Lagrangian_jet.dat':'Diesel',
    'Lagrangian_dilbit.dat':'Dilbit',
     'Lagrangian_other.dat':'Bunker-C'
}

oil_colors_dict={
    'ANS': 'darkslategrey',
    'Bunker-C':'teal',
    'Dilbit':'slategrey',
    'Diesel':'darkgoldenrod',#'cornflowerblue',
}


# misc.

# color of shoreline
shoreline ='grey'
shorelw = .2

 