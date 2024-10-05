import logging
import colorlog
from logging.handlers import RotatingFileHandler
from threading import Lock

class SingletonLogger:
    _instance = None
    _lock = Lock()  # 保证线程安全

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SingletonLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_file='app.log', log_level=logging.DEBUG):
        if not hasattr(self, '_initialized'):  # 避免重复初始化
            self._initialized = True
            self.logger = logging.getLogger("my_logger")
            self.logger.setLevel(log_level)

            # 创建终端输出的 handler，并设置彩色格式
            console_handler = logging.StreamHandler()
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                }
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

            # 创建写入文件的 handler
            file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)  # 文件大小5MB，保留5个备份
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

# 使用示例
if __name__ == "__main__":
    logger = SingletonLogger().get_logger()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
