import os
from pathlib import Path
import dotenv

from mywish import BrownieDeployer

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

brownie_deployer = BrownieDeployer()

with open('./token.sol', 'r') as token:
    contract_code = token.read()

contract = brownie_deployer.deploy(
    contract_code,
    account_name='test_key',
    account_pass='test_password',
    private_key=os.environ['PRIVATE_KEY'],
    network='ropsten',
    contract_name='MainToken',
    etherscan_api_token=os.environ['ETHERSCAN_API_TOKEN'],
    provider='WEB3_INFURA_PROJECT_ID',
    provider_id=os.environ['PROVIDER_ID'],
)

with open('./swap_bridge.sol', 'r') as token:
    contract_code = token.read()

print(contract)

swap_contract = brownie_deployer.deploy(
    contract_code,
    account_name='test_key',
    account_pass='test_password',
    private_key=os.environ['PRIVATE_KEY'],
    network='ropsten',
    contract_name='SwapContract',
    etherscan_api_token=os.environ['ETHERSCAN_API_TOKEN'],
    provider='WEB3_INFURA_PROJECT_ID',
    provider_id=os.environ['PROVIDER_ID'],
    constructor_params=[
        # Тут вопрос относительно этих параметров. Они подаются без скобок, если не прописать их вот таким образом
        f'\'{contract}\'',
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

print(swap_contract)

with open('./token.sol', 'r') as token:
    contract_code = token.read()

contract = brownie_deployer.deploy(
    contract_code,
    account_name='test_key',
    account_pass='test_password',
    private_key=os.environ['PRIVATE_KEY'],
    network='ropsten',
    etherscan_api_token=os.environ['ETHERSCAN_API_TOKEN'],
    contract_name='MainToken',
    provider='WEB3_INFURA_PROJECT_ID',
    provider_id=os.environ['PROVIDER_ID'],
)
