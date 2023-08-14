import logging, toml, time, json
from logging.handlers import RotatingFileHandler

import function
from Server.server import check_server

config_toml = toml.load('config.toml')

log = logging.getLogger('main')
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/main.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():

    with open("id.json") as file: 
        ID = json.load(file)['id']

    while 1:
        log.info("ID: {ID} -> Запуск")
        start_time = time.time()

        if config_toml['check_disk']['enable'] and function.runtime_check(config_toml['check_disk']['time'], 'Check_Disk', ID): 
            check_server()


        finish_time =time.time() - start_time
        log.info(f"ID: {ID} -> Час виконання: {finish_time}")

        with open("id.json", 'w') as file: 
            ID += 1
            json.dump({'id': ID}, file)

        logging.info(f"Wait {config_toml['time']} хв")
        time.sleep(config_toml['time'] * 60)
    
    


if __name__ == "__main__":
    main()

