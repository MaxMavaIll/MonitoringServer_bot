import logging
import toml
import time
import json
import asyncio

from logging.handlers import RotatingFileHandler

import function
from Server.server import check_server
# from Nodes.Vote.CosmosCLI import Vote_Active_Proposal
from Nodes.Proposer.proposal_cmd import Proposer
from WorkJson import WorkWithJson

config_toml = toml.load('config.toml')
work_json = WorkWithJson('id.json')

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

log_s = logging.StreamHandler()
log_s.setLevel(logging.INFO)
formatter2 = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
log_s.setFormatter(formatter2)

log_f = RotatingFileHandler(
    f"logs/main.log",maxBytes=config_toml['logging']['max_log_size'] * 1024 * 1024, backupCount=config_toml['logging']['backup_count'])
log_f.setLevel(logging.DEBUG)
formatter2 = logging.Formatter(
    "%(name)s %(asctime)s %(levelname)s %(message)s")
log_f.setFormatter(formatter2)

log.addHandler(log_s)
log.addHandler(log_f)


def main():

    ID = work_json.get_json()["id"]

    while 1:
        log.info(f"ID: {ID} -> Запуск")
        start_time = time.time()

        if config_toml['check_disk']['enable'] and function.runtime_check(config_toml['check_disk']['time'], 'Check_Disk', ID): 
            check_server()
        
        if config_toml['proposal']['enable'] and function.runtime_check(config_toml['proposal']['time'], 'Proposal', ID):
            Proposer()

        # if config_toml['vote']['enable']:
        #     Vote_Active_Proposal()

        finish_time =time.time() - start_time
        log.info(f"ID: {ID} -> Час виконання: {finish_time}")

        ID += 1
        work_json.set_json({'id': ID})

        logging.info(f"Wait {config_toml['time']} хв")
        time.sleep(config_toml['time'] * 60)
    
    


if __name__ == "__main__":
    main()

