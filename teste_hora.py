import helper
from booking import Booking
import fdb
from sincronismo import Sincronismo
from agenda import Agenda
from configuracao import Configuracao

configuracao = Configuracao()
con = fdb.connect(
    dsn=configuracao.db_host + ':' + configuracao.db_path,
    user=configuracao.db_user, password=configuracao.db_password)
cur = con.cursor()
controle=1249
qry_sync=(" UPDATE SINCRONISMO_WEB SET STATUS = 'ABE' WHERE CONTROLE = {controle} ".format(controle=controle))
cur.execute(qry_sync)
con.commit()
cur.close()
con.close()
