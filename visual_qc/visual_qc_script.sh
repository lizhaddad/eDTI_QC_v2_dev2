#!/bin/bash
#$ -cwd
#$ -j y

## ENIGMA-DTI TBSS QC SCRIPT(10/2024)
## Talia Nir, Elizabeth Haddad, Neda Jahanshad

###################################################################################################
########################################## EDIT ME ################################################
###################################################################################################
# (OPTIONAL MASTER DIRECTORY)
dir=/ifs/loni/faculty/njahansh/nerds/ehaddad/ENIGMA/eDTI_qc_testing

# PATH TO SUBJECT LIST TEXT FILE
subject_list=${dir}/example_data/subject_list.txt

# PATH TO ENIGMA DTI TEMPLATE
ENIGMA_FA_Template=${dir}/ENIGMA_DTI_TBSS/ENIGMA_DTI_FA.nii.gz

# PATH TO FOLDER WHERE YOU RAN THE eDTI TBSS PIPELINE
TBSS_run_folder=${dir}/example_tbss_output

# PATH TO THE qc_image_generation_nomask.py SCRIPT 
## (can be downloaded from here **ADD LINK**)
QCpng=${dir}/qc_image_generation_nomask.py

# FILE SUFFIXES
## (assumes you followed the same file/folder structure as the eDTI pipeline; 
##  eg: $subject precedes the name to these files)
FA_SKELETON_NAME="_masked_FAskel.nii.gz"
FA2ENIGMA_NAME="_dti_FA_FA_to_ENIGMA.nii.gz"
MD2ENIGMA_NAME="_MD_to_ENIGMA.nii.gz"
AD2ENIGMA_NAME="_AD_to_ENIGMA.nii.gz"
RD2ENIGMA_NAME="_RD_to_ENIGMA.nii.gz"

# PATH TO PYTHON BINARY
PYTHON=/ifshome/gfleishm/anaconda/bin/python

# PATH TO FSL INSTALLATION
FSLDIR=/usr/local/fsl-6.0.1
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${PATH}:${FSLDIR}/bin:
export FSLDIR PATH
###################################################################################################
###################################################################################################
###################################################################################################

QC_output_folder=${TBSS_run_folder}/QC_output
FAreg=${QC_output_folder}/FA_registration
FAskel=${QC_output_folder}/FA_skeleton
dMRI_FA=${QC_output_folder}/dMRI_maps/FA
dMRI_MD=${QC_output_folder}/dMRI_maps/MD
dMRI_AD=${QC_output_folder}/dMRI_maps/AD
dMRI_RD=${QC_output_folder}/dMRI_maps/RD
mkdir -p ${FAreg} ${FAskel} ${dMRI_FA} ${dMRI_MD} ${dMRI_AD} ${dMRI_RD}

for subject in $(cat ${subject_list}); do	

eval "FA_SKELETON=(${TBSS_run_folder}/FA_individ/${subject}/stats/${subject}${FA_SKELETON_NAME})" 
eval "FA2ENIGMA=(${TBSS_run_folder}/FA_individ/${subject}/FA/${subject}${FA2ENIGMA_NAME})" 
eval "MD2ENIGMA=(${TBSS_run_folder}/MD_individ/${subject}/MD/${subject}${MD2ENIGMA_NAME})" 
eval "AD2ENIGMA=(${TBSS_run_folder}/AD_individ/${subject}/AD/${subject}${AD2ENIGMA_NAME})" 
eval "RD2ENIGMA=(${TBSS_run_folder}/RD_individ/${subject}/RD/${subject}${RD2ENIGMA_NAME})" 

#Create a picture of the registered FA brain to be overlaid on the ENIGMA template
${FSLDIR}/bin/slicer ${FA2ENIGMA} ${ENIGMA_FA_Template} -e 0 -S 6 1500 ${FAreg}/${subject}_FA2ENIGMA_reg_QC.png

#Create a picture of the FA skeleton which shows the different intensisties to check for breaks in skeleton
${FSLDIR}/bin/slicer ${FA_SKELETON} -S 4 1500 ${FAskel}/${subject}_masked_FAskel.png

#Create a montage of slices from registered dMRI map images
${PYTHON} ${QCpng} ${FA2ENIGMA} ${dMRI_FA}/${subject}_FA2ENIGMA_QC.png
${PYTHON} ${QCpng} ${MD2ENIGMA} ${dMRI_MD}/${subject}_MD2ENIGMA_QC.png
${PYTHON} ${QCpng} ${AD2ENIGMA} ${dMRI_AD}/${subject}_AD2ENIGMA_QC.png
${PYTHON} ${QCpng} ${RD2ENIGMA} ${dMRI_RD}/${subject}_RD2ENIGMA_QC.png

done


