import argparse
import os
import sys
import time
import logging
import pandas as pd
import numpy as np
# from eDTI_outliers.scripts.filtering_algorithm import *
# from eDTI_outliers.scripts.constants import *
import eDTI_outliers.scripts.constants as cnst
import eDTI_outliers.scripts.filtering_algorithm as filtering_algorithm



def Argument_parser_function():
    '''
    parser function
    Return the argument parser
    '''
    logger = logging.getLogger("MyAppLogger") # Get the logger that was set in the main() [Logger is a singleton]
    parser = argparse.ArgumentParser(description="Process subject column and input file.")


    # Create a group for required arguments
    required_group = parser.add_argument_group("required arguments")
    # Define the required arguments
    required_group.add_argument("--subjID", required=True, help="Column name that holds subjectID information. Make sure the subjectID column name is the same across all input CSV files.")
    # Path to the text file, which have paths to each protocol results
    required_group.add_argument("--DTIinputs", required=True, help="Path to text file which contains a list of absolute paths to each ENIGMA DTI pipeline output csv file.")
    # Path where the csv file and results will be stored
    required_group.add_argument("--output", required=True, default="", help="Path to where the output csv will be saved.") 


    # For Diagnosis column and Site column
    parser.add_argument("--demogCSV", required=False, help="Path to the csv file that contains demographic information(e.g. Age). This csv should contain columns for diagnosis group and site, if available.")#Used for forming 4 combinations for filtering. If no demographic file, outliers will be identified against the complete data.
    parser.add_argument("--dx", required=False, help="Column name for diagnosis in demographic file, if applicable.") #Used for forming 4 combinations for filtering. If no demographic file, outliers will be identified across the complete data.
    parser.add_argument("--site", required=False, help="Column name for site in demographic file, if applicable.")# Used for forming 4 combinations for filtering. If no demographic file, outliers will be identified against the complete data.

    #Quantile range which will be approved: For Stringent 0.5%-99.5% 
    parser.add_argument("--quant1", required=False, type=float, nargs=2,  default=(0.005, 0.995), metavar=('VAL1', 'VAL2'), help="List of 2 numbers between 0 and 1 indicating the upper and lower quantile thresholds used to identify outliers (e.g. --quant1 .25 .75). NOTE: By default this is set to --quant1 .005 .995 such that ROI values < 0.5 %%ile or > 99.5 %%ile are flagged") 
    # parser.add_argument("--lq_thresh1", required=False, default=0.005, help="Lower quantile threshold. Will flag ROIs below this. Default set to 0.005.")
    # parser.add_argument("--uq_thresh1", required=False, default=0.995, help="Upper quantile threshold. Will flag ROIs above this. Default set to 0.995") 
    
    # Stringent threshold of 10% of ROIs
    parser.add_argument("--perc1", required=False, default=0.1, help="Percent of ROIs that must fall outside of lq_thresh1 and uq_thresh1 for subject to be flagged as an outlier. Default set to 0.1 (10%%).") #Threshold for flagging subjects which has atleast this many ROIs which were flagged outliers under Quantile range 1.


    #Quantile range which will be approved: For Linient 0.1%-99.9%
    parser.add_argument("--quant2", required=False, type=float, nargs=2,  default=(0.001, 0.999), metavar=('VAL1', 'VAL2'), help="List of 2 numbers between 0 and 1 indicating the upper and lower quantile thresholds used to identify outliers (e.g. --quant2 .25 .75). NOTE: By default this is set to --quant2 .001 .991 such that ROI values < 0.1 %%ile or > 99.9 %%ile are flagged") 
    # parser.add_argument("--lq_thresh2", required=False, default=0.001, help="Lower quantile threshold. Will flag ROIs below this. Default set to 0.001") 
    # parser.add_argument("--uq_thresh2", required=False, default=0.999, help="Upper quantile threshold. Will flag ROIs above this. Default set to 0.999") 
    
    # Stringent threshold of 5% of ROIs
    parser.add_argument("--perc2", required=False, default=0.05, help="Percent of ROIs that must fall outside of lq_thresh2 and uq_thresh2 for subject to be flagged as an outlier. Default set to 0.05 (5%%).") 
    
    

    # Parse the arguments
    args = parser.parse_args()

    #For setting the range upper and lower limit (Handles if the input is not given in correct order)
    args.lq_thresh1=min(args.quant1)
    args.uq_thresh1=max(args.quant1)
    args.lq_thresh2=min(args.quant2)
    args.uq_thresh2=max(args.quant2)

    return args


