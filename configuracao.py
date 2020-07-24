import configparser
from printlog import PrintLog
import os
import sys

printlog = PrintLog()

class Configuracao:

    def __init__(self):

        self.RetornoOk = True
        config = configparser.ConfigParser()
        
        if (os.path.exists('avec_app.ini')):
            config.read('avec_app.ini')
        else:
            printlog.Info('Não encontrado arquivo "avec_app.ini"')
            self.RetornoOk = False

        if (self.RetornoOk):
            try:
                config.read('avec_app.ini')
            except Exception: 
                try:
                    s = open('avec_app.ini', mode='r', encoding='utf-8').read()
                    if (s[0:1] == '\ufeff'):
                        open('avec_app.ini', mode='w', encoding='utf-8').write(s[1:len(s)])
                except Exception: 
                    pass

            try:
                config.read('avec_app.ini')
            except Exception: 
                printlog.Info('Não foi possivel abrir o arquivo "avec_app.ini"')
                self.RetornoOk = False

        if (self.RetornoOk):
            try:
                self.db_user = config['Banco']['user']
                self.db_password = config['Banco']['password']
                self.db_path = config['Banco']['path']
                self.db_lib = config['Banco']['lib']
                self.db_host = config['Servidor']['server']
                self.app_id = config['App']['id']
                self.app_token = config['App']['token']
                self.emp_padrao = config['App']['emp_padrao']

                self.email_user = config['Email']['user']
                self.email_password = config['Email']['password']
                self.email_to = config['Email']['to']

                self.app_nome = config['App']['nome']
                self.app_acesso = config['App']['acesso']
                self.app_telefone = config['App']['telefone']
            except Exception as e:
                printlog.Info('Não foi possivel carregar os campos do arquivo "avec_app.ini"')
                printlog.Info(e)
                self.RetornoOk = False

    def AllOk(self):
        return self.RetornoOk
