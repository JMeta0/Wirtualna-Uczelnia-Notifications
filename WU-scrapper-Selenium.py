# coding: utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumrequests import Firefox
from pyvirtualdisplay import Display
import re
import time
from shutil import copyfile
import os
from bs4 import BeautifulSoup
import requests
import filecmp

#zmienne
wu_login = 'LOGIN'
wu_password = 'PASSWORD'
discord_webhook = 'https://WEBHOOK.LINK'
main_directory = '/main/directory/'
old_files_folder = os.path.join(main_directory, 'temp/')

wiadomosci_index = os.path.join(main_directory, 'index.html')
all_wiadomosci_file = os.path.join(main_directory, 'allWiadomosci.html')
all_ogloszenia_file = os.path.join(main_directory, 'allOgloszenia.html')
plan_file = os.path.join(main_directory, 'plan.html')
oceny_file = os.path.join(main_directory, 'oceny.html')

all_wiadomosci_old_file = os.path.join(old_files_folder, 'oldWiadomosci.html')
all_ogloszenia_old_file = os.path.join(old_files_folder, 'oldOgloszenia.html')
plan_old_file = os.path.join(old_files_folder, 'oldPlan.html')
plan_before_change = os.path.join(old_files_folder, 'oldPlan_beforeChange.html')
oceny_old_file = os.path.join(old_files_folder, 'oldOceny.html')

error_wiadomosci = os.path.join(old_files_folder, 'errorWiadomosci.html')
error_ogloszenia = os.path.join(old_files_folder, 'errorOgloszenia.html')

#START
display = Display(visible=0, size=(1024, 768))
display.start()
cap = DesiredCapabilities.FIREFOX.copy()
cap["marionette"] = True
driver = webdriver.Firefox(capabilities=cap)

driver.get("https://wu.akademia.mil.pl/Logowanie2.aspx")

login = driver.find_element_by_name("ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$txtIdent")
login.clear()
login.send_keys(wu_login)

haslo = driver.find_element_by_name("ctl00$ctl00$ContentPlaceHolder$MiddleContentPlaceHolder$txtHaslo")
haslo.clear()
haslo.send_keys(wu_password)

submit_login = driver.find_element_by_xpath(
    "//*[@id='ctl00_ctl00_ContentPlaceHolder_MiddleContentPlaceHolder_butLoguj']")
submit_login.click()

driver.get("https://wu.akademia.mil.pl/OgloszeniaFrame.aspx?typ=0")
wiadomosci = BeautifulSoup(driver.page_source, 'lxml')
if driver.find_element_by_xpath("//*[@id='btnShowAll']"):
    enlargeButton = driver.find_element_by_xpath("//*[@id='btnShowAll']")
    enlargeButton.click()
    allWiadomosci = BeautifulSoup(driver.page_source, 'lxml')
driver.get("https://wu.akademia.mil.pl/OgloszeniaFrame.aspx?typ=1")
ogloszenia = BeautifulSoup(driver.page_source, 'lxml')
if driver.find_element_by_xpath("//*[@id='btnShowAll']"):
    enlargeButton = driver.find_element_by_xpath("//*[@id='btnShowAll']")
    enlargeButton.click()
    allOgloszenia = BeautifulSoup(driver.page_source, 'lxml')

