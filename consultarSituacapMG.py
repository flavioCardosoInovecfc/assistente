import requests
from selenium import webdriver
#from selenium.webdriver.chrome.service import Service as ChromeService
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
#from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime, timedelta


from selenium_stealth import stealth

import random
import gc
import sys
import pyautogui

from banco import * 


class ConsultarSituacaoMG(Banco):
        
    def iniciar(self,cnpj, user, siteInoveCFC,verificaSSL,versaochrome):
        
        self.versaochrome = versaochrome
        self.mapeamento()
        self.browser = None
        self.on_open()
    
        self.installPluguin()
        self.loginExameMG()
        self.chamaCertificado()

        self.cnpj = self.retirarPontos(cnpj)
        self.user = user
        self.verificaSSL = verificaSSL
        self.siteInoveCFC = siteInoveCFC
        sleep(3)
        self.selecionaEmpresa(self.cnpj, self.selectEmpresa)
        sleep(.3)
        self.menu()
        self.startConsulta()

        self.on_close()

        return True


    

    def menu(self):
        self.browser.switch_to.default_content()
        self._send_iframe(self.frame_menu)
        self._send_command(self.menuPV, 'click')
        self.browser.switch_to.default_content()
        self._send_iframe(self.frame_situacao_aluno)
        self._send_command(self.situacaoAluno, 'click')
        
         
    def startConsulta(self):
        situacoes = self.getConsultaSituacao()
        for situacao in situacoes:
            id_solicitacao = situacao[0]
            id_aluno = situacao[1]
            cpf = situacao[2]
            self._send_command(self.informeCPF, 'type', cpf)
            self._send_command(self.btnConsultar, 'click')

            caminho = '/html/body/center/form/table[1]/tbody/tr[6]/td[2]'
            table = self.browser.find_element(By.XPATH, caminho )
            tipoexame = table.text

            cont = 10
            
            for c in range(cont):
                try:  
                    num = 15 - c
                    caminho = '/html/body/center/form/table['+str(num)+']'
                    table = self.browser.find_element(By.XPATH, caminho )
                    texto = self.retirarPontos(table.text)
                    url = "https://"+self.siteInoveCFC+"/sistemas/python/detranmg/gravarBySituacao.php?user="+self.user+f"&id_solicitacao={id_solicitacao}&id_aluno={id_aluno}&observacao={texto}&tipoexame={tipoexame}"
                    r = requests.get(url, verify=self.verificaSSL) 
                    self._send_command(self.btnVoltar,'click')
                    self._send_command(self.situacaoAluno, 'click')
                    break
                except:
                    print("nada")


    def _send_iframe(self, obj):
        sleep(.3)
        self.browser.switch_to.frame(self.browser.find_element(*obj))

    def selecionaEmpresa(self, getValor, obj ):
        try:
            self._send_iframe(self.iframe_empresa)

            select_element = self.browser.find_element(By.XPATH,obj)
            select_object = Select(select_element)
            all_selected_options = select_object.options
            for linha in all_selected_options:
                if getValor in linha.get_attribute("value"):
                    select_object.select_by_visible_text(linha.text)
                    break
        except:
            sleep(.1)

    def chamaCertificado(self):
        try:
            self.browser.fullscreen_window()
            self.browser.execute_script("alternarTela()")
            self._send_command(self.certificado, 'click')
        except:
            self.coletor("erro de javascript no certificado")

    def installPluguin(self):
        
        self._send_command(self.pluguin, 'click')
        sleep(3)
        pyautogui.hotkey('tab','enter', interval=0.1)


    def loginExameMG(self):
        url = "https://empresas.detran.mg.gov.br/"
        self.browser.get(url)
       
        self._send_command(self.loginagendamnto, 'click')

    def on_open(self):
       
        #instala o plugin para onavegador 
        url = "https://chrome.google.com/webstore/detail/signa-prodemge/idbpfpeogbhifooiagnbbdbffplkfcke?hl=pt-BR"

        if not self.browser:
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument('--disable-gpu')
        

           
            #chromeOptions.add_argument("--kiosk")
            #chromeOptions.add_argument("--headless")
            #chromeOptions.add_argument('--no-sandbox')

            chromeOptions.add_experimental_option("excludeSwitches", ["enable-automation"])
            chromeOptions.add_experimental_option('useAutomationExtension', False)

            #chromeOptions.add_extension(f"chromedriver/extension_1_0_12_0.crx") isto aqui é para carregaar uma extensão
 
        
            self.browser  = webdriver.Chrome('chromedriver/chromedriver.exe', chrome_options=chromeOptions)
            

            stealth(self.browser,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
            )

           
            
            
        

            self.browser.get(url)
        
            

    def on_close(self):
        if self.browser:
            self.browser.close()
            self.browser.quit()
            self.browser = None
            
       
    
    def _send_command(self, obj, command, value=""):
        erro = False
        self.tempoaguarde = 60
        try:
    
                elem = WebDriverWait(self.browser, self.tempoaguarde).until(
            EC.element_to_be_clickable((By.XPATH, obj)))

        except:
            erro = True

        if erro == False:
            try:
                if command == 'click':
                   elem.click()
                elif command == 'type':
                    element = self.browser.find_element(By.XPATH,obj)
                    length = len(element.get_attribute('value'))
                    element.send_keys(length * Keys.BACKSPACE)
                    element.send_keys(value)
            except:
                self.coletor("Erro _send_command")

    def _send_iframe(self, obj):
        sleep(1)
        self.browser.switch_to.frame(self.browser.find_element(By.XPATH,obj))

    def coletor(self, msg="fim 1"):
        self.on_close()
        gc.collect()
        print(msg)
        sys.exit()

    def aguardar(self, obj):
        
           WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(obj))
          
       

    

    def percorreSelectByValue(self, getValor, erro, obj):
        entrou = True
        if erro == False:
            sleep(.2)

        try:
            select_element = self.browser.find_element(*obj)
            select_object = Select(select_element)
            all_selected_options = select_object.options
            for linha in all_selected_options:
                if getValor in linha.text:
                    select_object.select_by_visible_text(linha.text)
                    entrou = False
                    break

            return entrou
        except:
            return entrou

    def retirarPontos(self,cnpj):
        cnpj = cnpj.replace(".", "")
        cnpj = cnpj.replace("/", "")
        cnpj = cnpj.replace("-", "")
        cnpj = cnpj.replace("'", "")
        cnpj = cnpj.replace("\n", "")
        cnpj = cnpj.rstrip()

        return cnpj

    def mapeamento(self):
        self.loginagendamnto = '/html/body/main/div/form/div/div/div/div[1]/div/div[2]/li[2]/a'
        self.pluguin = "/html/body/div[3]/div[2]/div/div/div[2]/div[2]/div/div/div/div"
        self.certificado = '/html/body/div[1]/div/div/div[1]/div[3]/div[3]/div/div[3]/div[2]/ul/li[2]/div/div[3]/button'    

        self.iframe_empresa=  '/html/frameset/frameset/frame[2]' 
        self.selectEmpresa = '/html/body/form/div/table/tbody/tr/td/center/table[2]/tbody/tr[3]/td[2]/select'
        self.menuPV = '//*[@id="menu"]/tbody/tr[4]/td[2]/a'  
        self.situacaoAluno = '/html/body/center[3]/table/tbody/tr[1]/td/li/a' 
        self.frame_menu = '/html/frameset/frameset/frame[1]'
        self.frame_situacao_aluno = '/html/frameset/frameset/frame[2]'
        
        self.informeCPF = '/html/body/center/form/table/tbody/tr/td[2]/input'
        self.btnConsultar = '/html/body/center/form/input[1]'
        self.getObservacao = ''
        self.btnVoltar= '/html/body/center/form/input[2]'
   
     


ConsultarSituacaoMG()