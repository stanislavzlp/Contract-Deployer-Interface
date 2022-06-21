# Contract-Deployer-Interface

## About project
This project is inner project of MyWish team which focused on python interface realization to deploy contracts
in ethereum-like blockchains.

## Install project
To install mywish-deployer use pip
```bash 
pip install mywish-deployer
```

## Brownie deployer
On version 0.3.0 this project supports contract deploy using brownie project. In normal case to deploy contract
using brownie user need to use brownie-cli. Brownie deployer interacts with inner parts of brownie and provide
opportunity to deploy contracts directly from python scripts.

## How to use Brownie deployer

At first import Brownie deployer
```python
from mywish import BrownieDeployer
```

Initialize brownie deployer
```python
brownie_deployer = BrownieDeployer()
```

Deploy contract with all required arguments
```python
contract = brownie_deployer.deploy(
    contract_code=contract_code,
    account_name='some_key',
    account_pass='some_pass',
    private_key='private_key',
    network='network_name',
    contract_name='some_name',
    etherscan_api_token='some_token',
    provider='network_provider',
    provider_id='provider_id',
)
```

```contract_code: Full smart contract code```

```account_name: The name of the account that will be used when deploying contracts```

```account_pass: The name of the account that will be used when deploying contracts```

`private_key: The private of the account that will be used when deploying contracts`

`network: Network where contract will be deployed`

`contract_name: Contract name which will be used in deployment script`

`etherscan_api_token: Developer Etherscan API token`

`provider: Provider to use if network needs provider`

`provider_id: Provider ID`

`constructor_params: Params which will be used in contract deployment`

`config: Dataclass with all configurations for brownie projects`

Method deploy will return `Deployed contract address`

WARNING! All params in constructor_params must be provided as strings for future formatting. But arguments
which must be strings in params of constructor must be surrounded by double quotes. Like this:
```python
constructor_params = ['\'{some_address}\'']
```

For now brownie deployer is useful only for Ethereum network. In future, we will add support of others networks.

## IDeployer interface
IDeployer is abstract model with one method "deploy" which used in different deployers.