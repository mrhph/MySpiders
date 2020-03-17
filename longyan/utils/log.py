import os
import logging

from datetime import datetime

get_log_month = lambda month: month if month > 10 else '0' + str(month)  # 日志文件名month
today = datetime.now()

class Log:
    def __init__(self, terrace=None):
        if not isinstance(terrace, str):
            raise ValueError('请传入terrace，type：string')
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.terrace = terrace
        self.filename = self.log_file()

    def create_logger(self):
        logger = logging.getLogger()  #创建logger
        logger.setLevel(logging.DEBUG)  # 设置级别

        log_stream = logging.StreamHandler()  # 创建终端输出handler
        log_stream.setLevel(logging.INFO)

        log_file = logging.FileHandler(self.filename, mode='w', encoding='utf-8')  # 创建日志文件handler
        log_file.setLevel(logging.INFO)


        format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')  # 设置日志格式
        log_stream.setFormatter(format)
        log_file.setFormatter(format)

        logger.addHandler(log_stream)
        logger.addHandler(log_file)
        return logger

    def log_file(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = base_dir + '/log/'
        if not os.path.exists(path):
            os.mkdir(path)
        filename = '{}{}.log'.format(self.terrace, today.strftime('%Y%m%d'))
        file = path + filename
        return file


def logger(terrace=None):
    if terrace == None or terrace == '':
        raise TypeError('logger() should take an argument or parameter and it not be null character string')
    return Log(terrace).create_logger()