#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Imports
import pandas as pd
import time
import requests
import os

from selenium import webdriver
from pathlib import Path

# Begining timer
t0 = time.time()

# Requesting user to enter FEMA site "event number"
event_number = input("Enter Event Number:\n ")

# Requesting user to enter FEMA site "flight number"
flight_number = input("Enter Flight Number:\n ")

# Requesting time to sleep between image grabs. Allows user to set larger in low bandwidth situations
sleep_number = float(input("Enter time to wait between image grabs. \nConsider larger values for low bandwidth connections.\n"))

# Creating directory variable
directory = f'event_{event_number}_flight_{flight_number}'

# Creating Directory on user's Desktop based on event number
os.mkdir(os.path.abspath(Path.home()) + f'/Desktop/{directory}/')

# Assigning browser to be Firefox
driver = webdriver.Firefox()
# Sleep to allow for browser to load on slower systems
time.sleep(3)

# Setting base url
base_url = (f'http://fema-cap-imagery.s3-website-us-east-1.amazonaws.com/Images/{event_number}/')

# Collecting page data
driver.get(base_url + flight_number + '/')
time.sleep(5)

# Creating dataframe to be used as log
scrape_log = pd.DataFrame(columns=('Status Code', 'Time of Grab', 'File Name'))

# Function to grab image and write to flight specific directory
def image_grab(image, flight, event):
    # Setting scrape_log dataframe to be global so it can be added to
    global scrape_log
    global directory
    # Setting image url based on directory parameters 
    image_url = f'https://s3.amazonaws.com/fema-cap-imagery/Images/{event}/{flight}/{image}'
    # Grabbing local machine time for use in log
    grab_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # Requesting image
    image_grab_request = requests.get(image_url)
    # Sleep is to allow image time to load
    time.sleep(sleep_number)
    # Getting request status code
    status_code = image_grab_request.status_code
    # Generating file name for writing and log
    file_name = f'{event}_{flight}_{image}'
    # Dataframe of current pull to append to scraper_log
    temp_scrape_log = pd.DataFrame(
        {
            'Status Code'  : [status_code],
            'Time of Grab' : grab_time,
            'File Name'    : file_name
        }
    )
    # Updating and writing scraper_log
    scrape_log = (scrape_log.append(temp_scrape_log)).reset_index(drop=True)
    scrape_log.to_csv((os.path.abspath(Path.home()) + (f'/Desktop/{directory}/scrape-log.csv')))
    # Writing image to disk
    open(os.path.expanduser(f'~/Desktop/{directory}/{file_name}'), 'wb').write(image_grab_request.content)


# Calling list of all image file names
temp_image_file_list = driver.find_element_by_id('listing').text.split()
temp_image_file_list = [i for i in temp_image_file_list if '.jpg' in i]

# Running through each file with a check for an error and to retry if server times out on image request
for image in temp_image_file_list:
    try:
        image_grab(image, flight_number, event_number)
    except:
        print('Failure Occured')
        # Giving time for server to potentially fix whatever blip occured and trying request again
        time.sleep(30)
        print('Trying again after sleep')
        image_grab(image, flight_number, event_number)
        print('Trying again')

            
# Closing Firefox
driver.close()

# Ending timer and printing run time
print(f'Total time for scraping: {round((time.time() - t0), 2)}')

