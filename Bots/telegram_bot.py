import requests, toml, logging
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
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        # url = url + f'/sendMessage?chat_id={chat_id}&text={message}'
        data = {'chat_id': chat_id, 'text': message}
        try:
            response = requests.post(url=url, data=data, timeout=5)

            if response.status_code == 200:
                log.info(f"Повідомлення було відправиленно успішно код {response.status_code}")
                log.debug(f"Отримано через папит:\n{response.text}")
                return True
            else:
                log.error(f"Повідомлення отримало код {response.status_code}")
                log.error(response.text)
                log.error(f"url: {url}")
                log.error(f"data: {data}")
                return False
        except:
            log.exception("Telegram bot Error")
            return False
            
        