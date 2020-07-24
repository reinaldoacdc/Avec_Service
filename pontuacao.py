import fdb
from configuracao import Configuracao

class Pontuacao:

    def __init__(self, cliente_idweb, pontos):
        self.pontos = pontos
        self.cliente_idweb = cliente_idweb

    def parse_to_json(self):
        return {
            'salao_cliente_id': self.cliente_idweb,
            'pontos': self.pontos
        }

    @staticmethod
    def pesquisa_pontuacao(controle):
        configuracao = Configuracao()
        con = fdb.connect(
            dsn=configuracao.db_host + ':' + configuracao.db_path,
            user=configuracao.db_user, password=configuracao.db_password, fb_library_name=configuracao.db_lib)
        cur = con.cursor()
        qry_sync=("SELECT CONTROLE, CREDITO, DEBITO, CLIENTES.ID_WEB "            
            "  FROM CONTA_PONTOS  "
            "LEFT JOIN CLIENTES ON CONTA_PONTOS.CODIGO_CLIENTE = CLIENTES.CODIGO_CLIENTE"
            "   AND CONTA_PONTOS.EMP_CLIENTE = CLIENTES.CODIGO_EMPRESA "
            "WHERE CONTROLE = {controle} ".format(controle=controle))

        cur.execute(qry_sync)
        columns = [column[0] for column in cur.description]
        results = []
        for row in cur.fetchall():
         results.append(dict(zip(columns, row)))
        return results
