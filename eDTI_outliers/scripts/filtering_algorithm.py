import numpy as np
import pandas as pd
# from eDTI_outliers.scripts.constants import *
import eDTI_outliers.scripts.constants as cnst

class Filtering_Algorithm:
    def __init__(self):
        self.grouping_dict_diag_site_instance=cnst.SingletonGrouping() #The instance was already created in the input_validator, so it return the same reference
    

    def IQR_based_helper_func(self, df,grouping_header_name,df_ROIs_col,file_name_suffix):
        '''
        df:                     Dataframe
        grouping_header_name:   The dict key name, which is also the column name where we increment the counter if a ROI is an outlier
        df_ROIs_col:            Contains the ROI names on which we test if it's outlier
        
        For the incoming dataframe, we will check for each ROI and check if they are outlier and increment the Outlier ROIs for the subject 
        '''
        
        for ROI_i in df_ROIs_col:
            ROI_i_lower_bound_stringent=df[ROI_i].quantile(self.grouping_dict_diag_site_instance.quantile_stringent[0]) #To get the lower bound value for the stringent filtering:If none default is 5%
            ROI_i_upper_bound_stringent=df[ROI_i].quantile(self.grouping_dict_diag_site_instance.quantile_stringent[1]) #To get the upper bound value for the stringent filtering:If none default is 95%
            
            ROI_i_lower_bound_lenient=df[ROI_i].quantile(self.grouping_dict_diag_site_instance.quantile_lenient[0]) #To get the lower bound value for the lenient filtering:If none default is 1%
            ROI_i_upper_bound_lenient=df[ROI_i].quantile(self.grouping_dict_diag_site_instance.quantile_lenient[1]) #To get the upper bound value for the lenient filtering:If none default is 99%
            
            # Get subjects which are out of bounds for Stringent and Lenient IQR threshold 
            ROI_I_df_stringent=df[(df[ROI_i]<ROI_i_lower_bound_stringent) | (df[ROI_i]>ROI_i_upper_bound_stringent)]
            ROI_I_df_lenient=df[(df[ROI_i]<ROI_i_lower_bound_lenient) | (df[ROI_i]>ROI_i_upper_bound_lenient)]
            
            #Increment the count for the subjects which has an outlier ROI
            df.loc[ROI_I_df_stringent.index, grouping_header_name+cnst.stringent_string] += 1
            df.loc[ROI_I_df_lenient.index, grouping_header_name+cnst.lenient_string] += 1

            # Union operation to adds the new ROI element to the subject set
            df.loc[ROI_I_df_stringent.index, grouping_header_name+cnst.stringent_string+'_set']=df.loc[ROI_I_df_stringent.index, grouping_header_name+cnst.stringent_string+'_set'].apply(
                lambda x: x | {ROI_i+"__"+file_name_suffix}  
            )
            
            # Union operation to adds the new ROI element to the subject set
            df.loc[ROI_I_df_lenient.index, grouping_header_name+cnst.lenient_string+'_set']=df.loc[ROI_I_df_lenient.index, grouping_header_name+cnst.lenient_string+'_set'].apply(
                lambda x: x | {ROI_i+"__"+file_name_suffix}  
            )
            
            
        return df

    def outliers_helper_function(self, df,df_ROIs_col,csv_grouping_arr,threshold_stringent,threshold_lenient,file_name_suffix):
        '''
        Function to split the df as per the (diag value + site value)
        # of Diagnosis will be unique(df["Dx"])
        # of Sites will be unique(df["Dx"])
        
        In total there would be 2*2 combinations from : 4 
        [   All Diagnosis + All Site,
            All Diagnosis + Sites group,
            Diagnosis group + All Site,
            Diagnosis group + Sites group
        ]
        
        These array elements will become the columns which will have the # of ROIs which satisfied the condition of outliers (using IQR)
        '''
        
        df.set_index(self.grouping_dict_diag_site_instance.subject_col, inplace=True)
        # Setting the column count for each subject for the 4 criteria
        for key_i in csv_grouping_arr:
            df[key_i+cnst.stringent_string]=0    #Count for strict quantile threshold for the current grouping 
            df[key_i+cnst.lenient_string]=0      #Count for strict quantile threshold for the current grouping 
            df[key_i+cnst.stringent_string+"_set"]=[set() for _ in range(len(df))]    #Set to add ROI which were outliers for that subject 
            df[key_i+cnst.lenient_string+"_set"]=[set() for _ in range(len(df))]    #Set to add ROI which were outliers for that subject
  
        
        for key_i in csv_grouping_arr:
            grouping_cols=self.grouping_dict_diag_site_instance.grouping_criteria[key_i] # Get columns based on which we will group them
            if grouping_cols:
                grouped_df=df.groupby(grouping_cols) # Get the grouped dataframe after grouping the main df based on the grouping_cols
                
                # Iterate through each grouped df and find the outliers
                for group_name, group_df in grouped_df:
                    group_df=self.IQR_based_helper_func(group_df,key_i,df_ROIs_col,file_name_suffix)
                    df[key_i+cnst.stringent_string] = df[key_i+cnst.stringent_string].add(group_df[key_i+cnst.stringent_string], fill_value=0) #Add the group_df outliers count to the main dataframe for Stringent threshold
                    df[key_i+cnst.lenient_string] = df[key_i+cnst.lenient_string].add(group_df[key_i+cnst.lenient_string], fill_value=0) #Add the group_df outliers count to the main dataframe for Lenient threshold

                    df[key_i+cnst.stringent_string+"_set"] = df[key_i+cnst.stringent_string+"_set"].combine(
                        group_df[key_i+cnst.stringent_string+"_set"], 
                        lambda x, y: x.union(y) if pd.notnull(y) else x,
                        fill_value=set()
                    )
                    
                    df[key_i+cnst.lenient_string+"_set"] = df[key_i+cnst.lenient_string+"_set"].combine(
                        group_df[key_i+cnst.lenient_string+"_set"], 
                        lambda x, y: x.union(y) if pd.notnull(y) else x,
                        fill_value=set()
                    )
            
            
            else:
                df=self.IQR_based_helper_func(df,key_i,df_ROIs_col,file_name_suffix)  #For the complete dataframe, you can replace the dataframe with the result from the function

        # df[key_i+cnst.stringent_string] = df[key_i+cnst.stringent_string].where(df[key_i+cnst.stringent_string] > threshold_stringent, 0)
        # df[key_i+cnst.lenient_string] = df[key_i+cnst.lenient_string].where(df[key_i+cnst.lenient_string] > threshold_lenient, 0)
        # df[key_i+cnst.stringent_string+"_set"] = df.apply(
        #             lambda row: set() if row[key_i+cnst.stringent_string] <= threshold_stringent else row[key_i+cnst.stringent_string+"_set"],
        #             axis=1
        #         )   
        # df[key_i+cnst.lenient_string+"_set"] = df.apply(
        #             lambda row: set() if row[key_i+cnst.lenient_string] <= threshold_lenient else row[key_i+cnst.lenient_string+"_set"],
        #             axis=1
        #         )   


        return df