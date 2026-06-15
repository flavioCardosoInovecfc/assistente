import json
import os
import random
from playwright.sync_api import sync_playwright, expect, TimeoutError, Page
import time
import base64
import requests
from pathlib import Path

class TaxaMG():

    def __init__(self):
        self.user_inove = None
        self.verificaSSL = True
        self.codigoTaxa = ''
        self.codigo_municipio = ''
        self.id_aluno = ''
        self.categoria_pretendida = ''
        self.dados = {}
        self.pagina: Page = None
        self.tempo = 0

        self.mapeamento()

    def baixar_pdf(self, url_pdf: str, nome_arquivo: str):
        """
        Baixa um arquivo PDF de uma URL e salva em disco.
        """
        try:
            cookies = {}
            if self.pagina and self.pagina.context:
                for cookie in self.pagina.context.cookies():
                    cookies[cookie["name"]] = cookie["value"]

            print(f"Tentando baixar PDF de: {url_pdf}")
            resp = requests.get(url_pdf, cookies=cookies, verify=self.verificaSSL, timeout=30)
            resp.raise_for_status()

            pasta = Path("dae_pdfs")
            pasta.mkdir(exist_ok=True)
            caminho = pasta / nome_arquivo

            with open(caminho, "wb") as f:
                f.write(resp.content)

            print(f"PDF salvo com sucesso em: {caminho}")
            return caminho
        except requests.exceptions.RequestException as e:
            print(f"Erro ao baixar PDF da URL {url_pdf}: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao salvar PDF: {e}")
            return None

    def _capturar_e_baixar_dae(self):
        """
        Depois de clicar em 'Pagar', captura a nova aba/janela do DAE e
        tenta baixar o PDF. Se não conseguir, não fica travado.
        """
        print("Esperando botão 'Forma de pagamento DAE'...")
        botao_dae_locator = self.pagina.locator(self.xpath_botao_forma_pagamento_dae)
        expect(botao_dae_locator).to_be_visible(timeout=8000)

        dae_page = None
        try:
            print("Clicando e aguardando nova página do DAE (timeout 12s)...")
            with self.pagina.context.expect_page(timeout=12000) as new_page_info:
                botao_dae_locator.click()

            dae_page = new_page_info.value
            print(f"Nova página capturada: {dae_page.url}")

            try:
                dae_page.wait_for_load_state("domcontentloaded", timeout=5000)
            except TimeoutError:
                print("Timeout no loadstate (provavelmente tela branca), seguindo mesmo assim.")

            # 1) URL já é PDF?
            if "application/pdf" in dae_page.url or ".pdf" in dae_page.url.lower():
                print("Página do DAE é um PDF direto.")
                self.baixar_pdf(dae_page.url, f"dae_{self.id_aluno}_{self.codigoTaxa}.pdf")
                return

            # 2) Tenta achar iframe/embed com PDF
            time.sleep(2)
            pdf_frame = dae_page.locator('iframe[src*=".pdf"], embed[src*=".pdf"]')

            if pdf_frame.count() > 0:
                pdf_url = pdf_frame.first.get_attribute("src")
                if pdf_url:
                    print(f"PDF encontrado em iframe/embed: {pdf_url}")
                    self.baixar_pdf(pdf_url, f"dae_{self.id_aluno}_{self.codigoTaxa}.pdf")
                else:
                    print("Iframe/embed encontrado, mas sem src.")
            else:
                conteudo = dae_page.content()[:500].lower()
                if "oops" in conteudo and "erro ao acessar a página" in conteudo:
                    print("Site retornou tela de erro 'Oops!'. Encerrando sem tentar mais.")
                else:
                    print("Nenhum PDF encontrado; possivelmente tela branca.")

                dae_page.screenshot(
                    path=f"dae_page_{self.id_aluno}_{self.codigoTaxa}.png",
                    full_page=True
                )

        except TimeoutError:
            print("Timeout: nova página do DAE não abriu em 12s.")
        except Exception as e:
            print(f"Erro ao processar DAE: {e}")
        finally:
            if dae_page:
                try:
                    dae_page.close()
                except Exception:
                    pass
                print("Página do DAE fechada.")

    def iniciar(self, informacao: dict, verificaSSL: bool = True):
        self.user_inove = informacao.get('user_inove')
        self.verificaSSL = verificaSSL

        try:
            self.ajustarParms(informacao)
            self.on_open()
        except Exception as e:
            print(f"Erro crítico na inicialização: {e}")
            raise

    def ajustarParms(self, informacao: dict):
        convertsample = informacao.get('geral')
        if not convertsample:
            raise ValueError("Parâmetro 'geral' (base64) não encontrado na informação.")

        try:
            convertbytes = convertsample.encode("ascii")
            convertedbytes = base64.b64decode(convertbytes)
            decodedsample = convertedbytes.decode("ascii").split("&")
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            raise ValueError(f"Erro ao decodificar base64 ou ASCII: {e}")

        for item in decodedsample:
            temp = item.split("=")
            if len(temp) == 2:
                key, value = temp[0], temp[1]
                if key == 'codigoTaxa':
                    self.codigoTaxa = value
                elif key == 'codigo_municipio' or key == 'codigo-municipio':
                    self.codigo_municipio = value
                elif key == 'id_aluno':
                    self.id_aluno = value
                elif key == 'categoria_pretendida':
                    self.categoria_pretendida = value

        if not all([self.user_inove, self.id_aluno, self.codigoTaxa]):
            raise ValueError("Parâmetros essenciais (user_inove, id_aluno, codigoTaxa) não foram extraídos ou estão faltando.")

        try:
            request_url = (f"https://www.inovecfc.com/sistemas/python/detranmg/getAluno.php?"
                           f"user={self.user_inove}&id_aluno={self.id_aluno}&codigo={self.codigoTaxa}")
            
            request = requests.get(request_url, verify=self.verificaSSL, timeout=10)
            request.raise_for_status()
            self.dados = json.loads(request.content)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Erro na requisição para inovecfc.com: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON da resposta de inovecfc.com: {e}")

    def openServico(self):
        if self.codigoTaxa == '15':
            self.tempo = 30
            self.inscricaoprimeirahabiltacao()
        elif self.codigoTaxa == '16':
            self.tempo = 30
            self.adicaocategoria()
        elif self.codigoTaxa == '17':
            self.tempo = 30
            self.mudancacategoria()
        elif self.codigoTaxa == '18':
            self.tempo = 20
            self.examelegislacaorepetencia()
        elif self.codigoTaxa == '19':
            self.tempo = 30
            self.examedirecaorepetencia()
        elif self.codigoTaxa == '23':
            self.tempo = 20
            self.expedicaolicendaaprendizagem()
        elif self.codigoTaxa == '34':
            self.tempo = 20
            self.registroouimportacaoprontuario()
        elif self.codigoTaxa == '27':
            self.tempo = 30
            self.cnhDefenitiva()

    def registroouimportacaoprontuario(self):
        print("Executando registroouimportacaoprontuario.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/34",
            wait_until="domcontentloaded",
            timeout=30000
        )

        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def examedirecaorepetencia(self):
        print("Executando examedirecaorepetencia.")
        self.pagina.goto(
            "https://detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/19",
            wait_until="domcontentloaded",
            timeout=30000
        )

        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def expedicaolicendaaprendizagem(self):
        print("Executando expedicaolicendaaprendizagem.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/23",
            wait_until="domcontentloaded",
            timeout=30000
        )

        time.sleep(.1)
        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form_alt)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form_alt).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def cnhDefenitiva(self):
        print("Executando cnhDefenitiva.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/27",
            wait_until="domcontentloaded",
            timeout=30000
        )

        time.sleep(.1)
        expect(self.pagina.locator(self.xpath_cpf_cnh_definitiva)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_cpf_cnh_definitiva, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_nome_condutor_cnh_definitiva, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form_cnh_definitiva)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form_cnh_definitiva).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def examelegislacaorepetencia(self):
        print("Executando examelegislacaorepetencia.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/18",
            wait_until="domcontentloaded",
            timeout=30000
        )

        time.sleep(.1)
        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form_alt_btn1)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form_alt_btn1).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def adicaocategoria(self):
        print("Executando adicaocategoria.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/16",
            wait_until="domcontentloaded",
            timeout=30000
        )

        time.sleep(.1)
        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form_alt_btn1)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form_alt_btn1).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def mudancacategoria(self):
        print("Executando mudancacategoria.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/17",
            wait_until="domcontentloaded",
            timeout=30000
        )

        time.sleep(.1)
        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form_alt_btn1)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form_alt_btn1).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def inscricaoprimeirahabiltacao(self):
        print("Executando inscricaoprimeirahabiltacao.")
        self.pagina.goto(
            "https://www.detran.mg.gov.br/habilitacao/taxas-1/emitir-taxa-de-servico-de-habilitacao/preencher-dados-da-habilitacao/15",
            wait_until="domcontentloaded",
            timeout=30000
        )

        time.sleep(.1)
        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.dados.get('nome_aluno', ''))
        self.pagina.fill(self.xpath_cpf_contribuinte, self.dados.get('cpf', ''))
        self.pagina.fill(self.xpath_data_nascimento, self.dados.get('dt_nascimento', ''))

        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)

        time.sleep(2)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form).click()

        time.sleep(2)
        self._capturar_e_baixar_dae()

    def microfilmagem(self):
        print("Executando microfilmagem.")
        expect(self.pagina.locator(self.xpath_nome_contribuinte)).to_be_visible(timeout=10000)
        self.pagina.fill(self.xpath_nome_contribuinte, self.nome_contribuinte)
        self.pagina.fill(self.xpath_cpf_contribuinte, self.cpf_cnpj_contribuinte)
        time.sleep(2)
        self.gerarDae()

    def gerarDae(self):
        print("Executando gerarDae.")
        expect(self.pagina.locator(self.xpath_codigo_municipio_select)).to_be_enabled(timeout=10000)
        self.pagina.locator(self.xpath_codigo_municipio_select).select_option(self.codigo_municipio)
        expect(self.pagina.locator(self.xpath_botao_prosseguir_form)).to_be_visible(timeout=10000)
        self.pagina.locator(self.xpath_botao_prosseguir_form).click()
        time.sleep(2)
        self._capturar_e_baixar_dae()

    def atalhoTaxas(self):
        print("Executando atalhoTaxas.")
        expect(self.pagina.locator(self.menuTaxa)).to_be_visible(timeout=10000)
        self.pagina.locator(self.menuTaxa).click()
        expect(self.pagina.locator(self.emissaoTaxa)).to_be_visible(timeout=10000)
        self.pagina.locator(self.emissaoTaxa).click()

    def logarDetran(self):
        print("Executando logarDetran.")
        expect(self.pagina.locator(self.logindetran)).to_be_visible(timeout=10000)
        self.pagina.locator(self.logindetran).click()
        expect(self.pagina.locator(self.certificadoDigital)).to_be_visible(timeout=10000)
        self.pagina.locator(self.certificadoDigital).click()

    def on_open(self):
        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(
                    channel="chrome",
                    headless=False,
                    args=["--start-maximized", "--disable-gpu", "--disable-infobars", "--lang=pt-BR"]
                )

                context = browser.new_context()
                self.pagina = context.new_page()

                self.pagina.goto(
                    "https://transito.mg.gov.br/habilitacao",
                    wait_until="domcontentloaded",
                    timeout=30000
                )
                time.sleep(2)
                self.openServico()

                if getattr(self, "tempo", None):
                    time.sleep(self.tempo)

            except Exception as e:
                print(f"Erro ao abrir navegador ou executar serviço: {e}")
                if getattr(self, "pagina", None):
                    try:
                        self.pagina.screenshot(path="erro_on_open.png", full_page=True)
                    except Exception:
                        pass
                raise
            finally:
                if browser is not None:
                    browser.close()

    def mapeamento(self):
        self.url = "https://www.detran.mg.gov.br/habilitacao"

        # XPaths comuns
        self.xpath_nome_contribuinte = 'xpath=//*[@id="nome-contribuinte"]'
        self.xpath_cpf_contribuinte = 'xpath=//*[@id="cpf-cnpj-contribuinte"]'
        self.xpath_data_nascimento = 'xpath=//*[@id="data-nascimento"]'
        self.xpath_codigo_municipio_select = 'xpath=//*[@id="codigo-municipio"]'
        self.xpath_botao_prosseguir_form = 'xpath=//*[@id="content"]/form/button'
        self.xpath_botao_prosseguir_form_alt = 'xpath=//*[@id="content"]/form/button'
        self.xpath_botao_prosseguir_form_alt_btn1 = 'xpath=//*[@id="content"]/form/button[1]'
        self.xpath_botao_forma_pagamento_dae = 'xpath=//*[@id="btn-forma-pagamento-dae"]'

        # XPaths específicos para CNH Definitiva
        self.xpath_cpf_cnh_definitiva = 'xpath=//*[@id="cpf"]'
        self.xpath_nome_condutor_cnh_definitiva = 'xpath=//*[@id="nome-condutor"]'
        self.xpath_botao_prosseguir_form_cnh_definitiva = 'xpath=//*[@id="content"]/form/button'

        # Outros XPaths
        self.logindetran = 'xpath=/html/body/header/div/div[1]/div/div/div[2]/ul/li/a'
        self.certificadoDigital = 'xpath=//*[@id="cert-digital"]/button'
        self.menuTaxa = 'xpath=//*[@id="nav"]/ul/li[4]/a'
        self.emissaoTaxa = 'xpath=/html/body/main/div/div[1]/div[2]/div/div[2]/div/div[6]/ul/li[1]/a/span'
        self.INSCRICAOPARAPRIMEIRAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[1]/td[2]/a'
        self.MUDANCADECATEGORIA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[3]/td[2]/a'
        self.EXAMELEGISLREPETPRIMEIRAHABILITACAO = 'xpath=/html/body/main/div/div/div[1]/div/div/div[4]/div/table/tbody[2]/tr[4]/td[5]/a'
        self.EXAMEPPORTADORESDEDEFFISICA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[6]/td[2]/a'
        self.OPENCNHDEFENITIVA = 'xpath=/html/body/main/div/div[1]/div[2]/div/div[2]/div/div[3]/ul/li[2]/a/span'
        self.EXPEDICAODA2aVIADAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[8]/td[2]/a'
        self.ALTERACAODEDADOSDAHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[9]/td[2]/a'
        self.EXPEDICAODACARTEIRADEFINITIVA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[10]/td[2]/a'
        self.RENOVACAODODOCUMENTODEHABILITACAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[11]/td[2]/a'
        self.USOINTERNODODETRANAVALPSICOLOGICA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[12]/td[2]/a'
        self.USOINTERNODODETRANEXAMEMEDICO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[13]/td[2]/a'
        self.EXPEDICAODASEGUNDAVIADOEXAMEMEDICO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[14]/td[2]/a'
        self.REGISTRODEPRONTUARIODEESTRANGEIRO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[15]/td[2]/a'
        self.REGISTROIMPDEPRONTDAPERMISSAO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[17]/td[2]/a'
        self.EXPEDICAODECERTIDAOOUPRINTHABILITAC = 'xpath=//*[@id="content"]/table/tbody[2]/tr[18]/td[2]/a'
        self.COPIAMICROFILMAGEM = 'xpath=//*[@id="content"]/table/tbody[2]/tr[19]/td[2]/a'
        self.CREDENCIAMENTOOUREVALIDACAODECLINICA = 'xpath=//*[@id="content"]/table/tbody[2]/tr[20]/td[2]/a'
        self.EXAMELEGISLACAORENOVACAORECICLDACNH = 'xpath=//*[@id="content"]/table/tbody[2]/tr[21]/td[2]/a'
        self.PERMISSAOINTERNACIONALPARADIRIGIR = 'xpath=//*[@id="content"]/table/tbody[2]/tr[22]/td[2]/a'
        self.REGIMPORTACAODEPRONTUARIOCANDIDATO = 'xpath=//*[@id="content"]/table/tbody[2]/tr[23]/td[2]/a'
        self.CREDENCIAMENTOREVALANUALDESPACHANTE = 'xpath=//*[@id="content"]/table/tbody[2]/tr[24]/td[2]/a'
        self.a2VIADOCERTIFICADODIRETORINSTRUTOR = 'xpath=//*[@id="content"]/table/tbody[2]/tr[25]/td[2]/a'
        self.RELATORIOSEESTATISTICASITEM59TABD = 'xpath=//*[@id="content"]/table/tbody[2]/tr[26]/td[2]/a'

        # Parâmetros de compatibilidade
        self.nome_contribuinte = ''
        self.cpf_cnpj_contribuinte = ''
        self.documento_identificacao = ''
        self.uf_orgao_identificacao = ''
        self.uf_orgao_expedidor_identificacao = ''


# if __name__ == "__main__":
#     informacao_exemplo = {
#         'user_inove': 'seu_usuario_inove',  # Substitua pelo seu usuário real
#         'verificaSSL': True,
#         'geral': 'Y29kaWdvVGF4YT0xOCZjb2RpZ29fbXVuaWNpcGlvPTMxMjMyMDkmY2F0ZWdvcmlhX3ByZXRlbmRpZGE9QSZpZF9hbHVubz0xMjM0NQ=='
#     }

#     try:
#         taxa = TaxaMG()
#         taxa.iniciar(informacao_exemplo, True)
#         print("Processo concluído. Verifique a pasta 'dae_pdfs' para o arquivo.")
#     except Exception as e:
#         print(f"Falha geral na execução: {e}")