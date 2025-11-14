import time
import csv
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options=Options()
options.add_argument('--start-maximized')
#options.add_argument('--headless')

driver=webdriver.Chrome(options=options)
url="https://www.buyrentkenya.com/houses-for-rent"
driver.get(url)
time.sleep(10)  # Wait for the page to load completely

cookies=driver.find_element(By.ID, "onetrust-accept-btn-handler")
driver.execute_script("arguments[0].scrollIntoView()",cookies)
cookies.click()

def houses(soup):
    listings=soup.find_all('div','listing-card')
    for listing in listings:
        container=listing.find('div','md:w-3/5 relative flex flex-col justify-between px-3 py-4 md:px-5')
        house_details=container.find('div','block flex flex-col justify-between gap-y-3 overflow-hidden')
        #owner_details=container.find('flex items-center justify-between space-x-1 pt-2 md:h-[48px] md:space-x-0')
        link=container.find('a','absolute left-0 top-0 z-10 h-full w-full')['href']
        house_link=urljoin(url,link)
        title=house_details.find('h2','font-semibold md:hidden').get_text(strip=True)
        desc=house_details.find('h3','block flex-1 text-sm font-medium leading-5 text-black text-grey-850 md:hidden').text.strip()
        location=house_details.find('div','flex max-w-full items-center').p.text.strip()
        house_details.find('h3','block flex-1 text-sm font-medium leading-5 text-black text-grey-850 md:hidden').text.strip()
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
        data.append(
            {
            'title':title,
            'desc':desc,
            'location':location,
            'area':area,
            'price':price,
            'bedrooms':bedrooms,
            'bathrooms':bathrooms,
            'house_link':house_link
            }
            )


def click_next_page():
    next_cont=driver.find_element(By.XPATH, "//*[contains(@class, 'mt-4') and contains(@class, 'flex') and contains(@class, 'w-full') and contains(@class, 'flex-row') and contains(@class, 'items-center') and contains(@class, 'justify-center') and contains(@class, 'space-x-1') and contains(@class, 'md:space-x-3')]")
    next_link=next_cont.find_elements(By.TAG_NAME,'a')
    driver.execute_script("arguments[0].click()",next_link[-1])
    


paginater=driver.find_element(By.CLASS_NAME,'mb-5').find_element(By.XPATH,"//ul[contains(@class, 'list-reset') and contains(@class, 'pagination-page-nav') and contains(@class, 'flex') and contains(@class, 'w-auto') and contains(@class, 'justify-center') and contains(@class, 'space-x-1') and contains(@class, 'p-0') and contains(@class, 'md:space-x-3')]")
all_pages=paginater.find_elements(By.TAG_NAME,"li")
pages=int(all_pages[-1].find_element(By.TAG_NAME,'a').text)

data=[]
for page in range(3):
    wait=WebDriverWait(driver, 20)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "listing-card")))
    page_soup=BeautifulSoup(driver.page_source, "html.parser")
    houses(page_soup)
    click_next_page()


fields=['title', 'desc', 'location', 'area', 'price', 'bedrooms', 'bathrooms','house_link']
with open('data/houses.csv','w',newline='',encoding='utf-8') as obj:
    writer=csv.DictWriter(obj,fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)


driver.quit()

