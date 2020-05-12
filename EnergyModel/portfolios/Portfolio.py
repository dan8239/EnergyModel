from sites import Site
from pyllist import dllist, dllistnode
import pandas as pd
from energymodel import TddRtuModel
from ecm import EcmManager
from datetime import datetime
import os
from pathlib import Path
from climdata import HourlyDataManager

class Portfolio():
    def __init__(self, id, model_type = "TDD"):
        self.id = id
        self.site_list = dllist()
        if (model_type == "TDD"):
            self.energy_model = TddRtuModel.TddRtuModel()
        else:
            self.energy_model = None
        self.site_count = 0
        self.asset_count = 0
        self.x_tons = 0
        self.x_evap_hp = 0
        self.x_avg_age = 0
        self.x_avg_weighted_age = 0
        self.x_avg_eer = 0
        self.x_avg_weighted_eer = 0
        self.n_tons = 0
        self.n_evap_hp = 0
        self.n_avg_age = 0
        self.n_avg_weighted_age = 0
        self.n_avg_eer = 0
        self.n_avg_weighted_eer = 0
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0
        self.kwh_hvac_reduction_pct = 0
        self.ecm_manager = EcmManager.EcmManager()
        self.hourly_data_manager = HourlyDataManager.HourlyDataManager()
        self.update_input_file_flag = False

    def add_site(self, site):
        if (not isinstance(site, Site.Site)):
            raise TypeError("Cannot add a non Site type to portfolio Site_list")
        self.site_list.appendright(site)
        site.portfolio = self

    def find_site(self, site_name):
        for x in self.site_list.iternodes():
            if (x.value.id == site_name):
                return x.value
        return None

    def add_ecm_list(self, ecm_description):
        self.ecm_manager.add_ecm_list(ecm_description)

    def get_ecm_list(self, ecm_description):
        return self.ecm_manager.get_ecm_list(ecm_description)

    def add_ecm(self, ecm_description, ecm):
        self.ecm_manager.add_ecm(ecm_description, ecm)

    def filter_assets(self):
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.filter_assets()

    def apply_ecms(self):
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.apply_ecms()

    def run_energy_calculations(self):
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.run_energy_calculations(self.energy_model)
        self.update_energy_totals()

    def update_energy_totals(self):
        self.pre_kwh_hvac_yearly = 0
        self.post_kwh_hvac_yearly = 0
        self.sav_kwh_hvac_yearly = 0
        self.pre_therms_hvac_yearly = 0
        self.post_therms_hvac_yearly = 0
        self.sav_therms_hvac_yearly = 0

        self.site_count = self.site_list.size
        self.asset_count = 0
        self.x_tons = 0
        self.x_evap_hp = 0
        x_age_tot = 0
        x_age_tons_tot = 0
        x_eer_tot = 0
        x_eer_tons_tot = 0
        self.n_tons = 0
        self.n_evap_hp = 0
        n_age_tot = 0
        n_age_tons_tot = 0
        n_eer_tot = 0
        n_eer_tons_tot = 0

        for x in self.site_list.iternodes():
            if (x !=None):
                #asset count
                self.asset_count = self.asset_count + x.value.asset_count

                #existing asset sums
                self.x_tons = self.x_tons + x.value.x_tons
                self.x_evap_hp = self.x_evap_hp + x.value.x_evap_hp
                x_age_tot = x_age_tot + x.value.x_avg_age * x.value.asset_count
                x_age_tons_tot = x_age_tons_tot + x.value.x_avg_weighted_age * x.value.x_tons
                x_eer_tot = x_eer_tot + x.value.x_avg_eer * x.value.asset_count
                x_eer_tons_tot = x_eer_tons_tot + x.value.x_avg_weighted_eer * x.value.x_tons

                #new asset sums
                self.n_tons = self.n_tons + x.value.n_tons
                self.n_evap_hp = self.n_evap_hp + x.value.n_evap_hp
                n_age_tot = n_age_tot + x.value.n_avg_age * x.value.asset_count
                n_age_tons_tot = n_age_tons_tot + x.value.n_avg_weighted_age * x.value.n_tons
                n_eer_tot = n_eer_tot + x.value.n_avg_eer * x.value.asset_count
                n_eer_tons_tot = n_eer_tons_tot + x.value.n_avg_weighted_eer * x.value.n_tons

                # energy calc sums
                self.pre_kwh_hvac_yearly = self.pre_kwh_hvac_yearly + x.value.pre_kwh_hvac_yearly
                self.post_kwh_hvac_yearly = self.post_kwh_hvac_yearly + x.value.post_kwh_hvac_yearly
                self.sav_kwh_hvac_yearly = self.sav_kwh_hvac_yearly + x.value.sav_kwh_hvac_yearly
                self.pre_therms_hvac_yearly = self.pre_therms_hvac_yearly + x.value.pre_therms_hvac_yearly
                self.post_therms_hvac_yearly = self.post_therms_hvac_yearly + x.value.post_therms_hvac_yearly
                self.sav_therms_hvac_yearly = self.sav_therms_hvac_yearly + x.value.sav_therms_hvac_yearly
        
        if (self.pre_kwh_hvac_yearly):
            self.kwh_hvac_reduction_pct = self.sav_kwh_hvac_yearly / self.pre_kwh_hvac_yearly
        else:
            self.kwh_hvac_reduction_pct = 0

        if (self.asset_count):
            self.x_avg_age = x_age_tot / self.asset_count
            self.x_avg_eer = x_eer_tot / self.asset_count
            self.n_avg_age = n_age_tot / self.asset_count
            self.n_avg_eer = n_eer_tot / self.asset_count
        else:
            self.x_avg_age = 0
            self.x_avg_eer = 0
            self.n_avg_age = 0
            self.n_avg_eer = 0
        if (self.x_tons):
            self.x_avg_weighted_age = x_age_tons_tot / self.x_tons
            self.x_avg_weighted_eer = x_eer_tons_tot / self.x_tons
            self.n_avg_weighted_age = n_age_tons_tot / self.n_tons
            self.n_avg_weighted_eer = n_eer_tons_tot / self.n_tons
        else:
            self.x_avg_weighted_age = 0
            self.x_avg_weighted_eer = 0
            self.n_avg_weighted_age = 0
            self.n_avg_weighted_eer = 0


    def to_excel_file(self):
        # create folders if not existing, get folder path
        path = self.__output_file_path()
        # append file name to path
        filename = self.__output_file_name(path)
        # get dataframe summaries
        portfolio_table_df = self.__to_dataframe()
        site_table_df = self.__site_list_to_dataframe()
        asset_table_df = self.__asset_list_to_dataframe()
        # write to excel file with individual sheets
        writer = pd.ExcelWriter(filename, engine = 'xlsxwriter')
        portfolio_table_df.to_excel(writer, sheet_name = 'portfolio', index = False)
        site_table_df.to_excel(writer, sheet_name = 'site', index = False)
        asset_table_df.to_excel(writer, sheet_name = 'asset', index = False)
        writer.save()
        writer.close()

    def dump(self):
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXX PORTFOLIO XXXXXXXXXXXX")
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("ID: " + str(self.id))
        print("Total Sites:" + str(self.site_list.size))
        print("Pre KWH: " + str(self.pre_kwh_hvac_yearly))
        print("Post KWH: " + str(self.post_kwh_hvac_yearly))
        print("Saved KWH: " + str(self.sav_kwh_hvac_yearly))
        for x in self.site_list.iternodes():
            if (x != None):
                x.value.dump()
        print()

    #------------------------PRIVATE METHODS------------------------------------------#

    def __to_dataframe(self):
        colnames = vars(self).keys()    #vars gets dict from object. Keys gets keys from dict key-value pairs
        df = pd.DataFrame([[getattr(self, j) for j in colnames]], columns = colnames) #get attributes in a row
        df = df.drop(['site_list',
                      'energy_model',
                      'ecm_manager',
                      'x_avg_weighted_age',
                      'x_avg_weighted_eer',
                      'n_avg_weighted_age',
                      'n_avg_weighted_eer',
                      'pre_therms_hvac_yearly',
                      'post_therms_hvac_yearly',
                      'update_input_file_flag',
                      'sav_therms_hvac_yearly'], axis = 1)   #drop object references and unneeded columns
        return df

    def __output_file_path(self):
        date = datetime.now()
        #string path
        path = os.path.join("projects/" + 
                            self.id + 
                            "/output"
                            )
        #path path
        output_file_path = Path(path)
        #create folders if not existing
        output_file_path.mkdir(parents=True, exist_ok = True)
        #return only string
        return path

    def __output_file_name(self, path):
        date = datetime.now()
        filename = os.path.join(path + 
                            "/" +
                            self.id + 
                            "_energy_summary_" + 
                            str(date.year) + 
                            "_" +  
                            str(date.month) +
                            "_" +
                            str(date.day) +
                            "_" +
                            str(date.hour) +
                            "_" +
                            str(date.minute) +
                            ".xlsx", 
                            )
        return filename

    def __site_list_to_dataframe(self):
        print("Generating Site Summary Table")
        summary_df = pd.DataFrame()
        for x in self.site_list.iternodes():
            site_df = x.value.to_dataframe()
            if (summary_df.empty == True):
                summary_df = site_df
            else:
                summary_df = summary_df.append(site_df, ignore_index = True)
        return summary_df

    def __asset_list_to_dataframe(self):
        print("Generating Asset Summary Table")
        summary_df = pd.DataFrame()
        for x in self.site_list.iternodes():
            if (x !=None):
                site_df = x.value.proposal_summary_table_dataframe()
                if (summary_df.empty == True):
                    summary_df = site_df
                else:
                    summary_df = summary_df.append(site_df, ignore_index = True)
        return summary_df