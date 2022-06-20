import os
from contextvars import Context, copy_context
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union

import yaml
from brownie import accounts
from brownie.network.contract import ProjectContract
from brownie.network.transaction import TransactionReceipt
from brownie.project.main import Project, new
from brownie.project import run

from mywish.deployer.common_dataclasses import Config
from mywish.deployer.exeptions import DeployError, ErrorCodes
from mywish.deployer.interface import IDeployer


class BrownieDeployer(IDeployer):
    """Brownie Adapter class for interaction with
    brownie
    """

    def deploy(
            self,
            contract_code,
            network,
            account_name,
            account_pass,
            private_key,
            contract_name,
            etherscan_api_token,
            provider: str = None,
            provider_id: str = None,
            constructor_params: List[str] = None,
            config: Config = None,
    ) -> str:
        """
        Creates user if needed, create project, compile contract code and deploy

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

        with TemporaryDirectory() as tmp_dir:

            project_dir = Path(tmp_dir)

            try:
                new(str(project_dir))
            except Exception as e:
                raise DeployError(
                    ErrorCodes.CANNOT_CREATE_NEW_PROJECT,
                    exception=e,
                )

            self._create_token_file(project_dir, contract_code)
            self._create_project_config_file(project_dir, config)

            Project('brownie_project', project_dir)

            script_path = self._create_script_for_deploy(
                project_dir,
                contract_name,
                network,
                account_name,
                account_pass,
                constructor_params,
            )

            self._set_provider_if_need(provider, provider_id)

            self._set_etherscan_api_token(etherscan_api_token)
            try:
                run(script_path=script_path, project=project_dir)
            except Exception as e:
                raise DeployError(ErrorCodes.CANNOT_DEPLOY_CONTRACT, exception=e)

            token_var = self._get_token_variable_from_context()
            return token_var

    def _get_contract_deploy_script_code(
            self,
            contract_name: str,
            network: str,
            account_name: str,
            account_pass: str,
    ) -> str:
        """
        Creates script code for contract without constructor and
        returns it

        :param contract_name: Contract name which will be used in deployment script
        :param network: Network where contract will be deployed
        :param account_name: The name of the account that will be used when deploying contracts
        :param account_pass: The name of the account that will be used when deploying contracts

        :return: Scripts code for contract deployment script.py
        """

        script = '''
from brownie import {0}, accounts
from brownie import network
from contextvars import ContextVar


def main():
    if network.is_connected():
        if not network.show_active() == '{1}':
            network.connect('{1}')
    else:
        network.connect('{1}')
    accounts.load("{2}", password='{3}')
    token = {4}.deploy({5}, publish_source=True)
    var = ContextVar('token')
    var.set(token)
'''.format(
            contract_name,
            network,
            account_name,
            account_pass,
            contract_name,
            '{\'from\': accounts[0]}',
            contract_name,
        )
        return script

    def _get_contract_deploy_with_constructor_script_code(
            self,
            contract_name: str,
            network: str,
            account_name: str,
            account_pass: str,
            constructor_params: List,
    ) -> str:
        """
        Creates script code for contract with constructor and
        returns it

        :param contract_name: Contract name which will be used in deployment script
        :param network: Network where contract will be deployed
        :param account_name: The name of the account that will be used when deploying contracts
        :param account_pass: The name of the account that will be used when deploying contracts
        :param constructor_params: List of contract constructor parameters

        :return: Scripts code for contract deployment script.py
        """
        script = '''
from brownie import {0}, accounts
from brownie import network
from contextvars import ContextVar


def main():
    if network.is_connected():
        if not network.show_active() == '{1}':
            network.connect('{1}')
    else:
        network.connect('{1}')
    accounts.load("{2}", password='{3}')
    token = {4}.deploy({5}, {6}, publish_source=True)
    var = ContextVar('token')
    var.set(token)
'''.format(
            contract_name,
            network,
            account_name,
            account_pass,
            contract_name,
            ','.join(constructor_params),
            '{\'from\': accounts[0]}',
        )
        return script

    def _create_script_for_deploy(
            self,
            project_dir: Path,
            contract_name: str,
            network: str,
            account_name: str,
            account_pass: str,
            constructor_params: List = None,
    ) -> str:
        """
        Creates .py file with script for deploy and returns its path as str

        :param project_dir: tmp brownie project directory
        :param contract_name: Contract name which will be used in deployment script
        :param network: Network where contract will be deployed
        :param account_name: The name of the account that will be used when deploying contracts
        :param account_pass: The name of the account that will be used when deploying contracts
        :param constructor_params: List of contract constructor parameters

        :return: Path to the deployments script in tmp brownie project
        """

        if constructor_params:
            contract_deploy_script_code = self._get_contract_deploy_with_constructor_script_code(
                contract_name,
                network,
                account_name,
                account_pass,
                constructor_params,
            )
        else:
            contract_deploy_script_code = self._get_contract_deploy_script_code(
                contract_name,
                network,
                account_name,
                account_pass,
            )

        with open(f'{project_dir}/scripts/main.py', "w") as new_token:
            new_token.write(contract_deploy_script_code)

        return str(Path(f'{project_dir}/scripts/main.py'))

    def _add_new_account_to_project(self, private_key: str, name: str, password: str) -> None:
        """
        Adds new account to the project. If account already exists
        does nothing and returns

        Brownie stores account data in the dir ~/.brownie/accounts/

        :param private_key: The private of the account that will be used when deploying contracts
        :param name: The name of the account that will be used when deploying contracts
        :param password: The name of the account that will be used when deploying contracts
        """
        try:
            a = accounts.add(private_key)
            a.save(name, password=password)
        except FileExistsError:
            return
        except Exception as e:
            raise DeployError(ErrorCodes.CANNOT_CREATE_ACCOUNT, exception=e)

    def _create_token_file(self, project_dir: Path, contract_code: str) -> None:
        """
        Creates file with contract code in the project directory

        :param project_dir: tmp brownie project directory
        :param contract_code: Full smart contract code
        """
        with open(f'{project_dir}/contracts/token.sol', "w") as new_token:
            new_token.write(contract_code)

    def _set_provider_if_need(self, provider: str, provider_id: str) -> None:
        """
        Adds provider for Ethereum to the environment variables,
        raise Error if there is _provider but not _provider_id

        :param provider: Provider to use if network needs provider
        :param provider_id: Provider ID
        """
        if provider:
            if provider_id:
                os.environ[f'{provider}'] = f'{provider_id}'
            else:
                raise DeployError(ErrorCodes.HAVE_PROVIDER_BUT_NOT_PROVIDER_ID)

    def _get_token_variable_from_context(self) -> str:
        """
        Loads context and returns token from deployer script. Raise exception if
        token_var is not ProjectContract

        :return: Token contract address
        """
        token_var = None
        ctx: Context = copy_context()
        for key, value in list(ctx.items()):
            if key.name == 'token':
                token_var = key.get('token')

        if isinstance(token_var, ProjectContract):
            return str(token_var)
        elif isinstance(token_var, TransactionReceipt):
            raise DeployError(ErrorCodes.CONTRACT_SELF_DESTRUCTED_GOT_TRANSACTION_RECEIPT, transaction=token_var)
        elif token_var is None:
            raise DeployError(ErrorCodes.CONTRACT_NOT_DEPLOYED_TRANSACTION_NOT_RECEIVED)

    def _create_project_config_file(self, project_dir: Path, config: Union[Config, None]) -> None:
        """
        Creates brownie configuration file in the project directory

        :param project_dir: tmp brownie project directory
        :param config: Dataclass with all configurations for brownie projects
        """
        if config:
            config_dict = asdict(config)
        else:
            return

        with open(f'{project_dir}/brownie-config.yaml', "w") as config_file:
            yaml.dump(config_dict, config_file)

    def _set_etherscan_api_token(self, etherscan_api_token: str) -> None:
        """
        Adds etherscan api token for contract code verification to
        the environment variables

        :param etherscan_api_token: Developer Etherscan API token
        """
        os.environ['ETHERSCAN_TOKEN'] = etherscan_api_token
