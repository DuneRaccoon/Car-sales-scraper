from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from collections import defaultdict
from tqdm import tqdm
import csv

class CarSalesSpider:

    def __init__(self,
                 this_url = None,
                 car_manufacturer = None,
                 year_min = None,
                 year_max = None,
                 car_type = None,
                 car_model = None,
                 car_series = None,
                 car_badge = None,
                 gear_type = None
                 ):
        if not this_url:
            self.data_types = ['Premium','Standard','Showcase']
            self.car_manufacturer = car_manufacturer
            self.year_min = year_min
            self.year_max = year_max
            self.car_type = car_type
            self.car_model = car_model
            self.car_series = car_series
            self.car_badge = car_badge
            self.gear_type = gear_type
            self.all_urls = self.extract_urls()
            self.car_data = self.get_car_data(self.all_urls)
        else:
            self.url = this_url

        self.my_car_dep_per_km = 0.15
        self.my_car_odometer = 79816

    def page_scraper(self,this_url=None,p=1):
        if not this_url:
            url = f'https://www.carsales.com.au/cars/results?offset={(p*12)-12}&setype=pagination&q=%28And.Year.range%280{self.year_min}..{self.year_max}%29._.Service.Carsales._.BodyStyle.{self.car_type}._.%28C.Make.{self.car_manufacturer}._.%28C.Model.{self.car_model}._.%28And.Series.{self.car_series}._.Badge.{self.car_badge}.%29%29%29_.GenericGearType.{self.gear_type}.%29&sortby=TopDeal&limit=12'
        else:
            url = this_url
        html = urlopen(url)
        soup = bs(html,'html.parser')
        return soup

    def extract_urls(self):
        page = 1
        all_car_urls = []
        while True:
            print('Getting page ',page)
            current_page = self.page_scraper(p=page)
            if current_page.find('div',{'class':'no-results-header'}):
                return all_car_urls
            for d in self.data_types:
                current_data = current_page.findAll('div',{'data-type':d})
                if current_data:
                    for container in current_data:
                        all_car_urls.append\
                        ('https://www.carsales.com.au' + container.find('div',\
                        {'class':'action-buttons n_align-right n_width-min'}).a['href'])
            page += 1

    def get_car_data(self,urls):
        total_car_data = []
        for url in tqdm(urls):
            car_data = {}
            current_page = self.page_scraper(this_url=url)
            car_data['car_title'] = \
            ' '.join(current_page.find('div',{'class':'details-title'}).h1.text.split())
            car_data['year_model'] = car_data['car_title'].split()[0]
            car_data['price'] = current_page.find('div',{'class':'price'}).text.strip('*')
            car_data['odometer'] = \
            current_page.find('div',\
            {'class':'col features-item-value features-item-value-kilometers'}).text.strip().strip(' km')
            car_data['colour'] = \
            current_page.find('div',\
            {'class':'col features-item-value features-item-value-colour'}).text.strip()
            if current_page.find('div',\
            {'class':'col features-item-value features-item-value-roadworthy-safety-certificate'}):
                car_data['safety_certificate'] = \
                current_page.find('div',\
                {'class':'col features-item-value features-item-value-roadworthy-safety-certificate'}).text.strip()
            else:
                car_data['safety_certificate'] = 'No'
            if current_page.find('div',\
            {'class':'col features-item-value features-item-value-registration-expiry'}):
                car_data['reg_expiry'] = \
                current_page.find('div',\
                {'class':'col features-item-value features-item-value-registration-expiry'}).text.strip()
            else:
                car_data['reg_expiry'] = 'Expired'
            car_data['transmission'] = \
            current_page.find('div',\
            {'class':'col features-item-value features-item-value-transmission'}).text.strip()
            car_data['body'] = \
            current_page.find('div',\
            {'class':'col features-item-value features-item-value-body'}).text.strip()
            car_data['link'] = url
            total_car_data.append(car_data)
        return total_car_data
            
    def return_csv(self,file_name='car_sales_data.csv'):
        with open(file_name,'w',newline='') as car:
            fieldnames = ['car_title','year_model','price','odometer','colour',
                          'safety_certificate','reg_expiry','transmission','body','link']
            writer = csv.DictWriter(car,fieldnames=fieldnames)
            writer.writeheader()
            for data in self.car_data:
                writer.writerow(data)

if __name__ == '__main__':

    car = CarSalesSpider(car_manufacturer = 'Volkswagen',year_min='2012',year_max='2013',
                     car_type='Hatch',car_model='Golf',car_series='VI',car_badge='77TSI',
                     gear_type='Automatic')
    car.return_csv(file_name='new_car_data.csv')
