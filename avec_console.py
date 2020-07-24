import time
import helper
import logging
from avec_email import Email
from configuracao import Configuracao
from booking import Booking
from sincronismo import Sincronismo
from push_notification import PushNotification
from dao import Dao
from printlog import PrintLog

printlog = PrintLog()
ListaClientesNaoAchados = [] 

def send_push():
    printlog.Info('send_push...')
    lista = Dao().get_pushs()
    printlog.Info('resultado = ['+str(len(lista))+']')
    for item in lista:
        printlog.Info('push: ' + str(item))
        push = PushNotification(item)
        push.send_push()
        push.set_finalizado()


def importa_agendamentos():
    printlog.Info('importa_agendamentos...')
    lista = helper.get_bookings()

    if (lista['code'] == 401):
        printlog.Info('Erro 401 = '+lista['message'])
    else:
        printlog.Info('resultado = ['+str(len(lista['data']['bookings']))+']')
        for item in lista['data']['bookings']:
            printlog.Info('api: ' + str(item))
            agenda = Booking(item)

            if (agenda.salao_cliente_id > 0):
                agenda.cliente_importado()

            if agenda.status == 0:
                agenda.salva_auditoria(3)
                agenda.exclui_agenda()
                notificado = 1
                status = 0
            else:
                if not (agenda.is_available()):
                    agenda.salva_booking()
                    agenda.salva_auditoria(1)
                    notificado = 1
                    status = 1
                else:
                    notificado = 1
                    status = 0
            helper.post_sincronizado(status, notificado, agenda.id)


def exporta_agendamentos():
    printlog.Info('exporta_agendamentos...')
    lista = Dao().get_sincronismo()
    printlog.Info('resultado = ['+str(len(lista))+']')
    for item in lista:
        printlog.Info('agenda: ' + str(item))
        sinc = Sincronismo(item)
        sinc.informacao()
        if sinc.valida_registro() :
            retorno = sinc.valida_cliente(ListaClientesNaoAchados) 
            if retorno[0] == 1:
                sinc.sincronizar()
            elif retorno[0] == 2:
                ListaClientesNaoAchados.append(retorno[1])
                try:
                    configuracao = Configuracao()
                    Email(configuracao, 'EXPORTA_AGENDAMENTO', 'Cliente id '+retorno[1]+' não existe no svip', 'Export Sallon: ' + configuracao.app_id).send_mail()
                except Exception as e:
                    printlog.Info('nao foi possivel enviar email exception : ' + str(e))

def main():
    printlog.Info('Inicio da Sincronização...')
    configuracao = Configuracao()
    if (configuracao.AllOk()):
        while True:
            try:
                importa_agendamentos()
            except Exception as e:
                printlog.Erro(e)
                Email(configuracao, 'IMPORTACAO_AGENDAMENTO', e, 'Import Sallon: ' + configuracao.app_id).send_mail()
                printlog.Info('importa_agendamentos exception: ' + str(e))

            try:
                exporta_agendamentos()
            except Exception as e:
                printlog.Erro(e)
                Email(configuracao, 'EXPORTA_AGENDAMENTO', e, 'Export Sallon: ' + configuracao.app_id).send_mail()
                printlog.Info('exporta_agendamentos exception : ' + str(e))

            try:
                send_push()
            except Exception as e:
                printlog.Erro(e)
                Email(configuracao, 'SEND_PUSH', e, 'Push Sallon: ' + configuracao.app_id).send_mail()
                printlog.Info('send_push: ' + str(e))

            time.sleep(3)


if __name__ == "__main__":
    main()
