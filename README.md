# Additional QC tools

We offer additional QC tools in this submodule that may be used in conjunction with tools offered on the main Github page [link]. In brief, these include:

1. **Statistical QC:** In this section, we provide a package to help to identify outliers at the statistical level. Subjects are flagged based on various criteria including number of DTI ROI measures that fall outside various %iles. We recommend that this package be used to flag subjects for further visual inspection and not to automatically exclude data. Data can be visualized using the main tools described on the main Github pageabove[link] or by using the additional tools from this submodule.  

2. **Visual QC:** In this section, we provide an optional script that outputs a series of PNG images that may help to visually inspect problematic scans and/or registrations identified as outliers. These include images of: FA registrations to the ENIGMA template, FA values projected onto the ENIGMA template skeleton, and the diffusion scalar maps warped to the ENIGMA template.

## Table of Contents
- [Installation](#installation)
- [Statistical QC](#statistical-qc)
- [Visual QC](#visual-qc)


## Installation

Please follow the instructions below carefully to install the package.

### 1. Ensure Conda is Installed. If Conda is not installed, download and install Miniconda from the official website [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). 
  `conda --version`
### 2. Clone the repository:
  `git clone https://github.com/lizhaddad/eDTI_additional_QC.git`

### 3. After Miniconda has been installed, run the following command to create the environment:
  `conda env create -f eDTI_additional_QC/environment.yaml`

### 4. Once the environement is created, run the following command to activate environment:
  `conda activate ENIGMA_DTI_env`

### 5. After cloning (in the same directory that `git clone` was run in):
  `pip install ./eDTI_additional_QC`

**_Note that this procedure only needs to be followed once. Once the installation is complete, you will only need to execute Step #4 before running either the [eDTI_outliers](https://github.com/lizhaddad/eDTI_QC_v2_dev2/tree/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers) package or the [visual_qc_script.sh](https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/31e6dd2c687266182acd51f54c1d222b1724d435/visual_qc/visual_qc_script.sh) described below._**


## Statistical QC

### Description

The [eDTI_outliers](https://github.com/lizhaddad/eDTI_QC_v2_dev2/tree/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers) package can be used to identify outliers in the ENIGMA DTI output CSVs (e.g., combinedROItable_FA.csv). We recommend
* that it be used to flag subject scans for further visual inspection and not to automatically exclude data.
* if a subject’s scan fails further visual inspection, that the subject be excluded entirely and not just specific ROIs or DTI measures.

#### <ins>Criteria for flagging outliers</ins>

The code takes all ENIGMA DTI output CSVs that will be used in the study (i.e., FA, MD, RD, and AD) as inputs and, by default, uses 2 thresholds to flag subjects as outliers:

1. **Threshold 1:** Any subject with 5% of all ROI DTI values that are < 0.1 or > 99.9 percentile

2. **Threshold 2:** Any subject with 10% of all ROI DTI values that are < 0.5 or > 99.5 percentile

_Both the number of ROIs and the percentile thresholds may be changed if desired._

**Note:** the number of ROIs across all DTI measures input are considered together, not separately, as issues and artifacts in the DWI can influence all resulting maps 
* e.g., if 20 FA and 20 MD ROIs are input, then by threshold 2 defined above, a minimum of 0.10*40=4 ROI values must fall below the 0.5%ile or above the 99.5%ile for the subject to be flagged as an outlier

The code first checks for outliers across all subjects inputted. By default, it will also check for outliers when the data are parsed in the following ways:

1. If diagnosis is provided, it will check whether a subject is an outlier a) within diagnostic groups and b) across all diagnoses – this is important in situations where pathology is prevalent in disease and may appear as outliers across all subjects but not within the disease group (e.g., pervasive WMH). 

2. If multiple sites are included, it will check for outliers a) within each site and b) across all sites – this is important when on average a site behaves differently than other sites, and may appear as an outlier relative to other sites (e.g., only one site of 10 sites has 4mm voxels from an older 1.5T scanner and the rest are 2mm 3T). 

#### <ins>Output files</ins>

#### _Primary outputs_

**`${prefix}_SUMMARY_eDTI_outliers_subjects_flagged.txt`**: main output text file specifying any subject flagged as an outlier with one or more criteria. We recommend further visual inspection of these subjects:

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers/images/example_main_output.png" width="90%" height="50%">
</p>

**`${prefix}_eDTI_outliers.log`**: text file log of the command, flags, and inputs used