def Input_validator(entered_args):
    '''
    Check if the DTIinputs exist and is not empty.
    Checks if the subjID was entered by the user.
    Make sure that the perc1 and perc2 is within the range 0-1.
    Checks range of lq_thresh1, lq_thresh2, uq_thresh1 and uq_thresh2. Make sure that the values are valid.
    If all valid, return the grouping criteria (Across_Diagnosis + Across_Sites, Across_Diagnosis + Within_Sites, Within_Diagnosis + Across_Sites, Within_Diagnosis + Within_Sites)
    '''
    logger = logging.getLogger("MyAppLogger") # Get the logger that was set in the main() [Logger is a singleton]
    if not entered_args.subjID:#If Subject column is not given
        logger.info(f"Please enter subjID. Cannot be empty.")
        sys.exit(1)

    if not (entered_args.DTIinputs and os.path.exists(entered_args.DTIinputs)):#If the input file is empty of does not exist
        logger.info(f"The file {entered_args.DTIinputs} does not exist or the path is wrong")
        sys.exit(1)

    if entered_args.lq_thresh1<0 or entered_args.lq_thresh1>1:
        logger.info(f"The Quantile range1 for Lower limit {entered_args.lq_thresh1} is invalid. Valid range is between 0.0 to 1.0.")
        sys.exit(1)

    if entered_args.uq_thresh1<0 or entered_args.uq_thresh1>1:
        logger.info(f"The Quantile range1 for Upper limit {entered_args.uq_thresh1} is invalid. Valid range is between 0.0 to 1.0.")
        sys.exit(1)

    if entered_args.lq_thresh1>entered_args.uq_thresh1:
        logger.info(f"The Quantile range1 for lower limit is greater than Upper limit")
        sys.exit(1)

        
    if entered_args.lq_thresh2<0 or entered_args.lq_thresh2>1:
        logger.info(f"The Quantile range1 for Lower limit {entered_args.lq_thresh2} is invalid. Valid range is between 0.0 to 1.0.")
        sys.exit(1)

    if entered_args.uq_thresh2<0 or entered_args.uq_thresh2>1:
        logger.info(f"The Quantile range2 for Upper limit {entered_args.uq_thresh2} is invalid. Valid range is between 0.0 to 1.0.")
        sys.exit(1)

    if entered_args.lq_thresh2>entered_args.uq_thresh2:
        logger.info(f"The Quantile range2 for lower limit is greater than Upper limit")
        sys.exit(1)

    if entered_args.perc1<0.0 or entered_args.perc1>1.0:
        logger.info(f"The perc1: {entered_args.perc1} is invalid. Valid range is between 0.0 to 1.0. Recommended to use 0.1(10%)")
        sys.exit(1)

    if entered_args.perc2<0.0 or entered_args.perc2>1.0:
        logger.info(f"The perc2: {entered_args.perc2} is invalid. Valid range is between 0.0 to 1.0. Recommended to use 0.05(5%)")
        sys.exit(1)


    #Initializing the dictionary in the cnst py file(Only one instance is possible)
    grouping_dict_diag_site=cnst.SingletonGrouping(entered_args.site,entered_args.dx,entered_args.subjID, [float(entered_args.lq_thresh2),float(entered_args.uq_thresh2)], [float(entered_args.lq_thresh1),float(entered_args.uq_thresh1)], entered_args.perc1,entered_args.perc2)
    
    #Grouping combinations for the final CSV file=> cnst.grouping_criteria keys for iterating later
    csv_grouping_arr=[cnst.across_data] 

    logger.info("Entered SubjectID column: '{}'\n".format(entered_args.subjID))

    if not entered_args.demogCSV:
        logger.info("No demographic csv entered.\n")
        return csv_grouping_arr

    #Add Diagnosis based grouping
    if entered_args.dx:
        logger.info("Entered diagnosis column: '{}'\n".format(entered_args.dx))
        csv_grouping_arr.append(cnst.across_site)
    else:
        logger.info("No diagnosis column entered.\n")
    #Add Site based grouping
    if entered_args.site:
        logger.info("Entered site column: '{}'\n".format(entered_args.site))
        csv_grouping_arr.append(cnst.across_diagnosis)
    else:
        logger.info("No site column entered.\n")

    
    #Add Site based and Diagnosis based grouping
    if entered_args.site and entered_args.dx:
        csv_grouping_arr.append(cnst.diagnosis_site_group)

    return csv_grouping_arr


