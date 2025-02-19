from SeparatedTopologies import make_septop as ms
from SeparatedTopologies import boresch_restraints as br
from SeparatedTopologies import combine_coordinates as ac
from SeparatedTopologies import distance_solvent as ds
import os
import parmed as pmd

##########################
###### input needed  #####
##########################

#path to data folder
path = ''

#ligand folders: name of this folder is considered the ligand name
ligand_A = ''
ligand_B = ''

#directories of ligand input files
compound_A = '%s/%s'%(path, ligand_A)
compound_B = '%s/%s'%(path, ligand_B)

#name of solvent .gro and .top files
gro_A = '%s/solvent.gro'%compound_A
gro_B = '%s/solvent.gro'%compound_B
top_A = '%s/solvent.top'%compound_A
top_B = '%s/solvent.top'%compound_B

#scaling factor gamma
gamma = 0.3

#Create new folder for each edge
edge_A_B = '%s/edge_%s_%s'%(path, ligand_A, ligand_B)
if not os.path.isdir(edge_A_B):os.mkdir(edge_A_B)

#Three letter code for ligands
lig = 'UNL'

##########################
### Combine .gro files ###
##########################

solv_gro = '%s/solvent.gro'%edge_A_B
ac.combine_ligands_gro(gro_A, gro_B, solv_gro, ligand_A=lig, ligand_B=lig)
ac.edit_indices(solv_gro,solv_gro)

###############################
### Make separated topology ###
###############################

#Specify output file names
top = '%s/solvent.top'%edge_A_B
step_1 = '%s/step1.top'%edge_A_B
step_1_eq = '%s/step1_eq.top'%edge_A_B
step_2 = '%s/step2.top'%edge_A_B
step_2_eq = '%s/step2_eq.top'%edge_A_B

#Combine topology ligand B and topology A
ms.combine_ligands_top(top_A, top_B, top, ligand=lig)

# Generate separated topology files different legs cycle
#Four different end states:
        # vdwq_scaled-vdw
        # scaled-vdw_dummy
        # dummy_scaled-vdwq
        # scaled-vdwq_vdwq
#Create complex step 1
ms.create_top(top, step_1, gamma, 'vdwq_scaled-vdw', 'dummy_scaled-vdwq', top_A, top_B, ligand=lig)
ms.create_top(top, step_1_eq, gamma, 'vdwq_scaled-vdw', 'dummy_scaled-vdwq', top_A, top_B, ligand=lig)
#Create complex step 2
ms.create_top(top, step_2, gamma, 'scaled-vdw_dummy', 'scaled-vdwq_vdwq', top_A, top_B, ligand=lig)
ms.create_top(top, step_2_eq, gamma, 'scaled-vdw_dummy', 'scaled-vdwq_vdwq', top_A, top_B, ligand=lig)


##########################################
### Get .itp file for distance restraint #
##########################################

#Load in .top and .gro and save .gro again to fix residue numbers
gro = pmd.load_file(step_1, xyz=solv_gro)
gro.save(solv_gro, overwrite=True)

#equilibrate first with low force constant to avoid instabilities
fc_eq = 1.0
fc_prod = 1000.0

#restrain atoms closest to the COM of the two ligands using a single harmonic distance restraint
atoms_restrain,dist = ds.distance_restraint(solv_gro,lig)
ds.write_itp_restraints(atoms_restrain, dist, fc_eq,fc_eq, '%s/dist_restraint_eq.itp'%edge_A_B)
ds.write_itp_restraints(atoms_restrain, dist, fc_prod,fc_prod, '%s/dist_restraint.itp'%edge_A_B)

#Include .itp files in the topology files
br.include_itp_in_top(step_1, 'dist_restraint.itp')
br.include_itp_in_top(step_1_eq, 'dist_restraint_eq.itp')
br.include_itp_in_top(step_2, 'dist_restraint.itp')
br.include_itp_in_top(step_2_eq, 'dist_restraint_eq.itp')
