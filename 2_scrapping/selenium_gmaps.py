# Given the names of companies it will search on gmaps and collects the addresses and geocodes.
# Sometimes there may be a list of companies with same name, so cant find a particular address. That names are stored separately. 


import csv
import copy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import time

def open_page():
    
    global browser
    options = Options()
    options.headless = False
    browser = webdriver.Firefox(options=options)# I've used firefox browser
    browser.get('https://www.google.com/maps/@10.8091781,78.2885026,7z/hl=en')
    
def get_address(name):
    name = name.replace(' from ',' ').replace(' From ',' ').replace(' FROM ',' ').replace(' to ',' ')   
    elem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
    elem.send_keys(name)
    search = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "searchbox-searchbutton")))
    search.click()
    
    time.sleep(8)
    url = browser.current_url
    try :
        s = copy.deepcopy(url)
        a = s.find('@')
        s = s[a+1:]
        b = s.find('/')
        s = s[:b]
        s = s.split(',')
        geocodes = (float(s[0]),float(s[1]))
    except ValueError:
        try:
            s = copy.deepcopy(url)
            a = s.find('@')
            s = s[a+1:]
            a = s.find('@')
            s = s[a+1:]
            b = s.find('/')
            s = s[:b]
            s = s.split(',')
            geocodes = (float(s[0]),float(s[1]))
        except ValueError:
            s = copy.deepcopy(url)
            name.replace('/','%2F')
            l = len(name) + 34
            s = s[l:]
            a = s.find('@')
            s = s[a+1:]
            b = s.find('/')
            s = s[:b]
            s = s.split(',')
            geocodes = (float(s[0]),float(s[1]))
    results =  browser.find_elements_by_css_selector(".ugiz4pqJLAG__primary-text")
    if results==[]:
        clear = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gsst_a")))
        clear.click()
        return None,None,None,url
    header = browser.find_element_by_class_name("section-hero-header-title-description")
    title = header.find_element_by_xpath(".//h1")
    name=title.text
    address=results[0].text
    
    clear = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gsst_a")))
    clear.click()
    
    return name,address,geocodes,url 

def get_list(name):
    name = name.replace('from','').replace('From','').replace('FROM','').replace('to','')    
    elem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
    elem.send_keys(name)
    
    search = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "searchbox-searchbutton")))
    search.click()
    
    c_list=[]
    time.sleep(4)
    url = browser.current_url
    results =  browser.find_elements_by_class_name("section-result")
    for result in results:
        title = result.find_element_by_xpath(".//h3")
        name=title.text
        if name!='Bengaluru':
             c_list.append(name)
    
    clear = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "gsst_a")))
    clear.click()
    
    return c_list 

    
def kill():    
    browser.quit()    

open_page()
unknown_list=[]
c_names = []
d={}
with open("cleaned_location_data.csv") as location_file:
    location_reader = csv.reader(location_file, delimiter=',')
    for row in location_reader:
        cname = row[0]
        if (cname not in d) and cname!="Bengaluru":
            c_names.append(row[0])
            d[cname]=1

print(len(d))
n=len(c_names)
dic={}
with open("gmap_address_list.csv", mode='r') as address_list:
    location_reader = csv.reader(address_list, delimiter=',')
    for row in location_reader:
        cname = row[0]
        dic[cname]=1
with open("gmaps_unknown_cname_list.csv", mode='r') as address_list:
    location_reader = csv.reader(address_list, delimiter=',')
    for row in location_reader:
        cname = row[0]
        dic[cname]=1

a,b,c,d = get_address('SRIB')
print(len(dic))
with open("gmap_address_list.csv", mode='a') as address_list, \
open("gmaps_unknown_cname_list.csv", mode='a') as unknown_list:
    address_writer = csv.writer(address_list)
    unknown_cname_writer = csv.writer(unknown_list)
    for i in range(19904,25000):
        print(i)
        name, address, geocodes, url = get_address(c_names[i]+" Bangalore")
        if name==None:
            c_list = get_list(c_names[i]+" Bangalore")
            for c_name in c_list:
                if c_name not in dic:
                    name, address, geocodes, url = get_address(c_name+" Bangalore")
                    if name==None:
                        print("{} Sorry, {} is not Available".format(i,c_name))
                        unknown_cname_writer.writerow([c_name,url])
                        dic[c_name]=1
                    else:
                        if name not in dic:
                            print(i,name,address,geocodes)
                            address_writer.writerow([name,address,geocodes,url])
                            dic[name]=1
        else:
            if name not in dic:
                print(i,name,address, geocodes)
                address_writer.writerow([name,address,geocodes,url])
                dic[name]=1

kill()
