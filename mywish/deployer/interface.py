from abc import ABC, abstractmethod
from typing import List

from mywish.deployer.common_dataclasses import Config


class IDeployer(ABC):

    @abstractmethod
    def deploy(
            self,
            contract_code,
            account_name,
            account_pass,
            private_key,
            network,
            contract_name,
            etherscan_api_token,
            provider: str = None,
            provider_id: str = None,
            constructor_params: List[str] = None,
            config: Config = None,
    ) -> str:
        """
        Deploy contract with received parameters.
        Creates user if needed, create project, compile contract code and then deploy.

        :param contract_code: Full smart contract code
        :param account_name: The name of the account that will be used when deploying contracts
        :param account_pass: The name of the account that will be used when deploying contracts
        :param private_key: The private of the account that will be used when deploying contracts
        :param network: Network where contract will be deployed
        :param contract_name: Contract name which will be used in deployment script
        :param etherscan_api_token: Developer Etherscan API token
        :param provider: Provider to use if network needs provider
        :param provider_id: Provider ID
        :param constructor_params: Params which will be used in contract deployment
        :param config: Dataclass with all configurations for brownie projects

        :return: Deployed contract address
        """
