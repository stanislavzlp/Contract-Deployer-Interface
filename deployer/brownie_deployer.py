import os
from contextvars import Context, copy_context
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Union

import yaml
from brownie import accounts
from brownie.network.contract import ContractContainer, ProjectContract
from brownie.network.transaction import TransactionReceipt
from brownie.project.main import Project, new
from brownie.project import run

from deployer.common_dataclasses import Config
from deployer.exeptions import DeployError, ErrorCodes
from deployer.interface import IDeployer


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
            provider: str = None,
            provider_id: str = None,
            constructor_parasms: List[str] = None,
            config: Config = None,
    ) -> ProjectContract:
        """
        Creates user if needed, create project, compile contract code and deploy

        param: str contract_code: Full smart contract code
        param: str account_name: The name of the account that will be used when deploying contracts
        param: str account_pass: The name of the account that will be used when deploying contracts
        param: str private_key: The private of the account that will be used when deploying contracts
        param: str network: Network
        param: str contract_name:
        param: str provider:
        param: str provider_id:
        param: str constructor_parasms:
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
                constructor_parasms,
            )

            self._set_provider_if_need(provider, provider_id)

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
    ):
        """
        Creates script code for contract without constructor and
        returns it
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
    token = {4}.deploy({5})
    var = ContextVar('token')
    var.set(token)
'''.format(
            contract_name,
            network,
            account_name,
            account_pass,
            contract_name,
            '{\'from\': accounts[0]}'
        )
        return script

    def _get_contract_deploy_with_constructor_script_code(
            self,
            contract_name: str,
            network: str,
            account_name: str,
            account_pass: str,
            constructor_parasms: List,
    ) -> str:
        """
        Creates script code for contract with constructor and
        returns it
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
    token = {4}.deploy({5}, {6})
    var = ContextVar('token')
    var.set(token)
'''.format(
            contract_name,
            network,
            account_name,
            account_pass,
            contract_name,
            ','.join(constructor_parasms),
            '{\'from\': accounts[0]}'
        )
        return script

    def _create_script_for_deploy(
            self,
            project_dir: Path,
            contract_name: str,
            network: str,
            account_name: str,
            account_pass: str,
            constructor_parasms: List = None,
    ) -> str:
        """
        Creates .py file with script for deploy and returns its path as str
        """

        if constructor_parasms:
            contract_deploy_script_code = self._get_contract_deploy_with_constructor_script_code(
                contract_name,
                network,
                account_name,
                account_pass,
                constructor_parasms,
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
        """
        with open(f'{project_dir}/contracts/token.sol', "w") as new_token:
            new_token.write(contract_code)

    def _set_provider_if_need(self, provider: str, provider_id: str) -> None:
        """
        Adds provider for Ethereum to the environment variables,
        raise Error if there is _provider but not _provider_id
        """
        if provider:
            if provider_id:
                os.environ[f'{provider}'] = f'{provider_id}'
            else:
                raise DeployError(ErrorCodes.HAVE_PROVIDER_BUT_NOT_PROVIDER_ID)

    def _get_token_variable_from_context(self) -> str:
        """
        Loads context and returns token from deployer script.
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
        """
        if config:
            config_dict = asdict(config)
        else:
            return

        with open(f'{project_dir}/brownie-config.yaml', "w") as config_file:
            yaml.dump(config_dict, config_file)
