"""
Documentation 
"""


import json
import os

from tempfile import TemporaryDirectory
from typing import List
from brownie.project.main import Project, new
from brownie.project import run
from pathlib import Path
from brownie import accounts


class BrownieAdapter:
    """Brownie Adapter class for interaction with
    brownie

    TODO params documentation 
    """

    def __init__(
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
    ) -> None:
        self._contract_code = contract_code
        self._account_name = account_name
        self._account_pass = account_pass
        self._private_key = private_key
        self._network = network
        self._contract_name = contract_name
        self._provider = provider
        self._provider_id = provider_id
        self._project_dir = None
        self._constructor_parasms = constructor_parasms



    def deploy(
        self,
    ):
        """Creates tmp structured brownie project for futher 
        contract compiling etc
        """
        with TemporaryDirectory() as tmp_dir:

            self._project_dir = Path(tmp_dir)
            
            new(self._project_dir)
            
            self.create_token_file()
            
            # TODO название brownie проекта
            project = Project('test', self._project_dir)
            
            script_path = self.create_script_for_deploy()
            
            self.set_provider_if_need()
            
            # try:
            run(script_path=script_path, project=self._project_dir, )
            # except ValueError:
                # print('ValueError')

    def get_contract_deploy_script_code(self):
        """tmp container with script code in str
        """
        script = '''
from brownie import {0}, accounts
from brownie import network

def main():
    network.connect('{1}')
    accounts.load("{2}", password='{3}')
    {4}.deploy({5})
'''.format(
    self._contract_name, 
    self._network, 
    self._account_name, 
    self._account_pass,
    self._contract_name, 
    '{\'from\': accounts[0]}'
    )
        return script


    def get_contract_deploy_with_constructor_script_code(self):
        """tmp container with script code in str
        """
        for ii in self._constructor_parasms:
            print(ii)
        script = '''
from brownie import {0}, accounts
from brownie import network

def main():
    network.connect('{1}')
    accounts.load("{2}", password='{3}')
    {4}.deploy({5}, {6})
'''.format(
    self._contract_name, 
    self._network, 
    self._account_name, 
    self._account_pass,
    self._contract_name, 
    ','.join(self._constructor_parasms),
    '{\'from\': accounts[0]}'
    )
        # print(script)
        return script


    def create_script_for_deploy(self):
        """Creates .py file with script for deploy and returns str path
        """
        
        if self._constructor_parasms:
            contract_deploy_script_code = self.get_contract_deploy_with_constructor_script_code()
        else:
            contract_deploy_script_code = self.get_contract_deploy_script_code()

        with open(f'{self._project_dir}/scripts/main.py', "w") as new_token:
            new_token.write(contract_deploy_script_code)

        return str(Path(f'{self._project_dir}/scripts/main.py'))


    def add_new_account_to_project(cls, private_key, id_, password):
        try:
            a = accounts.add(private_key)
            a.save(id_, password=password)
        except FileExistsError:
            return

    def create_token_file(self):
        """Creates file with contract code in the project directory
        """
        with open(f'{self._project_dir}/contracts/token.sol', "w") as new_token:
                new_token.write(self._contract_code)

    def set_provider_if_need(self):
        """Adds provider for Etherium to the environment variables
        """
        if self._provider:
            if self._provider_id:
                os.environ[f'{self._provider}'] = f'{self._provider_id}'
            else:
                raise ValueError('Got provider without provider id')


class IContractDeployer:
    """Class - Interface for contract deployment"""
    @classmethod
    def deploy(
        self,
        contract_code: str,
        account_name: str = 'test_key',
        account_pass_tmp: str = 'test_password',
        private_key: str = None,
        network: str = None,
        contract_name: str = None,
        provider: str = None,
        provider_id: str = None,
        constructor_parasms: List[str] = None,
        ) -> None:
        
        # TODO Добавить проверку на сеть. Если сеть относится 
        # к одной из тех, что нуждаются в провайдере типа инфуры
        # то сразу возвращать ошибку

        brownie_adapter_instance = BrownieAdapter(
            contract_code,
            account_name,
            account_pass_tmp,
            private_key,
            network,
            contract_name,
            provider,
            provider_id,
            constructor_parasms,
        )

        brownie_adapter_instance.deploy()


with open('./prototypo/token.sol', 'r') as token:
    contract_code = token.read()


IContractDeployer.deploy(
        contract_code,
        account_name='test_key',
        account_pass_tmp='test_password',
        private_key='4032f47f29507528bd171c392bcb1345d67598001cbbc3b379650e7631774bc2',
        network='ropsten',
        contract_name='MainToken',
        provider='WEB3_INFURA_PROJECT_ID',
        provider_id='2b6b5110453a418ea4f58c3c66e0902a',
    )

with open('./prototypo/swap_bridge.sol', 'r') as token:
    contract_code = token.read()

IContractDeployer.deploy(
        contract_code,
        account_name='test_key',
        account_pass_tmp='test_password',
        private_key='4032f47f29507528bd171c392bcb1345d67598001cbbc3b379650e7631774bc2',
        network='ropsten',
        contract_name='SwapContract',
        provider='WEB3_INFURA_PROJECT_ID',
        provider_id='2b6b5110453a418ea4f58c3c66e0902a',
        constructor_parasms=[
            '\'0xd77accd3d4296cda9ff48f5a5c4b652f63f211e3\'',
            '\'0x986c3298d8a302fd854c8e40e1973fb78c7eba56\'',
            '3',
            '[1, 2]',
            '2',
            '0',
            '10000000000',
            '130000000000',
            '5'
        ]
    )