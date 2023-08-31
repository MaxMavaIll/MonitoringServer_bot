import requests, toml, logging, json
from logging.handlers import RotatingFileHandler

from WorkJson import WorkWithJson

config_toml = toml.load("config.toml")
work_json = WorkWithJson("id.json")

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/telegram_bot/{__name__}.log", maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)

class BotTelegram():


    def send_message(self, message: str, chat_id: int|str, type_bot_token: str = "TOKEN"):
        """
        type_bot_token | TOKEN_ERROR, TOKEN_PROPOSALS, TOKEN_SERVER, TOKEN_NODE
        """
        log.info(f"Відправляю повідомлення -> {chat_id}")
        TOKEN = config_toml["telegram_bot"][type_bot_token] if config_toml["telegram_bot"][type_bot_token] != '' else config_toml["telegram_bot"][f"TOKEN"]

        id = work_json.get_json()["id"]
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        # url = url + f'/sendMessage?chat_id={chat_id}&text={message}'
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        
        response = requests.post(url=url, data=data, timeout=5)

        if response.status_code == 200:
            log.info(f"ID: {id} -> Повідомлення було відправиленно успішно код {response.status_code}")
            log.debug(f"ID: {id} -> Отримано через папит:\n{response.text}")
            return True
        else:
            message = f"ID: {id} -> Повідомлення отримало код {response.status_code}"
            log.error(f"ID: {id} -> Повідомлення отримало код {response.status_code}")
            log.error(response.text)
            log.error(f"ID: {id} -> url: {url}")
            log.error(f"ID: {id} -> data: {data}")

            return False

        