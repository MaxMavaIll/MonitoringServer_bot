import requests, toml, logging, json
from logging.handlers import RotatingFileHandler

config_toml = toml.load("config.toml")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/telegram_bot/{__name__}.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)

class BotTelegram():

    def __init__(self, token: str) -> None:
        self.token = token

    def send_message(self, message: str, chat_id: int|str):
        id = self.get_id()
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        # url = url + f'/sendMessage?chat_id={chat_id}&text={message}'
        data = {'chat_id': chat_id, 'text': message}
        try:
            response = requests.post(url=url, data=data, timeout=5)

            if response.status_code == 200:
                log.info(f"ID: {id} -> Повідомлення було відправиленно успішно код {response.status_code}")
                log.debug(f"ID: {id} -> Отримано через папит:\n{response.text}")
                return True
            else:
                log.error(f"ID: {id} -> Повідомлення отримало код {response.status_code}")
                log.error(response.text)
                log.error(f"ID: {id} -> url: {url}")
                log.error(f"ID: {id} -> data: {data}")
                return False
        except:
            log.exception(f"ID: {id} -> Telegram bot Error")
            return False
            
    def get_id(self):
        with open("id.json") as file:
            ID = json.load(file)['id']
        
        return ID