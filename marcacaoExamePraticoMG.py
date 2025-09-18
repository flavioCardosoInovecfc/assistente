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


class MarcacaoExamePratMG(Banco):

    def iniciar(self, cnpj, user, siteInoveCFC, verificaSSL, versaochrome):
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
        sleep(2)
        self.menu()
        sleep(.3)

        self.startEnvio()

        self.on_close()

        return True

    def startEnvio(self):
        situacoes = self.getExamesMG()
        for situacao in situacoes:
            
            qtdeAluno = situacao[0]
        
            self._send_command(self.qtdeAluno, 'type', qtdeAluno)
        
            self.browser.execute_script("atualizaAluno()")
            
            counteudo =  situacao[1].split('**')
            info = counteudo[0].split('|')
            
            placa = info[4]
            local = info[5]
            veiculo = info[7]

            self._send_command(self.placa, 'type', placa)     
            self.percorreSelectByOption(veiculo,False, self.veiculo)
            self.percorreSelectByOption(local,False, self.local)

            c = 0
            for row in counteudo:
                linha = row.split('|')
                cpf = linha[3]
                tipoexame = linha[1]
                c += 1
                self._send_command('//*[@id="cpf'+str(c)+'"]', 'type', cpf)    

                if tipoexame == "1.HABIL.":
                    radio_button = self.browser.find_element(By.XPATH,"//input[@name='tipoAluno"+str(c)+"' and @value='1']")
                else: 
                    radio_button = self.browser.find_element(By.XPATH,"//input[@name='tipoAluno"+str(c)+"' and @value='2']")

                radio_button.click()
        
            
            self._send_command(self.consultaCPF, 'click')
          
            try:
                elem = WebDriverWait(self.browser, .1).until(
                EC.element_to_be_clickable((By.XPATH, self.confirmaMarcacao)))
                elem.click()
                self.menu()
            except:
                self.menu()
                

           
            

            

    def menu(self):
        self.browser.switch_to.default_content()
        self._send_iframe(self.frame_menu)
        self._send_command(self.menuPV, 'click')
        self.browser.switch_to.default_content()
        self._send_iframe(self.frame_inclusao)
        self._send_command(self.inclusaoExame, 'click')

    def _send_iframe(self, obj):
        sleep(.1)
        self.browser.switch_to.frame(self.browser.find_element(By.XPATH,obj))

    def selecionaEmpresa(self, getValor, obj):


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


    def percorreSelectByOption(self, getValor, erro, obj):
        entrou = True
        if erro == False:
            sleep(.2)

        select_element = self.browser.find_element(By.XPATH,obj)
        select_object = Select(select_element)
        all_selected_options = select_object.options
        for linha in all_selected_options:
            if getValor in linha.get_attribute("value"):
                select_object.select_by_visible_text(linha.text)
                entrou = False
                break

        return entrou

    
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
        pyautogui.hotkey('tab', 'enter', interval=0.1)

    def loginExameMG(self):
        url = "https://empresas.detran.mg.gov.br/"
        self.browser.get(url)

        self._send_command(self.loginagendamnto, 'click')

    def on_open(self):

        # instala o plugin para onavegador
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
            self.browser.execute_script('window.localStorage.clear()')
            self.browser.execute_script('window.sessionStorage.clear()')
            self.browser.close()
            self.browser.quit()
            self.browser = None
            self.consultaSinc = False
            

    def _send_command(self, obj, command, value=""):
        erro = False
        self.tempoaguarde = 10
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
        sleep(.3)
        self.browser.switch_to.frame(self.browser.find_element(By.XPATH,obj))

    def coletor(self, msg="fim 1"):
        self.on_close()
        gc.collect()
        print(msg)
        sys.exit()

    def aguardar(self, obj):

        WebDriverWait(self.browser, 1).until(
            EC.presence_of_element_located(By.XPATH,obj))

    def percorreSelectByValue(self, getValor, erro, obj):
        entrou = True
        if erro == False:
            sleep(.2)

        try:
            select_element = self.browser.find_element(By.XPATH,obj)
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

    def retirarPontos(self, cnpj):
        cnpj = cnpj.replace(".", "")
        cnpj = cnpj.replace("/", "")
        cnpj = cnpj.replace("-", "")

        return cnpj

    def mapeamento(self):
        self.loginagendamnto = '/html/body/main/div/form/div/div/div/div[1]/div/div[2]/li[2]/a'
        self.pluguin = "/html/body/div[3]/div[2]/div/div/div[2]/div[2]/div/div/div/div"
        self.certificado = '/html/body/div[1]/div/div/div[1]/div[3]/div[3]/div/div[3]/div[2]/ul/li[2]/div/div[3]/button'   
        
        self.iframe_empresa = "/html/frameset/frameset/frame[2]"  
        self.selectEmpresa = "/html/body/form/div/table/tbody/tr/td/center/table[2]/tbody/tr[3]/td[2]/select"
        self.menuPV = '//*[@id="menu"]/tbody/tr[8]/td[2]/a'
        self.inclusaoExame = '/html/body/center[2]/table[3]/tbody/tr/td/li/a'
        self.frame_menu = '/html/frameset/frameset/frame[1]'
        self.frame_inclusao = '/html/frameset/frameset/frame[2]'

        self.qtdeAluno = "/html/body/form/center/table/tbody/tr[2]/td[2]/input"
        self.placa = "/html/body/form/center/table/tbody/tr[3]/td[2]/input"
        self.veiculo = "/html/body/form/center/table/tbody/tr[4]/td[2]/select"
        self.local = "/html/body/form/center/table[1]/tbody/tr[5]/td[2]/div/select"
        self.tipoExame = "/html/body/form/center/table[3]/tbody/tr[1]/td[2]/input[1]"
        self.informaCPF = "/html/body/form/center/table[3]/tbody/tr[2]/td/input"
        self.consultaCPF = "/html/body/form/center/input[1]"
        self.confirmaMarcacao = "/html/body/form/center/input[14]" 
        self.voltar = "/html/body/form/center/input[8]"

        self.jamarcado = "/html/body/form/center/center/font"

        self.candidato = "/html/body/form/center/table[3]/tbody/tr[1]/td[2]/input[1]"
        self.condutor = "/html/body/form/center/table[3]/tbody/tr[1]/td[2]/input[2]"


MarcacaoExamePratMG()