def ROI_col_finder(input_file_path):
    '''
    Returns the columns of all ROIs that we are interested in. Should be intersection of cnst.ROI_columns or if "Average" key word is in ROI.
    Alternative: Pick all the columns and drop the subject column. This was the user has to make sure that the ENIGMA DTI results file contains only ROI columns and subject column
    Return a list of ROIs which exist in ENIGMA DTI results csv file.
    '''
    grouping_dict_diag_site_instance=cnst.SingletonGrouping() #The instance was already created in the input_validator, so it return the same reference
    logger = logging.getLogger("MyAppLogger") # Get the logger that was set in the main() [Logger is a singleton]
    
    # To check we don't include the subject,site,group while calculating the threshold
    set_cols_checker={grouping_dict_diag_site_instance.subject_col,grouping_dict_diag_site_instance.site_col,grouping_dict_diag_site_instance.diag_col}

    with open(input_file_path) as file:
        #List of all paths, to iterate through the list and combine the results from each iteration (Contains ROIs)
        all_csv_files=file.readlines()
    
    all_roi_cols=[] #Columns to list all the ROI columns
    roi_cols_from_cnst=[] #Columns to list which also occur in the cnst.ROI_columns. Also keep ROI which has Average in it.
    for file_i in all_csv_files:
        file_i=file_i.replace("\n","").replace("\r","")
        if not file_i:
            continue

        if not os.path.exists(file_i):#If the input file is empty of does not exist
            print(f"The file {file_i} does not exist.")
            sys.exit(1)
        
        cols_in_file_i=pd.read_csv(file_i, nrows=0).columns.to_list() # Columns in file_i
        if grouping_dict_diag_site_instance.subject_col not in cols_in_file_i:
            print(f"The file {file_i} does not have {grouping_dict_diag_site_instance.subject_col} column.")
            sys.exit(1)

        roi_cols_i=[]
        # all_roi_cols+=cols_in_file_i
        for col_i in cols_in_file_i:
            all_roi_cols.append(col_i)
            #Add Columns to list which also occur in the cnst.ROI_columns. Also keep ROI which has 'Average' in it.
            if col_i.lower() in cnst.ROI_columns or "average" in col_i.lower():
                roi_cols_i.append(col_i)

        # Lis of columns which are not being considered to calculate Outlier frequency for the subjects
        ROIs_not_used_file_i=set(cols_in_file_i).difference(set(roi_cols_i))
        ROIs_not_used_file_i.discard(grouping_dict_diag_site_instance.subject_col) #To remove subject column from the list, since it is used as index

        logger.info("Reading in: {}".format(file_i))
        logger.info("ROI Columns that are used: {}".format(",".join(roi_cols_i)))
        if ROIs_not_used_file_i:
            logger.info("Columns that are NOT used: {}\n".format(",".join(ROIs_not_used_file_i)))
        else:
            logger.info("All ROI columns from the file is being used\n")
        
        roi_cols_from_cnst+=roi_cols_i

    
    all_roi_cols=[col for col in all_roi_cols if col not in set_cols_checker]
    return roi_cols_from_cnst


