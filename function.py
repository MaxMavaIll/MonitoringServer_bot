import time, datetime, toml, logging
from logging.handlers import RotatingFileHandler

config_toml = toml.load('config.toml')

log = logging.getLogger('function')
log.setLevel(logging.DEBUG)
handler2 = RotatingFileHandler(f"logs/function.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)

def runtime_check(times: str, name: str, id: int) -> bool:
    time_now = datetime.datetime.now().time()
    log.info(f"Name service: {name} | Get {times} now time {time_now}")

    if times == '':
        return True
    
    elif times != '':
        
        for time in times.split(','):
            log.debug(f"{datetime.timedelta()} <= {datetime.timedelta(hours=time_now.hour, minutes=time_now.minute) - datetime.timedelta(hours=int(time))} <= {datetime.timedelta(minutes=config_toml['time'])}")
            
            if datetime.timedelta() <= datetime.timedelta(hours=time_now.hour, minutes=time_now.minute) - datetime.timedelta(hours=int(time))  <= datetime.timedelta(minutes=config_toml['time']):
                log.info(f"Name service: {name} | Get True")
                return True
    
    log.info(f"ID: {id} -> Name service: {name} | Get False")
    return False