if driver.find_element_by_xpath("//*[@id='btnShowAll']"):
    if not os.path.exists(main_directory):
        os.makedirs(main_directory)
    with open(wiadomosci_index, "w+") as text_file:
        ogloszenia = re.sub('<input.*type="hidden".*?/>', "", str(ogloszenia))
        wiadomosci = re.sub('<input.*type="hidden".*?/>', "", str(wiadomosci))
        allOgloszenia = re.sub('<input.*type="hidden".*?/>', "", str(allOgloszenia.prettify()))
        allWiadomosci = re.sub('<input.*type="hidden".*?/>', "", str(allWiadomosci.prettify()))

        ogloszenia = re.sub('Jolanta ......|Monika .............', " [Classified]", ogloszenia)
        wiadomosci = re.sub(
            '[0-9][0-9][0-9]&nbsp;|&nbsp;[0-9][0-9][0-9]|[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]',
            " [Classified]", wiadomosci)

        text_file.write("Scraping done on " + time.strftime('%c') + "\n<br>" + str(
            ogloszenia.replace('none', 'block;')) + "<br>" + str(
            wiadomosci.replace('none', 'block;')))
    with open(all_ogloszenia_file, "w+") as text_file:
        text_file.write(allOgloszenia)
    with open(all_wiadomosci_file, "w+") as text_file:
        text_file.write(allWiadomosci)

    rozmiar_wiadomosci = os.path.getsize(all_wiadomosci_file)
    rozmiar_ogloszen = os.path.getsize(all_ogloszenia_file)

    if not os.path.exists(old_files_folder):
        os.makedirs(old_files_folder)

    old_wiadomosci_check = os.path.isfile(all_wiadomosci_old_file)
    if not old_wiadomosci_check:
        open(all_wiadomosci_old_file, 'w').close()
    old_ogloszenia_check = os.path.isfile(all_ogloszenia_old_file)
    if not old_ogloszenia_check:
        open(all_ogloszenia_old_file, 'w').close()

    rozmiar_starych_ogloszen = os.path.getsize(all_ogloszenia_old_file)
    rozmiar_starych_wiadomosci = os.path.getsize(all_wiadomosci_old_file)

    if rozmiar_starych_wiadomosci < rozmiar_wiadomosci:
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"avatar_url": "https://wu.akademia.mil.pl/Templates/AON/images/aszwoj.png", "content": "@here Nowa wiadomość na Wirtualnej uczelni.\\n[https://isb.ovh/wiadomosci](https://isb.ovh/wiadomosci)\\n[https://wu.akademia.mil.pl/Ogloszenia.aspx](https://wu.akademia.mil.pl/Ogloszenia.aspx)"}'
        response = requests.post(
            discord_webhook,
            headers=headers, data=data.encode('utf-8'))
        copyfile(all_wiadomosci_file, all_wiadomosci_old_file)
    if rozmiar_starych_ogloszen < rozmiar_ogloszen:
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"avatar_url": "https://wu.akademia.mil.pl/Templates/AON/images/aszwoj.png", "content": "@here Nowe ogłoszenie na Wirtualnej uczelni.\\n[https://isb.ovh/wiadomosci](https://isb.ovh/wiadomosci)\\n[https://wu.akademia.mil.pl/Ogloszenia.aspx](https://wu.akademia.mil.pl/Ogloszenia.aspx)"}'
        response = requests.post(
            discord_webhook,
            headers=headers, data=data.encode('utf-8'))
        copyfile(all_ogloszenia_file, all_ogloszenia_old_file)

    if rozmiar_wiadomosci < rozmiar_starych_wiadomosci and rozmiar_starych_wiadomosci - rozmiar_wiadomosci > 50:
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"avatar_url": "https://wu.akademia.mil.pl/Templates/AON/images/aszwoj.png", "content": "<@147245006212562946> Exception Error, domniemany reset wiadomości"}'
        response = requests.post(
            discord_webhook,
            headers=headers, data=data.encode('utf-8'))
        copyfile(all_wiadomosci_file, error_wiadomosci)
        copyfile(all_wiadomosci_file, all_wiadomosci_old_file)
    if rozmiar_ogloszen < rozmiar_starych_ogloszen and rozmiar_starych_ogloszen - rozmiar_ogloszen > 50:
        headers = {
            'Content-Type': 'application/json',
        }
        data = '{"avatar_url": "https://wu.akademia.mil.pl/Templates/AON/images/aszwoj.png", "content": "<@147245006212562946> Exception Error, domniemany reset ogłoszeń"}'
        response = requests.post(
            discord_webhook,
            headers=headers, data=data.encode('utf-8'))
        copyfile(all_ogloszenia_file, error_ogloszenia)
        copyfile(all_ogloszenia_file, all_ogloszenia_old_file)

    driver.get('https://wu.akademia.mil.pl/PodzGodzin.aspx')
    if driver.find_element_by_xpath('//*[@id="ctl00_ctl00_ContentPlaceHolder_wumasterWhoIsLoggedIn"]'):
        semestralny = driver.find_element_by_id('ctl00_ctl00_ContentPlaceHolder_RightContentPlaceHolder_rbJak_2')
        semestralny.click()

        planRaw = driver.find_element_by_xpath(
            '//*[@id="ctl00_ctl00_ContentPlaceHolder_RightContentPlaceHolder_dgDane"]').text
        plan = BeautifulSoup(planRaw, 'lxml')

        with open(plan_file, "wb+") as text_file:
            text_file.write(plan.encode('cp1252'))

        old_plan_check = os.path.isfile(plan_old_file)
        if not old_plan_check:
            open(plan_old_file, 'w').close()

        if not filecmp.cmp(plan_file, plan_old_file):
            headers = {
                'Content-Type': 'application/json',
            }
            data = '{"avatar_url": "https://wu.akademia.mil.pl/Templates/AON/images/aszwoj.png", "content": "@here Wykryto zmianę w planie zajęć.\\n[https://wu.akademia.mil.pl/PodzGodzin.aspx](https://wu.akademia.mil.pl/PodzGodzin.aspx)"}'
            response = requests.post(
                discord_webhook,
                headers=headers, data=data.encode('utf-8'))
            copyfile(plan_old_file, plan_before_change)
            copyfile(plan_file, plan_old_file)

    driver.get('https://wu.akademia.mil.pl/OcenyP.aspx')
    if driver.find_element_by_xpath('//*[@id="ctl00_ctl00_ContentPlaceHolder_wumasterWhoIsLoggedIn"]'):

        old_oceny_check = os.path.isfile(oceny_old_file)
        if not old_oceny_check:
            open(oceny_old_file, 'w').close()

        oceny_raw = driver.find_element_by_xpath('//*[@id="ctl00_ctl00_ContentPlaceHolder_RightContentPlaceHolder_dgDane"]').text
        oceny = BeautifulSoup(oceny_raw, 'lxml')

        with open(oceny_file, "wb+") as text_file:
            text_file.write(oceny.encode('cp1252'))

        if not filecmp.cmp(oceny_file, oceny_old_file):
            headers = {
                'Content-Type': 'application/json',
            }
            data = '{"avatar_url": "https://wu.akademia.mil.pl/Templates/AON/images/aszwoj.png", "content": "@here Wykryto zmianę w ocenach.\\n[https://wu.akademia.mil.pl/OcenyP.aspx](https://wu.akademia.mil.pl/OcenyP.aspx)"}'
            response = requests.post(
                discord_webhook,
                headers=headers, data=data.encode('utf-8'))
            copyfile(oceny_file, oceny_old_file)

driver.quit()
display.stop()
os.remove("./geckodriver.log")
