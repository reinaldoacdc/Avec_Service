import logging
from datetime import datetime

class PrintLog:

    def MakeFile(self):
        t = datetime.now()
        logging.basicConfig(
            filename = 'avec-service'+t.strftime('%d%m%Y')+'.log',
            level = logging.INFO,
            format = '[avec-service] %(asctime)s %(levelname)-7.7s %(message)s'
        )

    def Info(self, msg):
        self.MakeFile()
        print(msg)
        logging.info(msg)

    def Erro(self, msg):
        self.MakeFile()
        print(msg)
        logging.error(str(msg), exc_info=True)
