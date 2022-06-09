from abc import ABC, abstractmethod
from typing import List

from deployer.common_dataclasses import Config


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
            provider: str = None,
            provider_id: str = None,
            constructor_parasms: List[str] = None,
            config: Config = None,
    ):
        """
        Creates user if needed, create project, compile contract code and deploy
        """