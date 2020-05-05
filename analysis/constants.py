from collections import OrderedDict
import json

# Set to True to output intermediate rasters for validation (uncomment in map.raster module)
# Set to True to output /tmp/test.html for reports
DEBUG = False

DATA_CRS = "EPSG:5070"
GEO_CRS = "EPSG:4326"
MAP_CRS = "EPSG:3857"

ACRES_PRECISION = 1
# meters to acres
M2_ACRES = 0.000247105
M_MILES = 0.000621371


# indexed by BP value
BLUEPRINT = json.loads("ui/config/blueprint.json")


BLUEPRINT_COLORS = {
    i: entry["color"] for i, entry in enumerate(BLUEPRINT) if "color" in entry
}

ECOSYSTEMS = [
    {
        "id": "beachanddune",
        "value": 0,
        "label": "Beach and dune",
        "indicators": ["beachbirds", "unalteredbeach"],
        "description": "Beaches and dunes occur along the Atlantic and Gulf shorelines. The system extends from the nearshore ocean across sand, gravel, or shell intertidal beaches, and into more stable and vegetated dunes. Waves, wind, and currents constantly shape these dynamic coastal features, which provide wildlife habitat, storm protection, and recreational opportunities.",
    },
    {
        "id": "estuarine",
        "value": 1,
        "label": "Estuarine",
        "indicators": ["coastalcondition", "watervegetationedge", "wetlandpatchsize"],
        "description": "Estuaries are partially enclosed coastal water bodies where freshwater rivers meet the ocean. This system extends upstream into tidal flats and salt marshes, and seaward to the estuary mouth. Nutrient-rich sediment and brackish water make estuaries extremely productive fish and crab nurseries, while salt marshes filter water and buffer coastal storms.",
    },
    {
        "id": "forestedwetland",
        "value": 2,
        "label": "Forested wetland",
        "indicators": ["amphibians", "birds", "extent"],
        "description": "These frequently flooded swamp forests occur across the region on both organic soils, like peatland pocosins and Carolina Bays, and mineral soils, like bottomland hardwood and floodplain forests. Though historically drained for timber production and agriculture, intact forested wetlands support ecological diversity and enhance water quality by filtering polluted runoff.",
    },
    {
        "id": "freshwatermarsh",
        "value": 3,
        "label": "Freshwater marsh",
        "indicators": ["birds", "extent"],
        "description": "Nontidal freshwater marshes occur throughout the geography in poorly-drained depressions, including waterfowl impoundments. Tidal freshwater marshes occur along the upper tidal reaches of coastal rivers. Characterized by regular flooding and low-growing vegetation, freshwater marshes harbor diverse reptile and amphibian populations. They also support recreational hunting and traditional Gullah sweetgrass harvest.",
    },
    {
        "id": "maritimeforest",
        "value": 4,
        "label": "Maritime forest",
        "indicators": ["extent"],
        "description": "Maritime forests are scattered throughout the South Atlantic coast, found on barrier islands and behind estuaries and dunes where migratory songbirds often refuel. Harsh salt spray and wind exposure shape these unique scrub-shrub and wooded communities. They naturally stabilize the coastline and provide critical storm protection, preventing excessive erosion.",
    },
    {
        "id": "pineandprairie",
        "value": 5,
        "label": "Pine and prairie",
        "indicators": ["amphibians", "birds", "regularlyburnedhabitat"],
        "description": "Distributed across the Coastal Plain and occasional Piedmont areas, this fireadapted ecosystem encompasses longleaf, loblolly, and slash forests, as well as open pine savannas and prairies. It is integral to the region’s economy, culture, and natural heritage, driving timber production, harboring rare species, and supporting quail hunting and native tribal traditions.",
    },
    {
        "id": "uplandhardwood",
        "value": 6,
        "label": "Upland hardwood",
        "indicators": ["birds", "urbanopenspace"],
        "description": "This ecosystem includes Piedmont wooded communities ranging from dry upland forests to moist forests next to floodplains. Deciduous hardwood trees adapted to less frequent fire typically dominate, mixed with pine. Most major urban centers occur in upland hardwood forests, which causes habitat fragmentation but also provides many people opportunities to appreciate nature.",
    },
    {
        "id": "marine",
        "value": 7,
        "label": "Marine",
        "indicators": ["birds", "mammals", "potentialhardbottomcondition"],
        "description": "The marine environment starts at either the estuary mouth or the shoreline and stretches 200 miles into the ocean, covering the extent of U.S. waters. The marine ecosystem comprises about half of the South Atlantic geography! From deepwater coral formations to right whale calving grounds, this vast expanse of open water and benthic habitat sustains coastal tourism, commerce, and fisheries.",
    },
    {
        "id": "waterbodies",
        "value": 8,
        "label": "Inland waterbodies",
        "indicators": [],
        "description": "",  # not displayed, no description needed
    },
    # region-wide ecosystems
    {
        "id": "freshwateraquatic",
        "label": "Freshwater aquatic",
        "indicators": [
            "imperiledaquaticspecies",
            "permeablesurface",
            "riparianbuffers",
        ],
        "description": "This ecosystem includes the lakes, rivers, and streams throughout the region that drain to the Atlantic Ocean and Gulf of Mexico. Water quality, quantity, and timing define a healthy freshwater environment, which provides clean drinking water and fishable and swimmable streams for human use while also supporting mussel and fish populations.",
        "extent": "region",
    },
    {
        "id": "landscapes",
        "label": "Landscapes",
        "indicators": [
            "lowroaddensitypatches",
            "lowurbanhistoric",
            "resilientbiodiversityhotspots",
        ],
        "description": "This system focuses on connections across all terrestrial habitats, from uplands to the shoreline. A functional landscape knits together biodiversity hotspots, large habitat patches, and cultural features. This ecologically connected network creates a healthy environment for wildlife and people alike that is resilient to threats like climate change and urbanization.",
        "extent": "region",
    },
    {
        "id": "waterscapes",
        "label": "Waterscapes",
        "indicators": ["migratoryfishconnectivity", "networkcomplexity"],
        "description": "This system focuses on connections between freshwater and saltwater—the flow of water from lakes and rivers, through marshes and estuaries, eventually to the ocean. Energy, agriculture, cities, shipping, and fisheries all depend on water. These competing uses limit water availability and interfere with natural processes like fish passage and natural seasonal flooding.",
        "extent": "region",
    },
]


