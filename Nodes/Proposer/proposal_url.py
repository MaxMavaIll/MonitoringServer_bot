import requests 
import logging
import toml 
import json
import subprocess
import time
import traceback
import aiohttp

from logging.handlers import RotatingFileHandler
from Bots.telegram_bot import BotTelegram
from WorkJson import WorkWithJson

config_toml = toml.load('config.toml')
work_json = WorkWithJson('Nodes/Proposer/receiver.json')
work_json_id = WorkWithJson('id.json')
telegram_bot = BotTelegram()

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_s = logging.StreamHandler()
log_s.setLevel(logging.INFO)
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
log_s.setFormatter(formatter2)

log_f = RotatingFileHandler(f"logs/vote/{__name__}.log",maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
log_f.setLevel(logging.DEBUG)
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
log_f.setFormatter(formatter2)

log.addHandler(log_s)
log.addHandler(log_f)

class Proposal:

    def __init__(
            self, 
            log_id: int, 
            name_network: str, 
            rpc: str,
            rest: str) -> None:
        self.log_id = log_id
        # self.bin = config_toml['proposal']['path'] + bin
        self.name_network = name_network
        self.rpc = rpc #if rpc == "" else ("--node " + rpc)
        self.rest = rest


    def GetNewProposals(
            self, 
            status: str = "PROPOSAL_STATUS_VOTING_PERIOD", 
            reverse: bool = False,
            limit: int = 20
            ) -> dict:
        log.debug(f"ID {self.log_id} | {self.name_network}  -> Get Proposals")

        def GetId(all_mass: dict):
            result = {}
            data = self.create_user()

            key_names = ['proposal_id', 'id']
            for proposal in all_mass['proposals']:
                for key_name in key_names:
                    proposal_id = proposal.get(key_name)
                    if proposal_id is not None and self.check_send_proposal_user(int(proposal_id), data):
                        
                        result[int(proposal_id)] = proposal
                    
                    log.debug(f"ID: {self.log_id} {self.name_network} -> помилковий ключ {key_name}")
                    
            if result == {}:
                log.info(f"ID: {self.log_id} {self.name_network} -> Вже повідомляв відносно цих пропозолів")

            return result

        url = f"{self.rest}/cosmos/gov/v1/proposals?proposal_status={status}&pagination.limit={limit}&pagination.reverse={reverse}"
        
        response = requests.get(url, verify=config_toml['ssl'])
        
        if response.status_code == 200:
            data = response.json()
            ids = GetId(data)

            if ids != {}:
                if config_toml['telegram_bot']['enable']:
                    for chat_id in config_toml['telegram_bot']['chat_id']:
                        telegram_bot.send_message(
                            message=f"🟩 NEW Proposals {self.name_network} 🟩", 
                            chat_id=chat_id, 
                            type_bot_token="TOKEN_PROPOSALS")

                return ids.items()

            

        else:
            log.error(f"ID {self.log_id} | {self.name_network}  "
                      f"-> This command received a non-200 status code:\n{response.text}")
        
        return []

    
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

        message = f"🔥 {self.name_network} - Proposal {proposal_id} 🔥"
        check_message = data.get('messages')
        check_content = data.get('content')
        # check_summary = data.get('summary')
        
        

        log.info(f"ID: {self.log_id} {self.name_network} | DATA -> {data}") 

        title = data.get('title')
        start_time = data.get('voting_start_time')
        end_time = data.get('voting_end_time')

        if check_message:
            message_data = check_message[0]
            
            # Check for upgrade plan and append if exists
            if message_data.get('content'):  
                title = message_data['content'].get('title')
                if message_data['content'].get('plan'):
                    plan = message_data['content']['plan']
                    message += f"\n\n<b>*--*UPGRADE*--*</b>\n\nHEIGHT: {plan['height']}\nName: {plan['name']}"

        elif check_content:
            title =  check_content.get('title')

        

        # Construct the main message
        message += f"\n<b>{title}</b>\n\nStart_Voting:\n\t\t{start_time}\nEnd_Voting:\n\t\t{end_time}"
        

        
        # elif check_metadata:
        #     message += f"\n\n<b>*--*UPGRADE*--*</b>\n\nHEIGHT: {plan['height']}\nName: {plan['name']}"

        # elif check_summary:
        #     pass

        # for key in keys:
        # if data.get(key):
        #     content_data = data[key][0]['content']  # Simplify access to content data
        #     title = content_data['title']
        #     start_time = data['voting_start_time']
        #     end_time = data['voting_end_time']
        
        #     # Construct the main message
        #     message += f"\n<b>{title}</b>\n\nStart_Voting:\n\t\t{start_time}\nEnd_Voting:\n\t\t{end_time}"
        
        #     # Check for upgrade plan and append if exists
        #     if content_data.get('plan'):
        #         plan = content_data['plan']
        #         message += f"\n\n<b>*--*UPGRADE*--*</b>\n\nHEIGHT: {plan['height']}\nName: {plan['name']}"


        # if data.get(key) == []:
        #     message += f"\n<b>{data[key]}</b> \n\n" + \
        #            f"Start_Voting:\n\t\t{data['voting_start_time']}\n" + \
        #            f"End_Voting:\n\t\t{data['voting_end_time']}"
            
        #     # if data[key][0]["content"].get('plan'):
        #     #     message += f"\n\n<b>*--*UPGRADE*--*</b>\n\nHEIGHT: {data[key][0]['content']['plan']['height']}\n" + \
        #     #             f"Name: {data[key][0]['content']['plan']['name']}"

        # else:
        #     title = data['content']['title']
        #     start_time = data['voting_start_time']
        #     end_time = data['voting_end_time']
            
        #     message += f"\n<b>{title}</b>\n\nStart_Voting:\n\t\t{start_time}\nEnd_Voting:\n\t\t{end_time}"
            
        #     # Check for upgrade plan in general content
        #     if data['content'].get('plan'):
        #         plan = data['content']['plan']
        #         message += f"\n\n<b>*--*UPGRADE*--*</b>\n\nHEIGHT: {plan['height']}\nName: {plan['name']}"

            

        if explorer_url != '':
            message += f"\n\n{explorer_url}{proposal_id}" 

        log.debug(f"ID: {self.log_id} {self.name_network} | MESSAGE -> {message}")       
            
        return message


    def add_to_cmd_command(self, variable: str, value: str, ) -> str:
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
                return { 'ok': False, 'answer': output[1].decode('utf-8')[0:200]+"\n\n"}
            
            return output
        except:
            log.exception(f"ID: {self.log_id} {self.name_network} -> error Terminal\n")
            message = "<b>Terminal</b> \n\n "
            message += traceback.format_exc()
            if config_toml['telegram_bot']['enable'] and reported:
                for id in config_toml['telegram_bot']['chat_id']:
                            telegram_bot.send_message(message=message, chat_id=id, type_bot_token="TOKEN_ERROR")

            return {'ok': False, 'answer': "Проблима з бінарником термінал не зміг знайти щось на сервері"}
    

def Proposer(
        network_name: str, 
        network: dict):
    log_id = work_json_id.get_json()['id']

    try:
        proposer = Proposal(
            log_id=log_id,
            name_network=network_name,
            rpc=network["rpc"],
            rest=network["rest"])

        for proposal_id, data in proposer.GetNewProposals():

            
            if config_toml['telegram_bot']['enable']:
                message = proposer.create_text(proposal_id=proposal_id, data=data)
                for id in config_toml['telegram_bot']['chat_id']:
                    if telegram_bot.send_message(message=message, chat_id=id, type_bot_token="TOKEN_PROPOSALS"):
                        data = work_json.get_json()
                        data[id][network_name].append(proposal_id)
                        
                data[id][network_name] = sorted(data[id][network_name], reverse=True)
                work_json.set_json(data=data)
                time.sleep(config_toml['proposal']['time_sleep'])

    except Exception as e:
        message = f"<b>Proposer\nlog_id: {log_id}</b> \n\n "
        message += traceback.format_exc()
        log.exception(f"Proposer:")
        
        if config_toml['telegram_bot']['enable']:
            for id in config_toml['telegram_bot']['chat_id']:
                        telegram_bot.send_message(message=message, chat_id=id, type_bot_token="TOKEN_ERROR")
