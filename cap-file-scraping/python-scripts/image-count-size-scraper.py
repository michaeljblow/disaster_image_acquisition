#!/usr/bin/env python
# coding: utf-8

# In[23]:


import pandas as pd
from selenium import webdriver
import time

# Requesting user to input desired FEMA "event number"
event_number = event_number = input("Enter Event Number:\n ")

# Assigning browser to be Firefox
driver = webdriver.Firefox()

# Setting base url
base_url = 'http://fema-cap-imagery.s3-website-us-east-1.amazonaws.com/Images/'

url = f'{base_url}{event_number}/'

url

# Collecting page data
driver.get(url)
time.sleep(5)

# Pulling everything under the 'listing' element into a variable and converting to list
main_list = driver.find_element_by_id('listing').text.split()

# Generating list individual flight events
# Checking against substrings and removing '/' from each itme
flight_list = [i.strip('/') for i in main_list if ('/' in i) and ('..' not in i)]

flight_list

# Instantiating empty list to store all file size numbers
file_sizes = []

# Loop through each flight event and 
for flight in flight_list:
    temp_url = f'{url}{flight}/'
    driver.get(temp_url)
    time.sleep(5)
    temp_image_file_size_list = driver.find_element_by_id('listing').text.split()
    temp_image_file_size_list = [float(i) for i in temp_image_file_size_list if (len(i) <= 5) and ('..' not in i) and ('.' in i)]
    file_sizes = file_sizes + temp_image_file_size_list

# Closing Firefox
driver.close()

print(f'Total image count : {len(file_sizes)}')
print(f'Total file count  : {round((sum(file_sizes)/1000), 2)} GB')
print(f'Largest File Size : {max(file_sizes)} MB')