INDICATORS = [
    {
        "id": "beachanddune_beachbirds",
        "filename": "BeachAndDune_BeachBirds_V_2_2_BinnedClip.tif",
        "label": "Beach birds",
        "values": {
            1: "Below the 20th percentile of importance for bird index species",
            2: "20th - 40th percentile of importance",
            3: "40th - 60th percentile of importance",
            4: "60th - 80th percentile of importance",
            5: "Above the 80th percentile of importance for bird index species (American oystercatcher, Wilson's plover, least tern, and piping plover)",
        },
        # This is a ramp, colors are approximate
        "colors": {
            1: "#F3FD7E",
            2: "#EFCA4F",
            3: "#EAA72F",
            4: "#B86512",
            5: "#6B0002",
        },
        "domain": [10, 100],
        "datasetID": "8331dd16ec304f7695bffcb1e835444e",
        "description": "Beach birds is a continuous index of habitat suitability for four shorebird species (Wilson's plover, American oystercatcher, least tern, piping plover). The relative use of beach habitat by these species for nesting, foraging, and breeding is an indicator of beach quality.",
        "caption": "Beach bird indicator values within the beach and dune ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "beachanddune_unalteredbeach",
        "filename": "BeachAndDune_UnalteredBeach_V_2_2Clip.tif",
        "label": "Unaltered beach",
        "values": {
            0: "Vulnerable to alteration, with/without nearby jetties/groins",
            1: "Less vulnerable with nearby jetties/groins",
            2: "Less vulnerable without nearby jetties/groins",
        },
        "colors": {0: "#FDBDFF", 1: "#DC57DD", 2: "#B800BB"},
        "domain": [0, 2],
        "goodThreshold": 2,
        "datasetID": "e9603ae3c1e545edaff95dc14231f428",
        "description": "Unaltered beach is an index of impacts from hardened structures like jetties, groins, and human infrastructure. Shoreline infrastructure degrades beach habitat, impedes beach migration and barrier island rollover processes, and can cause erosion.",
        "caption": "Unaltered beach indicator values within the beach ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "estuarine_coastalcondition",
        "filename": "Estuarine_CoastalCondition_V_2_1_BinnedClip.tif",
        "label": "Coastal condition",
        "values": {
            1: "Poor",
            2: "Fair to poor",
            3: "Fair",
            4: "Good to fair",
            5: "Good condition for index (water quality, sediment quality, and benthic community condition)",
        },
        # ramp; approximate
        "colors": {
            1: "#ACE3EF",
            2: "#6BA5E6",
            3: "#3B81DE",
            4: "#3344BC",
            5: "#230091",
        },
        "domain": [1, 5],
        "goodThreshold": 4,
        "datasetID": "a2fddbed78a64e73bbb5ed99b114f5f7",
        "description": "Coastal condition is a continuous index of water quality, sediment quality, and benthic community condition that reflects the overall abiotic status of open water estuaries and estuarine marsh. Developed by the Environmental Protection Agency (EPA), these measures capture human impacts on the environment like nonpoint source pollution.",
        "caption": "Coastal condition indicator values within the estuarine ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "estuarine_watervegetationedge",
        "filename": "EstuarineMarsh_Water_VegetationEdge_V_2_0Clip.tif",
        "label": "Water - vegetation edge",
        "values": {
            0: "0 - 0.61 km/sq km",
            1: "0.61 - 1.68 km/sq km",
            2: "1.68 - 2.82 km/sq km",
            3: "2.82 - 4.27 km/sq km",
            4: "4.27 - 19.42 km/sq km",
        },
        "colors": {
            0: "#F8CBF4",
            1: "#DB8DAF",
            2: "#B95977",
            3: "#9B2E4D",
            4: "#7B022B",
        },
        "domain": [0, 4],
        "datasetID": "00ecbf6049d4481db1f1416e4e3b8cc2",
        "description": "Water-vegetation edge is an index of edge length between open water and vegetation where estuarine waters meet wetland marshes. This zone is highly productive for shrimp, crab, fish, and other nekton and provides valuable foraging habitat for marsh birds. ",
        "caption": "Water-vegetation edge indicator values within the estuarine marsh ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "estuarine_wetlandpatchsize",
        "filename": "EstuarineMarsh_WetlandPatchSize_V_2_0Clip.tif",
        "label": "Wetland patch size",
        "values": {
            0: "1 - 328 ha",
            1: "329 - 1,228 ha",
            2: "1,229 - 3,087 ha",
            3: "3,088 - 6,088 ha",
            4: "6,088 - 15,154 ha",
        },
        "colors": {
            0: "#C1F4E5",
            1: "#98EBC9",
            2: "#73DFAE",
            3: "#4FD396",
            4: "#2CC87F",
        },
        "domain": [0, 4],
        "datasetID": "00ecbf6049d4481db1f1416e4e3b8cc2",
        "description": "Wetland patch size is an index based on the size of wetland patches. Larger, better connected wetland patches benefit fish and marsh birds and protect inland areas from waves during storm events.",
        "caption": "Wetland patch size indicator values within the estuarine marsh ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "forestedwetland_amphibians",
        "filename": "ForestedWetland_Amphibians_V_2_1Clip.tif",
        "label": "Forested wetland amphibians",
        "values": {
            0: "Not a Priority Amphibian and Reptile Conservation Area (PARCA) within forested wetlands",
            1: "Priority Amphibian and Reptile Conservation Area (PARCA) within forested wetlands",
        },
        "colors": {0: "#A3FF73", 1: "#568C00"},
        "domain": [0, 1],
        "datasetID": "7971445641934255b319b5971600eb47",
        "description": "Forested wetland amphibians draws from the Priority Amphibian and Reptile Conservation Areas (PARCAs) located in forested wetland habitat. PARCA is an expert-driven, nonregulatory designation that captures places capable of supporting viable amphibian and reptile populations. PARCAs include areas where rare or at-risk species have been observed or are likely to occur (like embedded, isolated wetlands).",
        "caption": "Forested wetland amphibians indicator values within the forested wetland ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "forestedwetland_birds",
        "filename": "ForestedWetland_Birds_V_2_1Clip.tif",
        "label": "Forested wetland birds",
        "values": {
            0: "Less potential for presence of bird index species",
            1: "Potential for presence of Northern parula,black-throated green warbler,red-headed woodpecker, or Chuck-will's widow",
            2: "Potential for additional presence of prothonotary warbler",
            3: "Potential for additional presence of Swainson's warbler",
        },
        "colors": {0: "#FFFFB1", 1: "#FDB309", 2: "#FC5908", 3: "#B93304"},
        "domain": [0, 3],
        "goodThreshold": 1,
        "datasetID": "ecf2d74a50cc47fa99ae6ef42d838866",
        "description": "Forested wetland birds is an index of habitat suitability for six bird species (Northern parula, black-throated green warbler, red-headed woodpecker, Chuck-will's widow, prothonotary warbler, Swainson's warbler) based on patch size and proximity to water. The needs of these species are increasingly restrictive at higher index values, reflecting better quality habitat.",
        "caption": "Forested wetland birds indicator values within the forested wetland ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "forestedwetland_extent",
        "filename": "ForestedWetland_Extent_V_2_2_NoDataTo0_ClipToEcosystemMaskClip.tif",
        "label": "Forested wetland extent",
        "values": {
            0: "Not currently forested wetland (within forested wetland ecosystem)",
            1: "Currently forested wetland (within forested wetland ecosystem)",
        },
        "colors": {1: "#083F28"},
        "domain": [0, 1],
        "datasetID": "72e6a105442444679fc61714feec49b4",
        "description": "Forested wetland extent represents the amount of overall acres of existing forested wetlands present in the South Atlantic geography. Overall acreage of existing forested wetlands provides an indicator of whether forested wetlands being inundated by sea level rise are being replaced or restored somewhere else.",
        "caption": "Forested wetland extent indicator values within the forested wetland ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "freshwatermarsh_birds",
        "filename": "FreshwaterMarsh_Birds_V_2_1_BinnedClip.tif",
        "label": "Freshwater marsh birds",
        "values": {
            1: "Less potential for presence of bird index species",
            2: "Potential for presence of least bittern, Northern pintail, and Northern shoveler",
            3: "Potential for additional presence of king rail",
        },
        # ramp; approximate
        "colors": {1: "#FDAC09", 2: "#FB0041", 3: "#8900E6"},
        "domain": [0, 11907],
        "goodThreshold": 2,  # NOTE: based on values not domain!
        "units": "ha",
        "datasetID": "785b6209bae6492ba080df35c40cc5ba",
        "description": "Freshwater marsh birds is a continuous index of patch size. Larger patches are likely to support the following suite of freshwater marsh birds: least bittern, Northern pintail, Northern shoveler, and king rail.",
        "caption": "Freshwater marsh birds indicator values within the freshwater marsh ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "freshwatermarsh_extent",
        "filename": "FreshwaterMarsh_Extent_V_2_2_NoDataTo0_ClipToEcosystemMaskClip.tif",
        "label": "Freshwater wetland extent",
        "values": {
            0: "Not currently freshwater marsh (within extent of freshwater marsh ecosystem)",
            1: "Currently freshwater marsh (within extent of freshwater marsh ecosystem)",
        },
        "colors": {1: "#607835"},
        "domain": [0, 1],
        "datasetID": "72e6a105442444679fc61714feec49b4",
        "description": "Forested wetland extent represents the amount of overall acres of existing forested wetlands present in the South Atlantic geography. Overall acreage of existing forested wetlands provides an indicator of whether forested wetlands being inundated by sea level rise are being replaced or restored somewhere else.",
        "caption": "Forested wetland extent indicator values within the forested wetland ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "maritimeforest_extent",
        "filename": "MaritimeForest_Extent_V_2_0_NoDataTo0_ClipToEcosystemMaskClip.tif",
        "label": "Maritime forest extent",
        "values": {
            0: "Not currently maritime forest (within extent of maritime forest ecosystem)",
            1: "Currently maritime forest (within extent of maritime forest ecosystem)",
        },
        "colors": {1: "#00734B"},
        "domain": [0, 1],
        "datasetID": "a5969b1b865b470482071d5ff2b1bbbc",
        "description": "Maritime forest extent represents the overall acres of maritime forest currently present in the South Atlantic geography. Since maritime forest has been substantially reduced from its historic extent, protecting the remaining acreage of existing maritime forest is important.",
        "caption": "Maritime forest extent indicator values within the maritime forest ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "pineandprairie_amphibians",
        "filename": "PineAndPrairie_Amphibians_V_2_1Clip.tif",
        "label": "Pine and prairie amphibians",
        "values": {
            0: "Not a Priority Amphibian and Reptile Conservation Area (PARCA) within pine and prairie",
            1: "Priority Amphibian and Reptile Conservation Area (PARCA) within pine and prairie",
        },
        "colors": {0: "#D1FF73", 1: "#5D9100"},
        "domain": [0, 1],
        "datasetID": "89c74fcd28b14683ae2322211104e56c",
        "description": "Pine and prairie amphibians draws from the Priority Amphibian and Reptile Conservation Areas (PARCAs) located in pine and prairie habitat. PARCA is an expert-driven, nonregulatory designation that captures places capable of supporting viable amphibian and reptile populations. PARCAs include areas where rare or at-risk species have been observed or are likely to occur (like embedded, isolated wetlands).",
        "caption": "Pine and prairie amphibians indicator values within the pine and prairie ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "pineandprairie_birds",
        "filename": "PineAndPrairie_Birds_V_2_1Clip.tif",
        "label": "Pine and prairie birds",
        "values": {
            0: "Less potential for presence of bird index species",
            1: "Potential for presence of 1 bird index species",
            2: "Potential for presence of 2 bird index species",
            3: "Potential for presence of all 3 bird index species (Bachman's sparrow, bobwhite quail, and red-cockaded woodpecker)",
        },
        "colors": {0: "#E5D5F2", 1: "#C184C7", 2: "#A82A84", 3: "#730038"},
        "domain": [0, 3],
        "goodThreshold": 1,
        "datasetID": "68f3ce917278453a82afcd280b5ec84b",
        "description": "Pine and prairie birds is an index of habitat suitability for three bird species (Northern bobwhite, red-cockaded woodpecker, Bachman's sparrow) based on observational data and predictive models. The presence of all three species indicates high pine ecosystem quality.",
        "caption": "Pine and prairie birds indicator values within the pine and prairie ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "pineandprairie_regularlyburnedhabitat",
        "filename": "PineAndPrairie_RegularlyBurnedHabitat_V_2_0Clip.tif",
        "label": "Regularly burned habitat",
        "values": {
            0: "Not recently burned or not open canopy",
            1: "Recently burned and open canopy",
        },
        "colors": {
            # 0: "#E1E1E1", # not sufficiently visible on basemap
            0: "#ccece6",
            1: "#FF0000",
        },
        "domain": [0, 1],
        "goodThreshold": 1,
        "datasetID": "ea13b5d4f83d4e27bc8bfc8878a85b2c",
        "description": "Regularly burned habitat is an indicator of acres of fire-maintained, open canopy habitat. It attempts to capture recent fire in the pine ecosystem by using LANDFIRE data (1999-2010) as a proxy for regularly burned habitat.",
        "caption": "Regularly burned habitat indicator values within the pine and prairie ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "uplandhardwood_birds",
        "filename": "UplandHardwood_Birds_V_2_0Clip.tif",
        "label": "Upland hardwood birds",
        "values": {
            0: "Less potential for presence of bird index species",
            1: "Potential for presence of wood thrush or whip-poor-will",
            2: "Potential for additional presence of hooded warbler or American woodcock",
            3: "Potential for additional presence of Acadian flycatcher or Kentucky warbler",
            4: "Potential for additional presence of Swainson's warbler",
        },
        "colors": {
            0: "#FFBAE0",
            1: "#FF8FDF",
            2: "#FA4784",
            3: "#A80084",
            4: "#690042",
        },
        "domain": [0, 4],
        "goodThreshold": 3,
        "datasetID": "9a98b3bf45fc4d2aa0833a171b56533a",
        "description": "Upland hardwood birds is an index of habitat suitability for seven upland hardwood bird species (wood thrush, whip-poor-will, hooded warbler, American woodcock, Acadian flycatcher, Kentucky warbler, Swainson's warbler) based on patch size and other ecosystem characteristics such as proximity to water and proximity to forest and ecotone edge. The needs of these species are increasingly restrictive at higher index values, reflecting better quality habitat.",
        "caption": "Upland hardwood birds indicator values within the upland hardwood ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "uplandhardwood_urbanopenspace",
        "filename": "UplandHardwood_UrbanOpenSpace_V_2_1Clip.tif",
        "label": "Urban open space",
        "values": {
            0: "Existing development",
            1: "Undeveloped area less than 400 m from protected land",
            2: "Undeveloped area 400 - 800 m from protected land",
            3: "Undeveloped area 800 - 1600 m from protected land",
            4: "Undeveloped area greater than 1600 m from protected land",
            5: "Protected land",
        },
        "colors": {
            0: "#B2B2B2",
            1: "#CCECA3",
            2: "#A1D99B",
            3: "#42AB5D",
            4: "#006D2E",
            5: "#003521",
        },
        "domain": [0, 5],
        "datasetID": "c0039f1c66c14115ba8b5f51ee22ef97",
        "description": "Urban open space is an index based on distance of urban areas from open space. This cultural resource indicator is intended to capture equitable access to open space for urban residents. Protected natural areas in urban environments offer refugia for some species while providing people a nearby place to connect with nature.",
        "caption": "Urban open space indicator values within the upland hardwood ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "marine_birds",
        "filename": "Marine_Birds_V_2_2_BinnedClip.tif",
        "label": "Marine birds",
        "values": {
            1: "Below the 20th percentile of importance for seasonal density of marine bird index species",
            2: "20th-40th percentile of importance",
            3: "40th-60th percentile of importance",
            4: "60th-80th percentile of importance",
            5: "Above the 80th percentile of importance for seasonal density of marine bird index species",
        },
        # ramp: approximation
        "colors": {
            1: "#C5FDED",
            2: "#4BB191",
            3: "#0D9571",
            4: "#005C3F",
            5: "#00160B",
        },
        "domain": [0, 100],
        "datasetID": "13aa474921e243e7860c7412d2988b4e",
        "description": "Marine birds is a continuous index of highly productive areas for birds that feed exclusively or mainly at sea. It uses seasonal predictions of relative abundance for sixteen species of marine birds. Marine birds help identify key areas of ocean productivity and complement the marine mammal index by providing finer spatial resolution and stronger connections to forage fish productivity.",
        "caption": "Marine bird indicator values within the marine ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "marine_mammals",
        "filename": "Marine_Mammals_V_2_1_BinnedClip.tif",
        "label": "Marine mammals",
        "values": {
            1: "Below the 20th percentile of importance for seasonal density of marine mammal index species",
            2: "20th - 40th percentile of importance",
            3: "40th - 60th percentile of importance",
            4: "60th - 80th percentile of importance",
            5: "Above the 80th percentile of importance for seasonal density of marine mammal index species",
        },
        # ramp: approximation
        "colors": {
            1: "#E9C4EA",
            2: "#D594EE",
            3: "#C87AEF",
            4: "#B95AF1",
            5: "#9B03F2",
        },
        "domain": [0, 100],
        "datasetID": "be70e3438a6e48d798916e788f35ef6b",
        "description": "Marine mammals is a continuous index of dolphin and whale density based on monthly density predictions for ten species of cetaceans and yearly density predictions for three rarer cetacean species. Marine mammals help identify key areas of ocean productivity and overall ocean health because they have long life spans, feed at high trophic levels, and can accumulate anthropogenic chemicals and toxins in their large blubber stores.",
        "caption": "Marine mammals indicator values within the marine ecosystem in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "marine_potentialhardbottomcondition",
        "filename": "Marine_PotentialHardbottomCondition_V_2_0Clip.tif",
        "label": "Potential hardbottom condition",
        "values": {
            0: "Hardbottom not predicted",
            1: "Hardbottom likely to be stressed by human activities",
            2: "Hardbottom less likely to be stressed by human activities",
            3: "Hardbottom likely to be in best condition due to additional protections",
        },
        "colors": {
            # 0: "#E1E1E1", # not sufficiently visible on basemap
            0: "#fff7bc",
            1: "#73FFDF",
            2: "#00A9E6",
            3: "#002673",
        },
        "domain": [0, 3],
        "goodThreshold": 2,
        "datasetID": "cbb923b746fc435b93d079f9261fa7c2",
        "description": "Potential hardbottom condition measures the protected status or potential stress (i.e., shipping traffic, dredge disposal) of solid substrate and rocky outcroppings. Hardbottom provides an anchor for important seafloor habitat such as deepwater corals, plants, and sponges, supporting associated invertebrate and fish species.",
        "caption": "Potential hardbottom condition indicator values within the marine ecosystem in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "freshwateraquatic_permeablesurface",
        "filename": "FreshwaterAquatic_PermeableSurface_V_2_1_BinnedClip.tif",
        "label": "Permeable surface",
        "values": {
            1: "Less than 70% of catchment permeable, likely degraded instream flow, water quality, and aquatic species communities",
            2: "70 - 90% of catchment permeable, likely degraded water quality and not supporting many aquatic species",
            3: "90 - 95% of catchment permeable, likely declining water quality and supporting most aquatic species",
            4: "Greater than 95% of catchment permeable, likely high water quality and supporting most sensitive aquatic species",
        },
        # ramp: approximation
        "colors": {1: "#DAD5FC", 2: "#C7B3FB", 3: "#8953EE", 4: "#5000E4"},
        "domain": [9, 100],
        "goodThreshold": 4,
        "datasetID": "aff20e09ff62451685dfb8ffedceeec1",
        "description": "Permeable surface is a continuous indicator that measures the percent of non-impervious cover by catchment. High levels of impervious surface degrade water quality and alter freshwater flow.",
        "caption": "Permeable surface indicator values in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "freshwateraquatic_riparianbuffers",
        "filename": "FreshwaterAquatic_RiparianBuffers_V_2_1_BinnedClip.tif",
        "label": "Riparian buffers",
        "values": {
            1: "Less than 80% natural habitat surrounding rivers and streams",
            2: "80 - 85% natural cover",
            3: "85 - 90% natural cover",
            4: "90 - 95% natural cover",
            5: "Greater than 95% natural habitat surrounding rivers and streams",
        },
        # ramp: approximation
        "colors": {
            1: "#F2FE92",
            2: "#00E51B",
            3: "#1EC378",
            4: "#219EB6",
            5: "#260389",
        },
        "domain": [0, 100],
        "goodThreshold": 5,
        "datasetID": "c822c798ba724e06b5fb25d2c18ff0cb",
        "description": "Riparian buffers measures the amount of natural habitat surrounding rivers and streams. This continuous indicator applies to the Active River Area, which spatially defines the dynamic relationship between riverine systems and the lands around them. The Active River Area includes meander belts, riparian wetlands, floodplains, terraces, and material contribution areas. Riparian buffers are strongly linked to water quality as well as water availability (i.e., instream flow).",
        "caption": "Riparian buffers indicator values within the active river area in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "freshwateraquatic_imperiledaquaticspecies",
        "filename": "FreshwaterAquatic_ImperiledAquaticSpecies_V_2_1Clip.tif",
        "label": "Imperiled aquatic species",
        "values": {
            0: "No aquatic imperiled (G1/G2) or threatened/endangered species observed",
            1: "1 aquatic imperiled (G1/G2) or threatened/endangered species observed",
            2: "2 aquatic imperiled (G1/G2) or threatened/endangered species observed",
            3: "3 aquatic imperiled (G1/G2) or threatened/endangered species observed",
            4: "4 or more aquatic imperiled (G1/G2) or threatened/endangered species observed",
        },
        "colors": {
            0: "#FFFFDB",
            1: "#CCFF77",
            2: "#55FF00",
            3: "#387700",
            4: "#387700",
        },
        "domain": [0, 4],
        "datasetID": "f6aa9bc688814468b5ae2772375c9fc2",
        "description": "Imperiled aquatic species measures the number of aquatic species within each watershed that are listed as G1 (globally critically imperiled), G2 (globally imperiled), or threatened/endangered under the U.S. Endangered Species Act. This indicator captures patterns of rare and endemic species diversity not well-represented by other freshwater aquatic indicators. It applies only to the Active River Area, which spatially defines the dynamic relationship between riverine systems and the lands around them; it includes meander belts, riparian wetlands, floodplains, terraces, and material contribution areas.",
        "caption": "Imperiled aquatic species indicator values within the active river area in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "landscapes_lowroaddensitypatches",
        "filename": "Landscapes_LowRoadDensityPatches_V_2_1Clip.tif",
        "label": "Low road density",
        "values": {
            0: "High road density (≥1.5 km/sq km)",
            1: "Low road density (<1.5 km/sq km) ",
        },
        "colors": {0: "#CFCEDE", 1: "#D68589"},
        "domain": [0, 1],
        "goodThreshold": 1,
        "datasetID": "61856f9901d74185a34c08e857380395",
        "description": "Low road density is an index of areas with few roads, measuring the length of roads within a square kilometer area. It represents habitat fragmentation. Extensive road networks are harmful to many species, including reptiles and amphibians, birds, and large mammals.",
        "caption": "Low road density indicator values in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.",
    },
    {
        "id": "landscapes_lowurbanhistoric",
        "filename": "Landscapes_LowUrbanHistoric_V_2_1_SOTClip.tif",
        "label": "Low-urban historic landscapes",
        "values": {
            0: "Historic place with nearby high-urban buffer",
            1: "Historic place with nearby low-urban buffer",
        },
        "colors": {0: "#FF8CC4", 1: "#730000"},
        "domain": [0, 1],
        "goodThreshold": 1,
        "datasetID": "037ecaa254ff48f88969fc1db467d917",
        "description": "Low-urban historic landscapes is an index of sites on the National Register of Historic Places surrounded by limited urban development. This cultural resource indicator identifies significant historic places that remain connected to their context in the natural world.",
        "caption": "Low-urban historic landscapes indicator values within the historic landscapes in this area. Good condition thresholds reflect the range of indicator values that occur in healthy, functioning ecosystems.  Note: Historic landscapes are rare across the South Atlantic. The presence of any historic landscape, even in high-urban condition, will increase the priority in the Blueprint.",
    },
    {
        "id": "landscapes_resilientbiodiversityhotspots",
        "filename": "Landscapes_ResilientBiodiversityHotspots_V_2_2Clip.tif",
        "label": "Resilient biodiversity hotspots",
        "values": {
            0: "Urban",
            1: "Final resilience score: Far below average (<-2 SD)",
            2: "Final resilience score: Below average (-1 to -2 SD)",
            3: "Final resilience score: Slightly below average (-0.5 to -1 SD)",
            4: "Final resilience score: Average (0.5 to -0.5 SD)",
            5: "Final resilience score: Slightly above average (0.5 to 1 SD)",
            6: "Final resilience score: Above average (1 to 2 SD)",
            7: "Final resilience score: Far above average (>2 SD)",
        },
        "colors": {
            0: "#9C9C9C",
            1: "#9C5521",
            2: "#BF874B",
            3: "#E0C09E",
            4: "#FFFFBF",
            5: "#A9C276",
            6: "#5D8A3A",
            7: "#21580B",
        },
        "domain": [0, 7],
        "datasetID": "62f821c124bb418298b0375dfcce830b",
        "description": "Resilient biodiversity hotspots is an index of mostly natural high-diversity areas potentially resilient to climate change. This indicator measures landscape diversity (geophysical features like soil and topography) and local connectedness. Areas with these characteristics will likely continue to support species richness and movement in a changing climate (i.e., are resilient).",
        "caption": "Resilient biodiversity hotspots indicator values in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "waterscapes_migratoryfishconnectivity",
        "filename": "Waterscapes_MigratoryFishConnectivity_V_2_1Clip.tif",
        "label": "Migratory fish connectivity",
        "values": {
            1: "Migratory fish connectivity index species not adjacent/not observed",
            2: "Adjacent to presence of migratory fish connectivity index species",
            3: "Presence of Alabama shad, American shad, blueback herring, or striped bass",
            4: "Presence of Gulf or Atlantic sturgeon",
        },
        "colors": {1: "#D7F2ED", 2: "#74B7AC", 3: "#537A82", 4: "#0B423D"},
        "domain": [1, 4],
        "datasetID": "955b5af8b2e24648a11b4a0134c0b285",
        "description": "Migratory fish connectivity is an index capturing how far upstream migratory fish have been observed. It also includes adjacent areas where habitat access could be restored through fish passage and hydrological barrier removal efforts. Migratory fish presence reflects uninterrupted connections between freshwater, estuarine, and marine ecosystems.",
        "caption": "Migratory fish connectivity indicator values within the active river area in this area. A good condition threshold is not yet defined for this indicator.",
    },
    {
        "id": "waterscapes_networkcomplexity",
        "filename": "Waterscapes_NetworkComplexity_V_2_1Clip.tif",
        "label": "Network complexity",
        "values": {
            1: "1 connected stream size class",
            2: "2 connected stream size classes",
            3: "3 connected stream size classes ",
            4: "4 connected stream size classes ",
            5: "5 connected stream size classes",
            6: "6 connected stream size classes",
            7: "7 connected stream size classes",
        },
        "colors": {
            1: "#FFFFFF",
            2: "#E3D3D3",
            3: "#B59696",
            4: "#8C7777",
            5: "#6B6B6B",
            6: "#353535",
            7: "#000000",
        },
        "domain": [1, 7],
        "datasetID": "88e4e923d1e94e1d833f0cfd5bb93d5e",
        "description": "Network complexity depicts the number of different stream size classes in a river network not separated by large dams. River networks with a variety of connected stream classes help retain aquatic biodiversity in a changing climate by allowing species to access climate refugia and move between habitats.",
        "caption": "Network complexity indicator values within the active river area in this area. A good condition threshold is not yet defined for this indicator.",
    },
]


