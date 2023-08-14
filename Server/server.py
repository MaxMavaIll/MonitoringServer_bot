import psutil, toml, logging, json
from logging.handlers import RotatingFileHandler
from Bots.telegram_bot import BotTelegram

ram = psutil.virtual_memory()
disk = psutil.disk_usage('/')
config_toml = toml.load("config.toml")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/server/{__name__}.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)


bot_telegram = BotTelegram(token=config_toml["telegram_bot"]["TOKEN"])

class MonitoringServer():

    def GetDiskParameters(self) -> list:
        list_disks = list()
        for path in config_toml['check_disk']['path']:
            disk = psutil.disk_usage(path=path)
            
            list_disks.append(disk)

        log.info("ID: {id} -> Отримано дані: success done")

        return list_disks

    def get_id(self):
        with open("id.json") as file:
            ID = json.load(file)['id']
        
        return ID

server = MonitoringServer()

def Sever_disk(list_disk_param: list) -> tuple:

    id = server.get_id()
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
        id = server.get_id()

        log.info(f"ID: {id} -> Отримую дані з диска")
        disk_list = server.GetDiskParameters()

        log.info(f"ID: {id} -> Я відсортовую результат")
        total, used, free, percent = Sever_disk(disk_list)
        

        for index in range(len(percent)):

            if percent[index] >= config_toml['telegram_bot']['interest']:
                log.info(f"ID: {id} -> Памʼять закінчується на {config_toml['check_disk']['path'][index]} залишилося {100 - percent[index]}%")
                massage = f"Sever: 173\n" + \
                        f"Path: {config_toml['check_disk']['path'][index]} \n" + \
                        f"Memory problem {percent[index]}%\n" + \
                        f"Date:\n\ttotal: {total[index]}\n\tused: {used[index]}\n\tfree: {free[index]} \n" 
                        # f"Date: {total[index]} {used[index]} {free[index]}"
                
                if config_toml['telegram_bot']['enable']:
                    for id in config_toml['telegram_bot']['chat_id']:
                        if not bot_telegram.send_message(message=massage, chat_id=id):
                            log.info(f"ID: {id} -> Не відправленно дивитись в Bots.telegram_bot.log")

                log.info(massage)

    except:
        log.exception(f"ID: {id} -> Зпапит на отримання памʼяті дотримав помилку")

