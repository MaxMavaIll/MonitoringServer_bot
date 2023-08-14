import requests, logging, toml, json
from logging.handlers import RotatingFileHandler

class CosmosApi():

    def __init__(self, url: str = "http://localhost", port: int = 1317) -> None:
        self.url = url
        self.port = port

    def GetProposals(self, proposal_status: str = "PROPOSAL_STATUS_VOTING_PERIOD"):

        a = requests.post(url=f"{self.url}:{self.port}/cosmos/gov/v1/proposals", data={"proposal_status": proposal_status})
        # ?proposal_status={proposal_status}
        print(a.text)


cosmosApi = CosmosApi(url="https://kujira.nodejumper.io")
cosmosApi.GetProposals("PROPOSAL_STATUS_PASSED")