#!/usr/bin/env python
# coding: utf-8
#Importing necessary libraries

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import numpy as np
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

#Creating a list to store the data
data=[]

#Setting up Selenium WebDriver with options
options=Options()
options.add_argument('--start-maximized')
options.add_argument('--headless')

#Launching the browser and navigating to the target URL
driver=webdriver.Chrome(options=options)
url="https://www.buyrentkenya.com/houses-for-rent"
driver.get(url)

#Function to wait for the page to load
def wait(drive,locator,t=20):
    wait=WebDriverWait(drive,t)
    wait.until(EC.visibility_of_element_located(locator))

#Function to click on cookies accept button
def click_cookies(drive):
    cookies=drive.find_element(By.ID, "onetrust-accept-btn-handler")
    drive.execute_script("arguments[0].scrollIntoView()",cookies)
    drive.execute_script("arguments[0].click()",cookies)
    
"""Waiting for page to load and  Accepting cookies
wait=WebDriverWait(driver, 20)
wait.until(EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler")))
click_cookies(driver)
time.sleep(3)"""

#Waiting for the page to load and accepting cookies
wait(driver,(By.ID, "onetrust-accept-btn-handler"))
click_cookies(driver)

 #Determining the total number of pages        
paginater=driver.find_element(By.CLASS_NAME,'mb-5').find_element(By.XPATH,"//ul[contains(@class, 'list-reset') and contains(@class, 'pagination-page-nav') and contains(@class, 'flex') and contains(@class, 'w-auto') and contains(@class, 'justify-center') and contains(@class, 'space-x-1') and contains(@class, 'p-0') and contains(@class, 'md:space-x-3')]")
all_pages=paginater.find_elements(By.TAG_NAME,"li")
pages=int(all_pages[-1].find_element(By.TAG_NAME,'a').text)

#Function to click on the next page button
def click_next_page():
    next_cont=driver.find_element(By.XPATH, "//*[contains(@class, 'mt-4') and contains(@class, 'flex') and contains(@class, 'w-full') and contains(@class, 'flex-row') and contains(@class, 'items-center') and contains(@class, 'justify-center') and contains(@class, 'space-x-1') and contains(@class, 'md:space-x-3')]")
    next_link=next_cont.find_elements(By.TAG_NAME,'a')
    driver.execute_script("arguments[0].click()",next_link[-1])


