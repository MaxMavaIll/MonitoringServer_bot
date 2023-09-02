import requests, logging, toml, json, subprocess, time, traceback
from logging.handlers import RotatingFileHandler
from Bots.telegram_bot import BotTelegram

from WorkJson import WorkWithJson

config_toml = toml.load('config.toml')
work_json = WorkWithJson('Nodes/Proposer/receiver.json')
work_json_id = WorkWithJson('id.json')
telegram_bot = BotTelegram()

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler2 = RotatingFileHandler(f"logs/vote/{__name__}.log",maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler2.setFormatter(formatter2)
log.addHandler(handler2)

class Proposal:

    def __init__(self, log_id: int, bin: str, name_network: str, node: str) -> None:
        self.log_id = log_id
        self.bin = config_toml['proposal']['path'] + bin
        self.name_network = name_network
        self.node = node if node == "" else ("--node " + node)

    def GetNewProposals(
            self, 
            status: str = None, 
            reverse: bool = None,
            limit: int = None
            ) -> dict:
        
        def GetId(all_mass: dict):
            result = {}
            data = self.create_user()

            key_names = ['proposal_id', 'id']
            for proposal in all_mass['proposals']:
                for key_name in key_names:
                    proposal_id = proposal.get(key_name)
                    if proposal_id is not None and self.check_send_proposal_user(int(proposal_id), data):
                        
                        result[int(proposal_id)] = proposal
                    
            if result == {}:
                log.info(f"ID: {self.log_id} {self.name_network} -> Помилкові ключі (proposal_id, id)\nІ голосували за ці пропозали")

            return result

        cmd = f"{self.bin} q gov proposals -o json {self.node} "

        if status:
            cmd += self.add_to_cmd_command("status", status)
        if reverse:
            cmd += " --reverse"
        if limit:
            cmd += self.add_to_cmd_command("limit", limit)

        answer = self.terminal(cmd)

        if not answer['ok']:
            log.error(f"ID: {self.log_id} {self.name_network} -> Ця команда отримала не dict формат:\n{answer['answer']}")
            log.warn(f"ID: {self.log_id} {self.name_network} -> Вертаю []")
            return {}
        
        

        ids = GetId(json.loads(answer['answer']))

        if ids != {}:
            if config_toml['telegram_bot']['enable']:
                for id in config_toml['telegram_bot']['chat_id']:
                    telegram_bot.send_message(message="🟩 NEW Proposals 🟩", chat_id=id, )

        return ids.items()
    
    def check_send_proposal_user(self, proposal_id: int, data: dict):
        

        for id in data:
            if proposal_id in data[id][self.name_network]:
                return False
        
        data[id][self.name_network].append(proposal_id)
        return True

    def create_user(self) -> dict:
        vote_data = work_json.get_json()

        for chat_id in config_toml['telegram_bot']['chat_id']:
            if chat_id not in vote_data:
                vote_data[chat_id] = {}

            if self.name_network not in vote_data[chat_id]:
                vote_data[chat_id][self.name_network] = []
        
        work_json.set_json(data=vote_data)
        return vote_data

    def create_text(self, proposal_id: int, data: dict):
        explorer_url = config_toml['proposal']['network'][self.name_network]["explorer"]
        message = f"🔥 {self.name_network} - Proposal {proposal_id} 🔥\n<b>{data['content']['title']}</b> \n\n" + \
                f"Start_Voting:\n\t\t{data['voting_start_time']}\n" + \
                f"End_Voting:\n\t\t{data['voting_end_time']}"

        if data["content"].get('plan') is not None:
            message += f"\n\n<b>*--*UPGRADE*--*</b>\n\nHEIGHT: {data['content']['plan']['height']}\n" + \
                    f"Name: {data['content']['plan']['name']}"

        if explorer_url != '':
            message += f"\n\n{explorer_url}{proposal_id}" 

        log.debug(f"ID: {self.log_id} {self.name_network} | MESSAGE -> {message}")       
            
        return message
            
    def add_to_cmd_command(self, variable: str, value: str|int|bool, ) -> str:
        return f" --{variable} {value}"

    def terminal(
            self, 
            cmd: str = None, 
            password: str = "Not password",
            reported: bool = False
            ) -> str:
        try:
            log.debug(f"ID: {self.log_id} {self.name_network} | CMD -> {cmd}")
            cmd = cmd.split()
            p1 = subprocess.Popen(["echo", password], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=p1.stdout)
            output = p2.communicate()
            p1.stdout.close()
            p2.stdout.close()
            log.debug(f"ID: {self.log_id} {self.name_network} | ANSWER -> {output}")
            if output[0].decode('utf-8') != '':
                return { 'ok': True, 'answer': output[0].decode('utf-8')}
            elif output[1].decode('utf-8') != '':
                return { 'ok': False, 'answer': output[1].decode('utf-8')}
            
            return output
        except:
            log.exception(f"ID: {self.log_id} {self.name_network} -> error Terminal\n")
            message = "<b>Terminal</b> \n\n "
            message += traceback.format_exc()
            if config_toml['telegram_bot']['enable'] and reported:
                for id in config_toml['telegram_bot']['chat_id']:
                            telegram_bot.send_message(message=message, chat_id=id, type_bot_token="TOKEN_ERROR")

            return {'ok': False, 'answer': "Проблима з бінарником термінал не зміг знайти щось на сервері"}
    

def Proposer():
    log_id = work_json_id.get_json()['id']
    for network in config_toml['proposal']['network']:
        try:
            proposer = Proposal(
                log_id=log_id,
                bin=config_toml['proposal']['network'][network]["bin"],
                name_network=network,
                node=config_toml['proposal']['network'][network]["node"]
            )

            for proposal_id, data in proposer.GetNewProposals(
                status="PROPOSAL_STATUS_VOTING_PERIOD",
                limit=20
                ):

                
                if config_toml['telegram_bot']['enable']:
                    message = proposer.create_text(proposal_id=proposal_id, data=data)
                    for id in config_toml['telegram_bot']['chat_id']:
                        if telegram_bot.send_message(message=message, chat_id=id, type_bot_token="TOKEN_PROPOSALS"):
                            data = work_json.get_json()
                            data[id][network].append(proposal_id)
                            
                    data[id][network] = sorted(data[id][network], reverse=True)
                    work_json.set_json(data=data)
                    time.sleep(config_toml['proposal']['time_sleep'])

        except Exception as e:
            message = f"<b>Proposer\nlog_id: {log_id}</b> \n\n "
            message += traceback.format_exc()
            log.exception(f"Proposer:")
            
            if config_toml['telegram_bot']['enable']:
                for id in config_toml['telegram_bot']['chat_id']:
                            telegram_bot.send_message(message=message, chat_id=id, type_bot_token="TOKEN_ERROR")