def Combined_Table_generator(input_file_path,subject_col, demogCSV,csv_combinations_cols,threshold_stringent,threshold_lenient,ROI_cols_arr):
    '''
    Prepares a dataframe with count of ROIs which were outliers for a specific subject.

    '''
    grouping_dict_diag_site_instance=cnst.SingletonGrouping() #The instance was already created in the input_validator, so it return the same reference
    
    # To check we don't include the subject,site,group while calculating the threshold
    set_cols_checker={grouping_dict_diag_site_instance.subject_col,grouping_dict_diag_site_instance.site_col,grouping_dict_diag_site_instance.diag_col}

    with open(input_file_path) as file:
        #List of all paths, to iterate through the list and combine the results from each iteration (Contains ROIs)
        all_csv_files=file.readlines()
    
    demography=None
    if demogCSV:
        # Read demography data
        demography=pd.read_csv(demogCSV)

    subject_set=set()
    for file_i in all_csv_files:
        file_i=file_i.replace("\n","").replace("\r","")
        subject_set=subject_set.union(set(pd.read_csv(file_i, usecols=[subject_col])[subject_col].tolist()))


    #Prepare the final dataframe which will have count for each combination
    complete_DTI_measures_count= pd.DataFrame(list(subject_set), columns=[subject_col])

    #Prepare the column for each combination for the 8 columns (all combinations); Initialize the count from 0
    for key_i in csv_combinations_cols:
        complete_DTI_measures_count[key_i+cnst.stringent_string]=0
        complete_DTI_measures_count[key_i+cnst.lenient_string]=0

        complete_DTI_measures_count[key_i+cnst.stringent_string+"_set"]=[set() for _ in range(len(complete_DTI_measures_count))]#Set to add ROI which were outliers for that subject 
        complete_DTI_measures_count[key_i+cnst.lenient_string+"_set"]=[set() for _ in range(len(complete_DTI_measures_count))]#Set to add ROI which were outliers for that subject


    #Set the index to Subject which will make it easier while combining results from multiple dataframes
    complete_DTI_measures_count.set_index(subject_col, inplace=True)

    Filtering_Algorithm_object=filtering_algorithm.Filtering_Algorithm()
    
    all_roi_cols=[] #Columns to list all the ROI columns
    for file_i in all_csv_files:
        file_i=file_i.replace("\n","").replace("\r","")
        file_name_suffix=file_i.split("/")[-1].split(".")[0]
        ROI_DF=pd.read_csv(file_i)
        ROI_DF.drop(columns=[grouping_dict_diag_site_instance.site_col,grouping_dict_diag_site_instance.diag_col], errors='ignore',inplace=True)
        
        # df_ROIs_col=[col for col in ROI_DF.columns.to_list() if col not in set_cols_checker] # Gets all the ROIs column and skips the Subject, Site and Diagnosis group columns
        df_ROIs_col=list(set(ROI_cols_arr).intersection(set(ROI_DF.columns.to_list()))) # Gets all the ROIs column which we had filtered from the ROI_col_finder function.
        if demography is not None:
            ROI_DF=ROI_DF.merge(demography, on=subject_col, how="inner", suffixes=["_x",""])

        new_ROI_df=Filtering_Algorithm_object.outliers_helper_function(ROI_DF,df_ROIs_col,csv_combinations_cols,threshold_stringent,threshold_lenient,file_name_suffix)
        # complete_DTI_measures_count=complete_DTI_measures_count+new_ROI_df[complete_DTI_measures_count.columns]

        for col in complete_DTI_measures_count.columns:
            if col.split("_")[-1]=="set":
                complete_DTI_measures_count[col] = complete_DTI_measures_count[col].combine(
                        new_ROI_df[col], 
                        lambda x, y: x.union(y) if pd.notnull(y) else x,
                        fill_value=set()
                    )
            else:
                complete_DTI_measures_count[col]=complete_DTI_measures_count[col]+new_ROI_df[col]
        
    
    return complete_DTI_measures_count


def Save_dataframe_function(combined_table_after_grouping,output_csv_folder):
    '''
    With the dataframe given as input, this function will produce CSV (for ROI count), excelBook and CSV (for specific string ROI which contributed to Outlier count)
    output_csv_folder is the path to the output file
    '''

    grouping_dict_diag_site_instance=cnst.SingletonGrouping() #The instance was already created in the input_validator, so it return the same reference
    
    logger = logging.getLogger("MyAppLogger") # Get the logger that was set in the main() [Logger is a singleton]
    columns_with_Outlier_ROI_names=sorted([col for col in combined_table_after_grouping.columns if col.endswith("_set")]) #Columns which list the Outliers
    columns_with_ROI_counts=sorted([col for col in combined_table_after_grouping.columns if not col.endswith("_set")]) #Columns with only count of Outliers

    #For excel workbook, to save it with multiindex columns such that the resulting file will have lenient and Stringent as sub columns
    column_sequence_counts=["Outliers_Count"]+columns_with_ROI_counts 

    #Count for each subject, to check how many times they were outliers across the combinations
    combined_table_after_grouping['Outliers_Count'] = combined_table_after_grouping[columns_with_Outlier_ROI_names].apply(lambda row: row.astype(bool).sum(), axis=1)

    combined_table_after_grouping_counts=combined_table_after_grouping[column_sequence_counts].copy() #Dataframe with Counts
    combined_table_after_grouping_names=combined_table_after_grouping[["Outliers_Count"]+columns_with_Outlier_ROI_names].copy() #Dataframe with names

    for col in columns_with_Outlier_ROI_names:
        combined_table_after_grouping_names[col] = combined_table_after_grouping_names[col].apply(lambda x: ", ".join(x))


    multi_index_col = [
        (col.split("+")[0],col.split("+")[1],grouping_dict_diag_site_instance.criteria_string_mapper[col.split("+")[2]]) 
        if col != "Outliers_Count" and col!=grouping_dict_diag_site_instance.subject_col
        else (col,'', '') 
        for col in column_sequence_counts
    ]
    columns_multiIndex = pd.MultiIndex.from_tuples(
    multi_index_col,    names=['', '', '']
    )



    # Saving as csv file
    combined_table_after_grouping_counts.columns = [col.replace("_","").replace("+","_") for col in combined_table_after_grouping_counts.columns]
    combined_table_after_grouping_names.columns = [col.replace("_","").replace("+","_").rstrip("_set") for col in combined_table_after_grouping_names.columns]

    combined_table_after_grouping_counts.to_csv(output_csv_folder+".csv")
    combined_table_after_grouping_names.to_csv(output_csv_folder+"_ROI_names.csv")

    #Saving as Excel Workbook
    combined_table_after_grouping_counts.columns = columns_multiIndex
    writer = pd.ExcelWriter(output_csv_folder+'.xlsx', engine='xlsxwriter')
    combined_table_after_grouping_counts.to_excel(writer)
    writer.close()
    logger.info("CSV saved in {}".format(output_csv_folder+"_ROI_names.csv"))
    logger.info("Excel saved in {}".format(output_csv_folder+".xlsx"))

