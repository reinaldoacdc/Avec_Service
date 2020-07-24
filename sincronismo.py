import json
from agenda import Agenda
from reserva import Reserva
from cliente import Cliente
from pontuacao import Pontuacao
from jornada import Jornada
import fdb
from datetime import date
from printlog import PrintLog

import requests
from configuracao import Configuracao

printlog = PrintLog()

class Sincronismo:

    def __init__(self, item):
        self.config = Configuracao()
        self.controle = item['CONTROLE']
        self.tabela = item['TABELA']
        self.acao = item['ACAO']
        self.pk1 = item['FIELD1']
        self.pk2 = item['FIELD2']
        self.pk3 = item['FIELD3']
        self.pk4 = item['FIELD4']

    def get_url(self):
        return {
            0: '/servico',
            1: '/profissional',
            2: '/profissional/' + '/servico',
            3: '/cliente',
            4: '/reserva',
            5: '/agenda',
            6: '/agenda',
            7: '/fidelidade'
        }[self.tabela]

    def get_acao(self):
        return {
            1: '/criar',
            2: '/atualizar',
            3: '/deletar'
        }[self.acao]

    def get_json(self):
        if self.tabela==3:
            return Cliente(self.pk1, self.pk2).parse_to_json()
        elif self.tabela==4:
            return Agenda(self.pk1).parse_to_json()
        elif self.tabela==5:
            return Reserva(self.pk1).parse_to_json()
        elif self.tabela == 6:
            return Jornada(self.pk1).parse_to_json()
        elif self.tabela==7:
            return Pontuacao(self.pk1, self.pk2).parse_to_json()

    def get_idweb(self):
        if self.tabela == 3:
            return Cliente(self.pk1, self.pk2).id_web
        elif self.tabela == 4:
            return Agenda(self.pk1).id_web
        elif self.tabela == 5:
            return Reserva(self.pk1).id_web
        elif self.tabela == 6:
            return 0


    def grava_id(self, id_web):
        if self.tabela==3:
            Cliente(self.pk1, self.pk2).grava_id(self.pk1, self.pk2, id_web)
        elif self.tabela==4:
             Agenda(self.pk1).grava_id(self.pk1, id_web)
        elif self.tabela==5:
             Reserva(self.pk1).grava_id(self.pk1, id_web)

    def valida_registro(self):
        if (self.tabela==4) or (self.tabela==5):
            r = Agenda.pesquida_agenda(self.pk1)
            if not(r) and (self.acao != 3):
                self.baixa_controle()
                return False
            elif (len(r) > 0) and (r[0]['DATA'] < date.today()):
                self.baixa_controle()
                return False
            else:
                return True
        elif (self.tabela ==3):
            self.baixa_controle()
        else:
            return True

    def atualiza_cliente(self, codigoEmpresa, codigoCliente, nomeCliente):
        printlog.Info('Sistema irá efetuar busca pelo nome do cliente no salao vip...')             
        retorno = False
        encontrados = []
        headers = {'authorization': self.config.app_token, 'content-type': 'application/json'}
        url = 'https://api.salaovip.com.br/salao/' + self.config.app_id + '/clientes'
        r  = requests.get(url, headers=headers, timeout=20)
        if r.json()['code'] == 200:
            ultima = r.json()['data']['salonClients']['last_page']
            i = 1
            while(i <= ultima):
                headers = {'authorization': self.config.app_token, 'content-type': 'application/json'}
                url = 'https://api.salaovip.com.br/salao/' + self.config.app_id + '/clientes?page='+str(i)
                r  = requests.get(url, headers=headers, timeout=20)
                lista = r.json()['data']['salonClients']['data']
                printlog.Info('Lendo pagina['+str(i)+']')
                i = i + 1
                for item in lista:
                    if item['nome'] == nomeCliente:
                        encontrados.append(item['id'])

        if len(encontrados) == 1:
            Cliente(codigoCliente, codigoEmpresa).grava_id(codigoCliente,codigoEmpresa, encontrados[0])
            printlog.Info('Sistema Identificou cliente com nome "'+nomeCliente+'" com id '+str(encontrados[0])+' e efetuou a troca!')
            retorno = True
        elif len(encontrados) > 1:
            printlog.Info('Sistema Identificou mais de um cliente com nome "'+nomeCliente+'"') 
        else :
            printlog.Info('Sistema Não Encontrou cliente com nome "'+nomeCliente+'"')              

        return retorno

    def valida_cliente(self, listaRepetida):
        retorno = []
        retorno.append(1)
        retorno.append('')
        if (self.tabela==4) and (self.acao==1):
            agd = Agenda(self.pk1)
            idCliente = agd.cliente_idweb
            headers = {'authorization': self.config.app_token, 'content-type': 'application/json'}
            url = 'https://api.salaovip.com.br/salao/' + self.config.app_id + '/cliente/'+str(idCliente)
            r  = requests.get(url, headers=headers, timeout=20)
            if r.json()['code'] == 404:
                printlog.Info('Cliente de Codigo "'+str(idCliente)+'" e Nome "'+ agd.nome_cliente.strip() +'" não existe para o salao id "'+self.config.app_id+'"!') 
                i = 0
                while(i != len(listaRepetida)):
                    if listaRepetida[i] == agd.codigo_cliente:
                        retorno[0] = 3
                        retorno[1] = agd.codigo_cliente
                        break

                if retorno[0] == 1:
                    if self.atualiza_cliente(self.config.emp_padrao, agd.codigo_cliente, agd.nome_cliente.strip()) == False:                    
                        retorno[0] = 2
                        retorno[1] = agd.codigo_cliente
           
        return retorno

    def sincronizar(self):
        headers = {'authorization': self.config.app_token, 'content-type': 'application/json'}

        if self.acao == 3:
            url = 'https://api.salaovip.com.br/salao/' + self.config.app_id + self.get_url() + '/' + self.pk2
            response_data  = requests.delete(url, headers=headers, timeout=20)
        else:
            id_web = self.get_idweb()
            if int(id_web or 0) > 0:
                url = 'https://api.salaovip.com.br/salao/' + self.config.app_id + self.get_url() + '/' + str(id_web)
                payload = self.get_json()
                printlog.Info('payload: ' + str(json.dumps(payload)))
                response_data  = requests.put(url, data = json.dumps(payload), headers=headers, timeout=20)
            else:
                url = 'https://api.salaovip.com.br/salao/' + self.config.app_id + self.get_url()
                payload = self.get_json()
                printlog.Info('payload: ' + str(json.dumps(payload)))
                response_data  = requests.post(url, data = json.dumps(payload), headers=headers, timeout=20)

        printlog.Info('response: ' + str(response_data.json()))
        data = response_data.json()
        if data['code'] == 200:
            self.baixa_controle()
            if (self.acao == 1) and (int(id_web or 0) == 0):
              self.grava_id(data['data']['id'])
        elif (data['code'] == 500) and (self.acao == 3):
            self.baixa_controle()
        elif (data['code'] == 404) and (self.acao == 3):
            self.baixa_controle()



    def baixa_controle(self):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password)
        cur = con.cursor()
        qry_sync=(" UPDATE SINCRONISMO_WEB SET STATUS = 'BAX' WHERE CONTROLE = {controle} ".format(controle=self.controle))
        cur.execute(qry_sync)
        con.commit()
        cur.close()
        con.close()

    def informacao(self):
        printlog.Info('[Tabela]'+self.get_url().replace('/','')+' [Ação]'+self.get_acao().replace('/',''))
