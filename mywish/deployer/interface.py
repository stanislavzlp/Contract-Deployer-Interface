from abc import ABC, abstractmethod
from typing import List

from mywish.deployer.common_dataclasses import Config


class IDeployer(ABC):

    @abstractmethod
    def deploy(
            self,
            *args,
            **kwargs,
    ) -> str:
        """
        Deploy contract with received parameters and returns contract or transaction ID
        """