#### _Secondary outputs_

Additional information on the criteria for which each subject was flagged and the specific ROI measures flagged can be found in the **`Supplementary_Outputs/`** folder.

**`Supplementary_Outputs/${prefix}_eDTI_outliers_subjects_flagged_byCriteria.xlsx`**: formatted excel file details, for each subject, how many ROI measures were flagged using each of 8 possible criteria. The 9 columns indicate the number of outliers detected:
* Across sites, across diagnoses, using threshold 1
* Across sites, across diagnoses, using threshold 2
* Across sites, within diagnoses, using threshold 1
* Across sites, within diagnoses, using threshold 2
* Within sites, across diagnoses, using threshold 1
* Within sites, across diagnoses, using threshold 2
* Within sites, within diagnoses, using threshold 1
* Within sites, within diagnoses, using threshold 2
* Summary column indicating the total number of times the subject was flagged across the 8 criteria

**Note:** If there are not multiple diagnoses or sites, these columns will automatically be excluded. Only ROI measure counts that meet or surpass the given criteria are noted (e.g. if only 3% of ROIs were identified as outliers, not 10%, the cell remains blank) 

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers/images/example_xlsx.png" width="90%" height="50%">
</p>

**`Supplementary_Outputs/${prefix}_eDTI_outliers_subjects_flagged_byCriteria.csv`**: CSV with the same information as **`Supplementary_Outputs/${prefix}_eDTI_outliers_subjects_flagged_byCriteria.xlsx`** but saved in a format that is easier to filter and read into other packages.

**`Supplementary_Outputs/${prefix}_eDTI_outliers_ROIs_flagged_byCriteria.csv`**: CSV with the number of ROI measures that were identified as outliers replaced with a list of the specific ROIs that were flagged

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers/images/example_roi_flagged.png" width="90%" height="50%">
</p>

### Setting up input files

**`eDTI_outliers.py`** requires two input files to run:

1.) <ins>ENIGMA DTI outputs text file</ins>: A text file enumerating the absolute path to each ENIGMA DTI output CSV file. These are the CSV files containing all the mean DTI measures in each ROI. **_We assume these CSVs include the standard white matter ROIs output by running the ENIGMA DTI protocol_**.

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers/images/example_text.png" width="90%" height="50%">
</p>

2.) <ins>Demographics CSV file</ins>: If you would like site and diagnosis to be considered, a separate CSV file with columns indicating diagnosis and site for each subject. This file can include other demographic and study variables as well, they do need to be removed. 

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/c0981c8c8230d0277c5641971ad2a3bc5d3a3b55/eDTI_outliers/images/example_demog.png" width="90%" height="50%">
</p>

The **subject ID column name must match** across all CSVs listed in the ENIGMA DTI outputs text file and the demographics CSV file.



### Usage

```
conda activate ENIGMA_DTI_env

eDTI_outliers \
--subjID subjectID \
--dx Diagnosis \
--site Site \
--demogCSV /Users/enigma_DTI/projects/tbss/example_input/example_demog.csv \
--output /Users/enigma_DTI/projects/tbss/example_output/eDTI_project \
--DTIinputs /Users/enigma_DTI/projects/tbss/example_input/example_text.txt
```

