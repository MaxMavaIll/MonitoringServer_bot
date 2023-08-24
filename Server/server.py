import psutil, toml, logging, json, os
from logging.handlers import RotatingFileHandler
from Bots.telegram_bot import BotTelegram

from WorkJson import WorkWithJson

config_toml = toml.load("config.toml")
work_json = WorkWithJson("id.json")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/server/{__name__}.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)


bot_telegram = BotTelegram()

class MonitoringServer():

    def GetDiskParameters(self) -> list:
        list_disks = list()
        path_list = list()
        id = work_json.get_json()["id"]
        for path in config_toml['check_disk']['path']:
            if os.path.exists(path):
                disk = psutil.disk_usage(path=path)
                log.info(path)
            
                list_disks.append(disk)
                path_list.append(path)
            else:
                log.warn(f"ID: {id} -> Path not found: {path}\nPerhaps you forgot to add the path to the docker-compose.yml.")

        log.info(f"ID: {id} -> Отримано дані: success done")

        return list_disks, path_list



server = MonitoringServer()

def Sever_disk(list_disk_param: list) -> tuple:

    id = work_json.get_json()["id"]
    total = list()
    used = list()
    free = list()
    percent = list()

    for disk in list_disk_param:
        total.append( int( disk[0] / (1024 ** 3) ) )
        used.append( int( disk[1] / (1024 ** 3) ) )
        free.append( int( disk[2] / (1024 ** 3) ) )
        percent.append(disk[3])
    
    log.debug(f"ID: {id} -> Відсортований результат:\ntotal: {total}\nused: {used}\nfree: {free}\npercent: {percent}")
    
    log.info(f"ID: {id} -> Сортування: success done")
    return tuple(total), tuple(used), tuple(free), tuple(percent)
    

def check_server():
    try: 
        id = work_json.get_json()["id"]

        log.info(f"ID: {id} -> Отримую дані з диска")
        disk_list, path_list = server.GetDiskParameters()

        log.info(f"ID: {id} -> Я відсортовую результат")
        total, used, free, percent = Sever_disk(disk_list)
        

        for index in range(len(percent)):

            massage = f"Sever: 173\n" + \
                        f"Path: {path_list[index]} \n" + \
                        f"Memory problem {percent[index]}%\n" + \
                        f"Date:\n\ttotal: {total[index]}\n\tused: {used[index]}\n\tfree: {free[index]} \n"
     
            if percent[index] >= config_toml['telegram_bot']['interest']:
                log.info(f"ID: {id} -> Памʼять закінчується на {path_list[index]} залишилося {100 - percent[index]}%")
                if config_toml['telegram_bot']['enable']:
                    for id in config_toml['telegram_bot']['chat_id']:
                        if not bot_telegram.send_message(
                            message=massage,
                            chat_id=id):
                            log.info(f"ID: {id} -> Не відправленно дивитись в Bots.telegram_bot.log")

            
            log.info(massage)

    except:
        log.exception(f"ID: {id} -> Зпапит на отримання памʼяті дотримав помилку")

