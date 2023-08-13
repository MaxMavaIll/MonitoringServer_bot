import logging, toml, time
from logging.handlers import RotatingFileHandler

from Server.server import check_server

config_toml = toml.load('config.toml')

log = logging.getLogger('main')
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/main.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)


def main():
    
    check_server()


  
    
    


if __name__ == "__main__":
    log.info("Запуст")
    start_time = time.time()

    main()

    finish_time =time.time() - start_time
    log.info(f"Завершилося з результатом: {finish_time}")