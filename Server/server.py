import psutil, toml, logging
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

# print("Загальна пам'ять: {} GB".format(memory.total / (1024 ** 3)))
# print("Використано пам'яті: {} GB".format(memory.used / (1024 ** 3)))
# print("Вільної пам'яті: {} GB".format(memory.free / (1024 ** 3)))
# print("Використано відсотків пам'яті: {}%".format(memory.percent))

# print(psutil.cpu_percent(interval=1, percpu=True))

bot_telegram = BotTelegram(token=config_toml["telegram_bot"]["TOKEN"])

class MonitoringServer():

    def GetDiskParameters(self) -> list:
        list_disks = list()
        for path in config_toml['check_disk']['path']:
            disk = psutil.disk_usage(path=path)

            # print("Загальна пам'ять: {} GB".format(disk.total / (1024 ** 3)))
            # print("Використано пам'яті: {} GB".format(disk.used / (1024 ** 3)))
            # print("Вільної пам'яті: {} GB".format(disk.free / (1024 ** 3)))
            # print("Використано відсотків пам'яті: {}%".format(disk.percent), end='\n\n')
            
            list_disks.append(disk)

        log.info("Get disk memory")

        return list_disks

server = MonitoringServer()

def Sever_disk(list_disk_param: list) -> tuple:
    total = list()
    used = list()
    free = list()
    percent = list()

    for disk in list_disk_param:
        total.append( int( disk[0] / (1024 ** 3) ) )
        used.append( int( disk[1] / (1024 ** 3) ) )
        free.append( int( disk[2] / (1024 ** 3) ) )
        percent.append(disk[3])
    
    log.debug(f"Відсортований результат:\ntotal: {total}\nused: {used}\nfree: {free}\npercent: {percent}")
    
    return tuple(total), tuple(used), tuple(free), tuple(percent)
    

def check_server():
    try: 
        log.info("Отримую дані з диска")
        disk_list = server.GetDiskParameters()
        log.info("Отримано дані: success done")

        log.info("Я відсортовую результат")
        total, used, free, percent = Sever_disk(disk_list)
        log.info("Сортування: success done")

        for index in range(len(percent)):

            if percent[index] >= config_toml['telegram_bot']['interest']:
                log.info(f"Памʼять закінчується на {config_toml['check_disk']['path'][index]} залишилося {100 - percent[index]}%")
                massage = f"Sever: 173\n" + \
                        f"Path: {config_toml['check_disk']['path'][index]} \n" + \
                        f"Memory problem {percent[index]}%\n" + \
                        f"Date:\n\ttotal: {total[index]}\n\tused: {used[index]}\n\tfree: {free[index]} \n" 
                        # f"Date: {total[index]} {used[index]} {free[index]}"
                
                if config_toml['telegram_bot']['enable']:
                    for id in config_toml['telegram_bot']['chat_id']:
                        if not bot_telegram.send_message(message=massage, chat_id=id):
                            log.info(f"Не відправленно дивитись в Bots.telegram_bot.log")

                log.info(massage)

    except:
        log.exception("Зпапит на отримання памʼяті дотримав помилку")