def main():
    # Output Folder Name
    # output_file_name="FA_MD_L1_RD_Outliers_testing"+str(time.time()).replace(".","_")

    # Input arguments 
    args=Argument_parser_function()

    #Output file name
    output_csv_folder=args.output.rstrip("/")#+"/"+output_file_name

    # Create a named logger, so that it can be used in other functions and classes
    logger = logging.getLogger("MyAppLogger")
    logger.setLevel(logging.INFO)  # Set the minimum log level to INFO

    # File handler
    file_handler = logging.FileHandler(output_csv_folder+".log",  mode="w")
    file_handler.setLevel(logging.INFO)  # Ensure the handler respects the minimum level
    file_handler.setFormatter(logging.Formatter('%(message)s'))  # Keep only the message, don't add INFO DEBUG ERROR 

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Ensure the handler respects the minimum level
    console_handler.setFormatter(logging.Formatter('%(message)s'))  # Keep only the message, don't add INFO DEBUG ERROR 

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


    logger.info("Program initiated:\n")

    #Input validation + Combination array for the final CSV file
    csv_combinations_cols=Input_validator(args)


    # Reconstruct the command
    full_command_array=[]
    comm_i_ind=0
    while comm_i_ind< len(sys.argv):
        comm_i=sys.argv[comm_i_ind]
        if comm_i.startswith("--"):
            if comm_i=="--quant1" or comm_i=="--quant2":
                full_command_array.append(sys.argv[comm_i_ind]+" "+sys.argv[comm_i_ind+1]+" "+sys.argv[comm_i_ind+2])
                comm_i_ind+=1
            else:
                full_command_array.append(sys.argv[comm_i_ind]+" "+sys.argv[comm_i_ind+1])
            comm_i_ind+=1
        else:
            full_command_array.append(sys.argv[comm_i_ind])
        comm_i_ind+=1
    command_string=" \\\n".join(full_command_array)
    logger.info(f"Call: \n{command_string}\n")



    #Complete ROI column list from each measures from the input file
    ROI_cols_arr=ROI_col_finder(args.DTIinputs)
    tot_ROIs=len(ROI_cols_arr) # #ROIs which will be considered for getting the outliers

    threshold_stringent=int(args.perc1*tot_ROIs) # Stringent threshold of 10% of ROIs or perc1
    threshold_lenient=int(args.perc2*tot_ROIs) # Lenient threshold of 5% of ROIs or perc2

    logger.info("Total ROIs across all the ENIGMA DTI pipeline outputs: {}\n".format(tot_ROIs))

    logger.info("Criteria 1: Subjects with {} out of {} ROIs (i.e. {}% of all ROIs) labeled as extreme (<{}%ile or >{}%ile) will be flagged as outliers.\n".format(threshold_stringent, tot_ROIs, args.perc1*100.0,args.lq_thresh1*100.0,args.uq_thresh1*100.0))
    
    logger.info("Criteria 2: Subjects with {} out of {} ROIs (i.e. {}% of all ROIs) labeled as extreme (<{}%ile or >{}%ile) will be flagged as outliers.\n".format(threshold_lenient, tot_ROIs, args.perc2*100.0,args.lq_thresh2*100.0,args.uq_thresh2*100.0))
    
    # Generated the dataframe with count of ROI outliers for each subject
    combined_table_after_grouping=Combined_Table_generator(args.DTIinputs, args.subjID,args.demogCSV,csv_combinations_cols,threshold_stringent,threshold_lenient,ROI_cols_arr)
    combined_table_after_grouping=combined_table_after_grouping.replace(0, "")

    #Save the dataframe as CSV and excel workbook
    Save_dataframe_function(combined_table_after_grouping,output_csv_folder)

    


if __name__=="__main__":
    main()