import scrapy
import pandas as pd
import json
from ast import literal_eval
import os
import logging
import scrapy.item



class DF_product(scrapy.Item):
    District = scrapy.Field()
    District_Id = scrapy.Field()
    Tehsil = scrapy.Field()
    Tehsil_Id = scrapy.Field()
    Village = scrapy.Field()
    Village_Id = scrapy.Field()
    khasra_Count = scrapy.Field()



out_path = r'C:\Users\ABC\Downloads\matching Code\scarpping\Testing'
class MP_scrapy(scrapy.Spider):
    name= 'mp_bhulekh_2'
    start_urls = ["https://mpbhulekh.gov.in/dataReportFromHeaderHome.do?actionType=2"]
    

    def __init__(self):
        super().__init__()
        log_format = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        self.log = logging.getLogger('MP_scrapy')
        log_info = logging.FileHandler('log_MP_info.log',mode='w',encoding='utf-8')
        log_error = logging.FileHandler('log_MP_error.log',mode='w',encoding='utf-8')

        log_info.setFormatter(log_format)
        log_info.setLevel(logging.INFO)
        self.log.addHandler(log_info)

        log_error.setFormatter(log_format)
        log_error.setLevel(logging.ERROR)
        self.log.addHandler(log_error)
        self.log.setLevel(logging.INFO)



    def parse(self,response):
        print('*****')
        print(response)
        url = response.css("form#myForm::attr(action)").get()
        print(url)
        yield response.follow(url, callback=self.parse_next)

    def parse_next(self,response):
        try:
            first_drop = response.css("select[name='ddlDistrictId'] > option")
            district_list = []
            count = 1
            for districts in first_drop:
                if districts.css('::attr(value)').get()!='0':
                    dist = districts.css('::text').get()
                    value = districts.css('::attr(value)').get()
                    dist_dict = {'District':dist,'District_id':value}
                    district_list.append(pd.DataFrame([dist_dict]))
            self.log.info(f"The districts output: {district_list}")   
            for ind,rows in pd.concat(district_list).reset_index().iterrows():
                print(f"-----------------_ District ----------------------------- {rows['District']}")
                url_teh = response.urljoin('/UniSearch/getTehsils')
                dist_id = {"DistId": f"{rows['District_id']}"}
                meta = {"District":rows['District'],"District_id":rows['District_id']}
                
                yield scrapy.Request(url=url_teh,
                                    method="POST",
                                    body=json.dumps(dist_id),
                                    headers={'Content-Type': 'application/json'},
                                    dont_filter=True,
                                    meta=meta,
                                    callback= self.parse_teh)
        except Exception as e:
            self.log.error(f"The error: {e}, response: {response}",exc_info=True)

            
    
    def parse_teh(self,response):
        try:
            teh_list = []
            vil_list = []
            self.log.info(f"for the district: {response.meta['District_id']}: {json.loads(response.text)}")
            for lis in json.loads(response.text):
                tehs = {**{"District":response.meta['District'],"District_id":response.meta['District_id']},**{"Tehsil":lis['Tehsil_Name'],"Tehsil_id":lis['Tehsil_Id']}}
                teh_list.append(pd.DataFrame([tehs]))
            for ind, rows in pd.concat(teh_list).reset_index().iterrows():
                url_teh = response.urljoin('/UniSearch/getVillages')
                dist_id = {"DistId": f"{rows['District_id']}",
                        "TehsilId":f"{rows['Tehsil_id']}"}
                meta = {"District":rows['District'],"District_id":rows['District_id'],
                        "Tehsil":rows['Tehsil'],"Tehsil_id":rows['Tehsil_id']
                        }
                yield scrapy.Request(url=url_teh,
                                    method="POST",
                                    body=json.dumps(dist_id),
                                    headers={'Content-Type': 'application/json'},
                                    dont_filter=True,
                                    meta=meta,
                                    callback= self.parse_vil,
                                    cb_kwargs={'vil_list': vil_list})
        except Exception as e:
                self.log.error(f"The error: {e} response: {response}",exc_info=True)


    
    def parse_vil(self,response,vil_list):
        vilages_list =[]

        try:
            self.log.info(f"For district_id {response.meta['District_id']} and tehsil_id:{response.meta['Tehsil_id']}:{json.loads(response.text)}") 
            for vil in json.loads(response.text):
                        
                vil_dict = {**{"District":response.meta['District'],
                            "District_id":response.meta['District_id'],
                            "Tehsil":response.meta['Tehsil'],
                            "Tehsil_id":response.meta['Tehsil_id']},
                            **{"Village":vil['Village_Name'],"Village_id":vil['Village_Id']}}
                self.log.info(f"For district_id {response.meta['District_id']} and tehsil_id:{response.meta['Tehsil_id']}:{vil_dict}")
                vilages_list.append(vil_dict)

            # Create a DataFrame from vil_list
            df_villages = pd.DataFrame(vilages_list)
            
            # Iterate over each row in the DataFrame to send requests for khasra count
            for ind, rows in df_villages.iterrows():
                url_teh = response.urljoin('/UniSearch/getKhasraLst')
                dist_id = {
                    "DistId": str(rows['District_id']),
                    "TehsilId": str(rows['Tehsil_id']),
                    "VillageLgd": str(rows['Village_id'])
                }
                
                meta = {
                    "District": rows['District'],
                    "District_id": rows['District_id'],
                    "Tehsil": rows['Tehsil'],
                    "Tehsil_id": rows['Tehsil_id'],
                    "Village": rows['Village'],
                    "Village_id": rows['Village_id'] 
                }
                
                # Send request to get khasra count
                yield scrapy.Request(
                    url=url_teh,
                    method="POST",
                    body=json.dumps(dist_id),
                    headers={'Content-Type': 'application/json'},
                    dont_filter=True,
                    meta=meta,
                    callback=self.parse_khasra,
                    cb_kwargs={'khasra_list': vil_list}
                )
        except Exception as e:
                self.log.error(f"The error: {e}, response {response}",exc_info=True)
    
    
    def parse_khasra(self, response, khasra_list):
        try:
            try:
                # Parse khasra numbers from response
                try:
                    khasra_numbers = len(json.loads(response.text))  # Assuming khasra_numbers is a list in the response
                except Exception as e:
                    khasra_numbers = 0

                vil_dict = {"District":response.meta['District'],
                            "District_id":response.meta['District_id'],
                            "Tehsil":response.meta['Tehsil'],
                            "Tehsil_id":response.meta['Tehsil_id'],
                            "Village_Name": response.meta['Village'],
                            "Village_Id":response.meta['Village_id'],
                            "Khasra_Count": khasra_numbers
                            }

                khasra_list.append(vil_dict)
                district_id = response.meta['District'].split('|')[0].strip()
                pd.DataFrame(khasra_list).to_csv(os.path.join(out_path,f"MP_{district_id}.csv"),encoding='utf-8',index=False)
            except Exception as e:
                self.log.error(f"The error: {e}, response {response}",exc_info=True)
        
        except Exception as e:
            self.log.error(f"Error in parse_khasra: {e}, response {response}", exc_info=True)


            


            


            

        
        


        

                
        
        