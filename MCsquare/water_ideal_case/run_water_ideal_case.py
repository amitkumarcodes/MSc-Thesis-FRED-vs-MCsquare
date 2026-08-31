import sys
sys.path.append('..')
import os
import SimpleITK as sitk

from opentps.core.data.plan import ProtonPlan, RTPlan
from opentps.core.io.scannerReader import readScanner
from opentps.core.io import mcsquareIO
from opentps.core.io.mhdIO import exportImageMHD
from opentps.core.processing.doseCalculation.doseCalculationConfig import DoseCalculationConfig
from opentps.core.processing.doseCalculation.protons.mcsquareDoseCalculator import MCsquareDoseCalculator
from opentps.core.data.plan._planProtonBeam import PlanProtonBeam
from opentps.core.data.plan._planProtonLayer import PlanProtonLayer
from opentps.core.data.images._ctImage import CTImage
import numpy as np
import matplotlib.pyplot as plt

script_dir = os.path.dirname(os.path.abspath(__file__))
script_name = os.path.splitext(os.path.basename(__file__))[0]

ctCalibration = readScanner(DoseCalculationConfig().scannerFolder)
bdl = mcsquareIO.readBDL(DoseCalculationConfig().bdlFile)

# Loading a copy of bdl file to prevent any modification of 
# ctCalibration = readScanner(DoseCalculationConfig().scannerFolder)
# bdl_path = "/home/amit/opentps/opentps_core/opentps/core/processing/doseCalculation/protons/MCsquare/BDL/BDL_fred_like_pbwater.txt"
# bdl = mcsquareIO.readBDL(bdl_path)
ctSize = 200
#bdl.nozzle_isocenter = 400 # making at same as that of FRED to match the beam model

# Load the water phantom
ct_path = os.path.join(script_dir, "CT_HU_200mm_water.mha")
ct_sitk = sitk.ReadImage(ct_path)
ct_array = sitk.GetArrayFromImage(ct_sitk).astype(np.float32)



ct = CTImage()
ct.name = "200 mm water phantom"
ct.imageArray = ct_array
ct.spacing = ct_sitk.GetSpacing()
ct.origin = ct_sitk.GetOrigin()
huWater = 0.
huWater = ctCalibration.convertRSP2HU(1.)
# data = huWater * np.ones((ctSize, ctSize, ctSize))
# #data[:, :50, :] = huAir
# ct.imageArray = data

#ct.spacing = (1.0, 1.0, 1.0)
voxel_spacing = float(ct.spacing[1])

plan = ProtonPlan()
plan.appendBeam(PlanProtonBeam())
plan.beams[0].gantryAngle = 180
plan.beams[0].appendLayer(PlanProtonLayer(150)) # 150 MeV
plan[0].layers[0].appendSpot([0], [0], [1])

# Why do you do this ctSize*voxel_spacing//2.0 and not just ctSize//2.0?
# total size = N x spacing

plan.beams[0].isocenterPosition = [ctSize*voxel_spacing/2.0, ctSize*voxel_spacing/2.0, ctSize*voxel_spacing/2.0]


#plan.beams[0].isocenterPosition = [149.5, 149.5, 149.5]

#Making the beam as pencil beam with spot size = 0
# to match the beam parameters (twiss) that of fred
#sigma_x = 1.69 # mm
sigma_spatial = 1e-9
bdl.spotSize1x = [sigma_spatial] * len(bdl.nominalEnergy)
bdl.spotSize1y = [sigma_spatial] * len(bdl.nominalEnergy)
bdl.spotSize2x = [sigma_spatial] * len(bdl.nominalEnergy)
bdl.spotSize2y = [sigma_spatial] * len(bdl.nominalEnergy)

# to match the twiss parameter, because this can't be set to zero
#sigma_div = 0.0125 # rad, dimensionless
sigma_div = 1e-9
bdl.divergence1x = [sigma_div] * len(bdl.nominalEnergy)
bdl.divergence1y = [sigma_div] * len(bdl.nominalEnergy)
bdl.divergence2x = [sigma_div] * len(bdl.nominalEnergy)
bdl.divergence2y = [sigma_div] * len(bdl.nominalEnergy)

# Near-monoenergetic beam for Experiment 1
#########################################
tiny_spread_percent = 0.01 / 2.355 / 150 * 100   # from target EFWHM = 0.01 MeV
bdl.energySpread = [tiny_spread_percent] * len(bdl.nominalEnergy)

layer_energy = plan.beams[0].layers[0].nominalEnergy
idx = np.where(bdl.nominalEnergy == layer_energy)[0][0]

sigma = bdl.energySpread[idx] * layer_energy/100
efwhm = 2.355 * sigma

print("before sigma (MeV):", sigma)
print("before EFWHM (MeV):", efwhm)
#############################################

idx = np.where(bdl.nominalEnergy == 150)[0][0]
bdl.meanEnergy[idx] = 150.0


mc2 = MCsquareDoseCalculator()
mc2.beamModel = bdl
mc2.ctCalibration = ctCalibration
mc2.nbPrimaries = 1e7
dose = mc2.computeDose(ct, plan)

dose_output_path = os.path.join(script_dir, f"{script_name}_dose")
exportImageMHD(dose_output_path, dose)
print(f"Dose saved to: {dose_output_path}.mhd")

layer_energy = plan.beams[0].layers[0].nominalEnergy
idx = np.where(bdl.nominalEnergy == layer_energy)[0][0]

print("Nominal energy:", bdl.nominalEnergy[idx])
print("Energy spread used (%):", bdl.energySpread[idx])

sigma = bdl.energySpread[idx] * layer_energy/100
efwhm = 2.355 * sigma
print("after sigma (MeV):", sigma)
print("after EFWHM (MeV):", efwhm)

print("MCsquare actual mean energy:", bdl.meanEnergy[idx])
print("HU values:", np.unique(ct.imageArray))