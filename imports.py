import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from time import sleep
from datetime import datetime, timedelta
from selenium_stealth import stealth

import json
import random
import gc
import sys


class Acoes():

    def _send_command(self, obj, command, value="" , espera = 5):
            erro = False
            self.tempoaguarde = espera
            try:
                elem = WebDriverWait(self.browser, self.tempoaguarde).until(EC.element_to_be_clickable((By.XPATH, obj)))
                if command == 'click':
                    elem.click()
                elif command == 'type':
                    element = self.browser.find_element(By.XPATH,obj)
                    length = len(element.get_attribute('value'))
                    element.send_keys(length * Keys.BACKSPACE)
                    element.send_keys(value)

            except:
                erro = True

         
               
            
    def coletor(self, msg="fim 1"):
        self.on_close()
        gc.collect()
        print(msg)
        sys.exit()
    
    def on_close(self):
        if self.browser:
            self.browser.close()
            self.browser.quit()
            #self.browser = None
    
    def percorreSelectByOption(self, getValor, obj):
        entrou = True
        #sleep()

        select_element = self.browser.find_element(By.XPATH,obj)
        select_object = Select(select_element)
        all_selected_options = select_object.options
        for linha in all_selected_options:
            if getValor in linha.get_attribute("value"):
                select_object.select_by_visible_text(linha.text)
                entrou = False
                break

        return entrou