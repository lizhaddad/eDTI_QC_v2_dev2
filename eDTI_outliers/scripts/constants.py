# Change if you want a new column header
across_data="Across_Diagnosis+Across_Sites"
across_diagnosis="Across_Diagnosis+Within_Sites"
across_site="Within_Diagnosis+Across_Sites"
diagnosis_site_group="Within_Diagnosis+Within_Sites"

criteria_1_string="Criteria1"
criteria_2_string="Criteria2"

stringent_string='+'+criteria_1_string
lenient_string='+'+criteria_2_string

# The ROI columns which we are interested i (ENIGMA DTI)
ROI_columns={'ic', 'cst.l', 'pcr.r', 'ec.l', 'cr', 'alic', 'gcc', 'ss.r', 'ec', 'cgh', 'rlic.l', 'ic.l', 'acr.r', 'alic.l', 'scc', 'plic', 'ss.l', 'fx', 'plic.r', 'bcc', 'unc.r', 'ifo.l', 'pcr', 'unc', 'slf.l', 'cst', 'ptr', 'ptr.r', 'ptr.l', 'rlic', 'cgc.l', 'fxst', 'rlic.r', 'sfo', 'cgc.r', 'slf.r', 'cgc', 'ss', 'cc', 'slf', 'cgh.l', 'sfo.r', 'averagefa', 'acr.l', 'cr.l', 'fx.st.l', 'cst.r', 'cgh.r', 'fx.st.r', 'ec.r', 'scr.r', 'scr', 'ic.r', 'acr', 'cr.r', 'plic.l', 'pcr.l', 'sfo.l', 'unc.l', 'alic.r', 'ifo', 'scr.l', 'ifo.r'}

# Setting the grouping criteria and the columns for those. Can change the name of the column by changing the key name.
class SingletonGrouping:
    _instance = None  # Class-level attribute for singleton instance

    def __new__(self, sitecol="", diagcol="",subjectcol="",quantile_lenient=[],quantile_stringent=[], threshold_1=0.1,threshold_2=0.05):
        # Ensure only one instance is created
        if self._instance is None:
            self._instance = super(SingletonGrouping, self).__new__(self)
        return self._instance

    def __init__(self, sitecol="", diagcol="",subjectcol="",quantile_lenient=[],quantile_stringent=[], threshold_1=0.1,threshold_2=0.05):
        # Initialize attributes only once
        if not hasattr(self, 'initialized'):
            self.site_col = sitecol
            self.diag_col = diagcol
            self.subject_col = subjectcol
            self.quantile_stringent=quantile_stringent
            self.quantile_lenient=quantile_lenient
            self.threshold_1=float(threshold_1)
            self.threshold_2=float(threshold_2)
            print("***************************************************************")
            self.criteria_string_mapper={
                                        criteria_1_string : "{}% of measures >{} or <{}]".format(self.threshold_1*100.0,self.quantile_stringent[0],self.quantile_stringent[1]),
                                        criteria_2_string : "{}% of measures >{} or <{}]".format(self.threshold_2*100.0,self.quantile_lenient[0],self.quantile_lenient[1]),
                                        }

            self.grouping_criteria = {
                across_data: [],
                across_diagnosis: [self.site_col],
                across_site: [self.diag_col],
                diagnosis_site_group: [self.diag_col, self.site_col]
            }
            self.initialized = True  # Mark instance as initialized

    #For resetting the instance if needed
    def reset_instance(self):
        self._instance = None