#Function to extract data from the page
def get_data(soup):
    listings=soup.find_all('div','listing-card')
    for count,listing in enumerate(listings):
        amn=[]
        container=listing.find('div','md:w-3/5 relative flex flex-col justify-between px-3 py-4 md:px-5')
        house_details=container.find('div','block flex flex-col justify-between gap-y-3 overflow-hidden')
        link=container.find('a','absolute left-0 top-0 z-10 h-full w-full')['href']
        house_link=urljoin(url,link)
        title=house_details.find('h2','font-semibold md:hidden').get_text(strip=True)
        #desc=house_details.find('h3','block flex-1 text-sm font-medium leading-5 text-black text-grey-850 md:hidden').text.strip()
        #location=house_details.find('div','flex max-w-full items-center').p.text.strip()
        location=house_details.find('div','max-w-full flex items-center gap-x-1').p.text.strip()
        price_div=house_details.find('h3','capitalize flex')
        classes=[
            'flex items-center justify-center text-xl font-bold leading-7 text-grey-900',
            'inline-flex justify-between text-xl font-bold leading-7 text-grey-850 md:hidden']
        for cls in classes:
            price_details=price_div.find('div',cls)
            if price_details:
                price=price_details.find('a').get_text(strip=True)
                break
        washrooms=house_details.find('div','swiper-wrapper space-x-2')
        try:
            beds=washrooms.find('div','swiper-slide flex h-6 !w-auto items-center rounded-full bg-highlight px-2 py-1 text-sm font-normal leading-4 text-grey-550 swiper-slide-active')
            bedrooms=beds.span.get_text(strip=True)
        except:
            bedrooms=np.nan
        try:
            baths=washrooms.find('div','swiper-slide flex h-6 !w-auto items-center rounded-full bg-highlight px-2 py-1 text-sm font-normal leading-4 text-grey-550 swiper-slide-next')
            bathrooms=baths.span.get_text(strip=True)
        except:
            bathrooms=np.nan
        try:
            areas=washrooms.find('div','swiper-slide flex h-6 !w-auto items-center rounded-full bg-highlight px-2 py-1 text-sm font-normal leading-4 text-grey-550')
            area=areas.find('span').get_text(strip=True)
        except:
            area=np.nan
        #Navigating to the secondary page for more details
        sec_driver=webdriver.Chrome(options=options)
        sec_driver.get(house_link)
        
        """""
        sec_wait=WebDriverWait(sec_driver,20)
        sec_wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        #wait(sec_driver,(By.ID, "onetrust-accept-btn-handler"))"""
        #Waiting for the secondary page to load and accepting cookies
        wait(sec_driver,(By.ID, "onetrust-accept-btn-handler"))
        click_cookies(sec_driver)
        time.sleep(3)
        
        sec_soup=BeautifulSoup(sec_driver.page_source, 'html.parser')
        main=sec_soup.select_one(".container.mx-auto.flex.flex-col.md\\:mb-10.lg\\:flex-row.lg\\:flex-nowrap")
        sections=main.select('.px-3.md\\:px-0.py-3')
        desc=sections[1].find(attrs={'id':"truncatedDescription"}).get_text(strip=True)
        description=''.join(desc.split("\n"))#.replace("* \u2060"," ")
        created_at=sections[2].select_one(".flex.w-full.justify-between.py-2").span.get_text(strip=True)
        try:
            amenities=main.select_one(".px-0.py-3.md\\:pt-6").find('div',class_="gap-y-2").select(".flex.w-full.flex-col")
            for amenity in amenities:
                headers=amenity.select(".px-3.py-3.even\\:bg-gray-50")
                for header in headers:
                    am=[x.get_text(strip=True) for x in header.select_one(".flex.flex-wrap.gap-3").find_all('span')]
                    amn.append(am) 
        except:
            amn.append([])

        agency=sec_soup.select_one(".flex.w-full.md\\:pl-4").select_one(".flex.flex-col.justify-center.space-y-3.px-4.pl-8")
        agency_link=agency.a.get('href')
        agency_name=agency.p.get_text(strip=True)
        phone=sec_driver.find_element(By.CSS_SELECTOR,".agent-contact-enquiry.mb-10.flex.flex-col.items-center.space-y-3.md\\:mb-5")
        #.find_element(By.CSS_SELECTOR,".h-full.w-full.flex-1.space-y-3.rounded-t.p-0")
        button=phone.find_element(By.TAG_NAME,'button')
        sec_driver.execute_script("arguments[0].scrollIntoView()",button)
        sec_driver.execute_script("arguments[0].click()",button)
        time.sleep(5)
        number=sec_driver.find_element(By.CSS_SELECTOR,".flex.cursor-pointer.flex-col.items-center.justify-center.space-y-1.rounded-2xl.bg-secondary-500.py-3.text-center.text-white.md\\:cursor-default.md\\:bg-secondary-50.md\\:text-secondary-500")
        agency_number=number.find_element(By.CSS_SELECTOR,".items-center.justify-center.space-y-1").find_element(By.TAG_NAME,'span').text
        sec_driver.quit()
        data.append(
            {
                'posted_on':created_at,
                'title':title,
                'description':description,
                'location':location,
                'area':area,
                'price':price,
                'bedrooms':bedrooms,
                'bathrooms':bathrooms,
                'house_link':house_link,
                'amenities':amn,
                'agencyName':agency_name,
                'agencyNumber':agency_number,
                'agentLink':agency_link,
            })
        print(f'listing {count+1} done')
 
#Looping through all pages and extracting basic and secondary data
for page in range(pages):
    wait(driver,(By.CLASS_NAME,"listing-card"))
    soup=BeautifulSoup(driver.page_source, 'html.parser')
    get_data(soup)
    click_next_page()
    print(f'page {page+1} done')

#Saving data to a CSV file
fields=['posted_on','title', 'description', 'location', 'area', 'price', 'bedrooms', 'bathrooms','house_link','amenities','agencyName','agencyNumber','agentLink']
with open('trial.csv','w',newline='',encoding='utf-8') as obj:
    writer=csv.DictWriter(obj,fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)

#Closing the browser
driver.quit()