| flag        | input type   | required/ optional | description                                                                                                                                                                                                                                                                                                                                    |
| ----------- | ------------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| \--subjID   | string       | required           | Indicate the column name that indicates the subject ID information across all files input (e.g., –subjID subjectID). Make sure the subject ID column name is the same across all input CSV files.                                                                                                                                              |
| –-DTIinputs  | text file    | required           | Path to text file that contains a list of absolute paths to each ENIGMA DTI output CSV file. This should contain a minimum of 1 path, but can include more.                                                                                                                                                                                    |
| \--demogCSV | csv file     | optional           | Path to CSV file that contains all study variables (e.g. demographic information). If you would like site and diagnosis to be considered, this CSV should contain columns for diagnosis group and site, if available. If not provided, only outliers across all diagnoses and sites will be considered.                                        |
| \--dx       | string       | optional           | If applicable, indicate the column name that indicates diagnosis information in –demogCSV (e.g., –dx Diagnosis). If not provided, only outliers across all diagnoses will be considered.                                                                                                                                                       |
| \--site     | string       | optional           | If applicable, indicate the column name that indicates site or study information in –demogCSV (e.g., –site Site). If not provided, only outliers across all sites will be considered.                                                                                                                                                          |
| –-quant1     | numeric      | optional           | List of 2 numbers between 0 and 1 indicating the upper and lower quantile thresholds used to identify outliers (e.g. –quant1 .25 .75). NOTE: By default this is set to –quant1 .005 .995 such that ROI values < 0.5 %ile or > 99.5 %ile are flagged                                                                                            |
| \--perc1    | numeric      | optional           | Number between 0 and 1 indicating the percent of ROIs that must fall outside the thresholds defined by –quant1 in order to flag a subject as an outlier (e.g. –perc1 .50 indicates 50%). NOTE: By default this is set to –perc1 0.1 such that if 10% of the total number of ROIs are outside quant1, the subject will be flagged as an outlier |
| –-quant2     | numeric      | optional           | List of 2 numbers between 0 and 1 indicating the upper and lower quantile thresholds used to identify outliers (e.g. –quant2 .25 .75). NOTE: By default this is set to –quant2 .001 .999 such that ROI values < 0.1 %ile or > 99.9 %ile are flagged                                                                                            |
| \--perc2    | numeric      | optional           | Number between 0 and 1 indicating the percent of ROIs that must fall outside the thresholds defined by –quant2 in order to flag a subject as an outlier (e.g. –perc2 .50 indicates 50%). NOTE: By default this is set to –perc2 0.05 such that if 5% of the total number of ROIs are outside quant2, the subject will be flagged as an outlier |
| \--output   | path/ prefix | required           | Path to where the output files will be outputted along with an output prefix (e.g. /Users/enigma_DTI/projects/tbss/example_output/eDTI_project).                                                                                                                                                                                                                                                       |





## Visual QC

Once you have created the environment from described in [this section](##Installation), be sure to activate the environment in your terminal (as in step 4) each time you want to run the visual QC script:

`conda activate ENIGMA_DTI_env`

Open the [visual qc script.sh](https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/826fcbebcee3d9fdc06ef3d402f259b9c14c58c2/visual_qc/visual_qc_script.sh) in any text editor and modify the paths and file suffixes in the "EDIT ME" section.

Once you have completed these two steps, simply run the script in a terminal as such (being sure to point to the absolute path if the script is not in your present working directory):

`./visual_qc.script.sh` 

Next, you can view the following outputs:

### FA registration
Shows the outline of the ENIGMA template in red overlaid on each subject’s FA image

_What to look for:_
* Red outline is misaligned in central white matter regions of high FA (eg: the corpus callosum, internal capsule, etc)

**Good example:**


<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/826fcbebcee3d9fdc06ef3d402f259b9c14c58c2/visual_qc/images/registration_qc_good.png" width="90%" height="50%">
</p>

**Bad example:**

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/826fcbebcee3d9fdc06ef3d402f259b9c14c58c2/visual_qc/images/registration_qc_bad.png" width="90%" height="50%">
</p>

### FA skeleton
Creates a picture of extracted subject FA values in the ENIGMA template skeleton which shows the different intensities to check for breaks in skeleton

_What to look for:_
* Regions of skeleton with no values (i.e. dark/blacked out)
* Extreme differences in contrast/FA values in the skeleton indicating noisy FA

**Good example:**

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/826fcbebcee3d9fdc06ef3d402f259b9c14c58c2/visual_qc/images/skeleton_qc_good.png" width="90%" height="50%">
</p>

**Bad example:**

<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/826fcbebcee3d9fdc06ef3d402f259b9c14c58c2/visual_qc/images/skeleton_qc_bad.png" width="90%" height="50%">
</p>


### dMRI maps
DTI scalar maps (i.e. FA, MD, AD, RD) warped to the ENIGMA template

_What to look for:_
* Evidence of misregistration (eg: image looks extremely distorted, out of field of view)
* Another opportunity to QC preprocessing if it wasn’t done (i.e. note noisy images, pathology, cropped FOV, etc)

**Example FA:**
<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/f15f34baeec08485da47b618bf5b57da79ede787/visual_qc/images/example_FA2ENIGMA_QC.png" width="90%" height="50%">
</p>


**Example MD:**
<p align="center">
<img src="https://github.com/lizhaddad/eDTI_QC_v2_dev2/blob/f15f34baeec08485da47b618bf5b57da79ede787/visual_qc/images/example_MD2ENIGMA_QC.png" width="90%" height="50%">
</p>