INDICATORS_INDEX = OrderedDict({indicator["id"]: indicator for indicator in INDICATORS})


URBAN_YEARS = [2020, 2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]

URBAN_LEGEND = [
    None,  # spacer; not actually displayed
    {"label": "Urban in 2009", "color": "#333333"},
    {"label": "< 2.5% probability", "color": "#FFBFBA"},
    {"label": "5%", "color": "#FFB1A8"},
    {"label": "10%", "color": "#FFA496"},
    {"label": "20%", "color": "#FF9787"},
    {"label": "30%", "color": "#FC8B76"},
    {"label": "40%", "color": "#FC806B"},
    {"label": "50%", "color": "#FA735A"},
    {"label": "60%", "color": "#F5654B"},
    {"label": "70%", "color": "#F25740"},
    {"label": "80%", "color": "#F04D35"},
    {"label": "90%", "color": "#EB402A"},
    {"label": "95%", "color": "#E5311B"},
    {"label": "97.5%", "color": "#E12114"},
    {"label": "> 97.5% probability", "color": "#DB0000"},
]


SLR_LEGEND = [
    {"label": "< 1 foot", "color": "#2B00A1"},
    {"label": "1", "color": "#403EB9"},
    {"label": "2", "color": "#4567CF"},
    {"label": "3", "color": "#4495E5"},
    {"label": "4", "color": "#74B0EB"},
    {"label": "5", "color": "#94CBEF"},
    {"label": "≥ 6 feet", "color": "#C0F0F3"},
]


