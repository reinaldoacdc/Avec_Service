import requests
import urllib3
import json
from configuracao import Configuracao
from printlog import PrintLog

printlog = PrintLog()

def get_bookings():
    urllib3.disable_warnings()
    config = Configuracao()
    url = 'https://api.salaovip.com.br/salao/' + config.app_id + '/reservas/sincronizado'
    headers = {'authorization': config.app_token}
    r = requests.get(url, headers=headers, timeout=20)
    return json.loads(r.text)

def post_sincronizado(status, notificado, reserva_id):
    urllib3.disable_warnings()
    config = Configuracao()
    url = 'https://api.salaovip.com.br/salao/' + config.app_id + '/reservas/sincronizar/' + str(reserva_id)
    headers = {'authorization': config.app_token}
    data = {'status': status, 'notificar': notificado}
    requests.post(url, data, headers=headers, timeout=20)

def get_cliente(cliente_id):
    urllib3.disable_warnings()
    config = Configuracao()
    url = 'https://api.salaovip.com.br/salao/' + config.app_id + '/cliente/' + str(cliente_id)
    headers = {'authorization': config.app_token}
    r = requests.get(url, headers=headers, timeout=20)
    return json.loads(r.text)
