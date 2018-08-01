import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import os
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")

def grabber_newsbitcoin(load_times, mode):
    executable_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/driver/chromedriver'
    html = "http://news.bitcoin.com"
    cur_time = int(time.time())
    recept_period = 24*60*60
    end_time = cur_time
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
    browser.get(html)

    TIME_OUT = 1
    titles = np.array([])
    update_times = np.array([])
    PAGE_OUT = 50

    if mode == 0:
        while load_times and PAGE_OUT:
            try:
                page_titles_element = browser.find_elements_by_xpath("//div[@class='item-details']/h3")
                page_titles = [x.text for x in page_titles_element]
                page_update_time_elememts = browser.find_elements_by_xpath("//div[@class='item-details']/div/span/time")
                page_update_times = []
                for page_update_time in page_update_time_elememts:
                    page_update_times.append(page_update_time.get_attribute("datetime"))
                titles = np.append(titles, page_titles)
                update_times = np.append(update_times, page_update_times)
            except Exception:
                PAGE_OUT -= 1

            try:
                browser.find_element_by_class_name(
                    "td-icon-menu-right").click()
                load_times -= 1
                print("=====load page====", load_times)
                WebDriverWait(browser, TIME_OUT).until(
                    EC.visibility_of_element_located((
                        By.CLASS_NAME, "td-icon-menu-right")))
            except Exception:
                print('load out')

    if mode == 1:
        while cur_time - end_time < recept_period and PAGE_OUT:
            try:
                page_titles_element = browser.find_elements_by_xpath("//div[@class='item-details']/h3")
                page_titles = [x.text for x in page_titles_element]
                page_update_time_elememts = browser.find_elements_by_xpath("//div[@class='item-details']/div/span/time")
                page_update_times = []
                for page_update_time in page_update_time_elememts:
                    page_update_times.append(page_update_time.get_attribute("datetime"))
                titles = np.append(titles, page_titles)
                update_times = np.append(update_times, page_update_times)
                end_time = int(datetime.datetime.strptime(update_times[-1], '%Y-%m-%dT%H:%M:%S+00:00').timestamp() + 32400)
            except Exception:
                PAGE_OUT -= 1

            try:
                browser.find_element_by_class_name(
                    "td-icon-menu-right").click()
                WebDriverWait(browser, TIME_OUT).until(
                    EC.visibility_of_element_located((
                        By.CLASS_NAME, "td-icon-menu-right")))
            except Exception:
                print('load out')

    return (titles.tolist(), update_times.tolist())


def grabber_ccn(load_times, mode):
    print("=====grab news from ccn======", "====load page===", load_times)
    executable_path = os.path.abspath(os.path.join(os.getcwd(), "..")) + '/driver/chromedriver'
    html = "http://www.ccn.com"
    cur_time = int(time.time())
    recept_period = 12 * 60 * 60
    end_time = cur_time
    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path)
    browser.get(html)
    PAGE_OUT = 50

    if mode == 0:
        while load_times and PAGE_OUT:
            try:
                browser.find_element_by_class_name("omaha-CloseButton").click()
            except Exception as e:
                time.sleep(0.1)

            try:
                browser.find_element_by_class_name("load-more-btn").click()
                print("====load page====", load_times)
                load_times -= 1
                time.sleep(0.5)
            except Exception:
                PAGE_OUT -= 1

    if mode == 1:
        while cur_time - end_time < recept_period and PAGE_OUT:
            try:
                browser.find_element_by_class_name("omaha-CloseButton").click()
            except Exception:
                time.sleep(0.1)
            try:
                browser.find_element_by_class_name("load-more-btn").click()
                end_time = int(datetime.datetime.strptime(browser.find_elements_by_class_name("updated")[-1].text, '%Y-%m-%dT%H:%M:%S+00:00').timestamp() + 32400)
                print(end_time)
                time.sleep(0.1)
            except Exception:
                PAGE_OUT -= 1

    titles_element1 = browser.find_elements_by_xpath("//li/div[1]")
    titles_element2 = browser.find_elements_by_xpath("//article/header/h4[1]")
    titles = [x.text for x in titles_element1] + [x.text for x in titles_element2]
    update_time_elememt = browser.find_elements_by_class_name("updated")
    update_time = [x.text for x in update_time_elememt]

    return (titles, update_time)
