from sites import Site
from pyllist import dllist, dllistnode
import pandas as pd
from energymodel import TddRtuModel
from ecm import EcmManager
from datetime import datetime
import os
from pathlib import Path

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

    def __to_dataframe(self):
        column_names = ['portfolio_id',
                        'site_count',
                        'asset_count',
                        'x_tons',
                        'x_hp',
                        'x_avg_age',
                        'x_avg_weighted_age',
                        'x_avg_eer',
                        'x_avg_weighted_eer',
                        'n_tons',
                        'n_hp',
                        'n_avg_age',
                        'n_avg_weighted_age',
                        'n_avg_eer',
                        'n_avg_weighted_eer',
                        'pre_kwh_hvac_yearly',
                        'post_kwh_hvac_yearly',
                        'sav_kwh_hvac_yearly',
                        'kwh_hvac_yearly_reduction_pct']
        values = [[self.id, 
                   self.site_count,
                   self.asset_count,
                   self.x_tons,
                   self.x_evap_hp,
                   self.x_avg_age,
                   self.x_avg_weighted_age,
                   self.x_avg_eer,
                   self.x_avg_weighted_eer,
                   self.n_tons,
                   self.n_evap_hp,
                   self.n_avg_age,
                   self.n_avg_weighted_age,
                   self.n_avg_eer,
                   self.n_avg_weighted_eer,
                   self.pre_kwh_hvac_yearly, 
                   self.post_kwh_hvac_yearly, 
                   self.sav_kwh_hvac_yearly,
                   self.kwh_hvac_reduction_pct]]
        return pd.DataFrame(values, columns=column_names)

    def __output_file_path(self, projectname):
        date = datetime.now()
        path = os.path.join("projects/" + 
                            projectname + 
                            "/output"
                            )
        return path

    def __output_file_name(self, projectname, filetype):
        date = datetime.now()
        path = os.path.join(projectname + 
                            "_" + 
                            filetype +
                            "_" +
                            str(date.year) + 
                            "_" +  
                            str(date.month) +
                            str(date.day) +
                            ".csv", 
                            )
        return path

    def __to_csv_wrapper(self, dataframe, filetype):
        output_file_path = Path(self.__output_file_path(self.id))
        output_file_name = self.__output_file_name(self.id, filetype)
        output_file_path.mkdir(parents=True, exist_ok = True)
        dataframe.to_csv(output_file_path / output_file_name, index = False)

    def portfolio_summary_table_to_csv(self, filename):
        print("Generating Portfolio Summary File")
        summary_df = self.__to_dataframe()
        self.__to_csv_wrapper(summary_df, "portfolio_summary")

    def site_summary_table_to_csv(self, filename):
        print("Generating Site Summary File")
        summary_df = pd.DataFrame()
        for x in self.site_list.iternodes():
            if (x !=None):
                site_df = x.value.to_dataframe()
                if (summary_df.empty == True):
                    summary_df = site_df
                else:
                    summary_df = summary_df.append(site_df, ignore_index = True)
        self.__to_csv_wrapper(summary_df, "site_summary")

    def proposal_summary_table_to_csv(self, filename):
        print("Generating Asset Summary File")
        summary_df = pd.DataFrame()
        for x in self.site_list.iternodes():
            if (x !=None):
                site_df = x.value.proposal_summary_table_dataframe()
                if (summary_df.empty == True):
                    summary_df = site_df
                else:
                    summary_df = summary_df.append(site_df, ignore_index = True)
        self.__to_csv_wrapper(summary_df, "asset_summary")

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