OWNERSHIP = OrderedDict(
    {
        "FED": {"color": "#2ca02c", "label": "Federal"},
        "STP": {"color": "#1f77b4", "label": "State/province"},
        "LOC": {"color": "#aec7e8", "label": "Local"},
        "TNC": {"color": "#98df8a", "label": "The Nature Conservancy"},
        "PNP": {"color": "#ad494a", "label": "Private non-profit"},
        "PFP": {"color": "#ff7f0e", "label": "Private for-profit"},
        "PLO": {"color": "#7D3E07", "label": "Private land owner"},
        "TRB": {"color": "#9467bd", "label": "Tribal"},
        "UNK": {"color": "#c49c94", "label": "Ownership unknown"},
    }
)

PROTECTION = OrderedDict(
    {
        1: {
            "color": "#637939",
            "label": "Permanently protected for biodiversity",
            "description": " Nature reserves, research natural areas, wilderness areas, Forever Wild easements",
        },
        2: {
            "color": "#b5cf6b",
            "label": "Permanently protected to maintain a primarily natural state",
            "description": " National Wildlife Refuges, many State Parks, high-use National Parks",
        },
        3: {
            "color": "#98df8a",
            "label": "Permanently secured for multiple uses and in natural cover",
            "description": " State forests, lands protected from development by forest easements",
        },
        39: {
            "color": "#e7cb94",
            "label": "Permanently secured and in agriculture or maintained grass cover",
            "description": " Agricultural easements",
        },
        4: {
            "color": "#7D3E07",
            "label": "Unsecured (already developed temporary easements and/or municipal lands)",
            "description": " Private lands with no easements, city parks, undesignated state lands ",
        },
        9: {
            "color": "#9edae5",
            "label": "Unknown - protected lands status unknown",
            "description": "Protection status unknown",
        },
    }
)

CORRIDORS = [
    # 0:
    {"color": "#353535", "label": "Inland Hubs"},
    # 1:
    {"color": "#828282", "label": "Inland Corridors"},
    # 2:
    {"color": "#454F89", "label": "Marine Hubs"},
    # 3:
    {"color": "#9EBBD7", "label": "Marine Corridors"},
]