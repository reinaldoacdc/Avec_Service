from configuracao import Configuracao
import requests
import json
import fdb


class PushNotification:

    def __init__(self, item):
        self.controle = item['CONTROLE']
        self.codigo_profissional = item['CODIGO_PROFISSIONAL']
        self.emp_profissional = item['EMP_PROFISSIONAL']
        self.tipo = item['TIPO']
        self.mensagem = item['MENSAGEM']
        self.hash = item['HASH']

    def get_title(self):
        tipo = int(self.tipo)
        if tipo==1:
            return 'Novo agendamento'
        elif tipo==2:
            return 'Agendamento Alterado'
        elif tipo==3:
            return 'Agendamento Exluido'
        elif tipo==4:
            return 'Abertura de Comanda'

    def parse_to_json(self):
        return {
            'notification': {
                'title': self.get_title(),
                'body': self.mensagem
            },
            'to': self.hash
        }

    def set_finalizado(self):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("UPDATE PUSH SET ENVIADO = 'S' WHERE CONTROLE = {controle}".format(controle=self.controle))
        cur.execute(qry_sync)
        con.commit()
        cur.close()
        con.close()

    def delete_dispositivo(self):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("DELETE FROM DISPOSITIVOS WHERE HASH = '{hash}'".format(hash=self.hash))
        cur.execute(qry_sync)
        con.commit()
        cur.close()
        con.close()

    def send_push(self):
        token = 'AAAA9v64w7E:APA91bHTWw-8_7Px_d04eHQ_U-zWh1Z7Eo79j3YM2eJmzk0FklxAtNXruHU9kdRs2slrX3ypBTWi0NZrl6A_7kyM5L_hjLmbmPSv3uE9yekk_htsBr-VoZMc6vv7f3i61twvsGm18DSy'
        url = 'http://fcm.googleapis.com/fcm/send'
        headers = {'authorization': 'key={token}'.format(token=token), 'Content-type': 'application/json'}
        data = self.parse_to_json()
        r = requests.post(url, json.dumps(data) , headers=headers, timeout=20)
        data = r.json()
        print(data)
        if data['failure'] == 1:
            if (data['results'][0]['error'] == 'NotRegistered'):
                self.delete_dispositivo()
