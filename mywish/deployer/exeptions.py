from typing import TypeVar, Generic

from enum import Enum


T = TypeVar('T', bound=Enum)


class Error(BaseException, Generic[T]):
    code: T
    data: any

    def __init__(self, code: T, **data: any):
        self.code = code
        self.data = data

    def __str__(self):
        result = []
        for name, value in self.data.items():
            if name.startswith('_'):
                continue
            result.append(f'{name}={value}')
        result = ', '.join(result)
        return f'{self.__class__.__name__}({self.code.value})[{result}]'


class ErrorCodes(Enum):
    HAVE_PROVIDER_BUT_NOT_PROVIDER_ID = 'HAVE_PROVIDER_BUT_NOT_PROVIDER_ID'
    CANNOT_CREATE_NEW_PROJECT = 'CANNOT_CREATE_NEW_PROJECT'
    CANNOT_DEPLOY_CONTRACT = 'CANNOT_DEPLOY_CONTRACT'
    CONTRACT_SELF_DESTRUCTED_GOT_TRANSACTION_RECEIPT = 'CONTRACT_SELF_DESTRUCTED_GOT_TRANSACTION_RECEIPT'
    CONTRACT_NOT_DEPLOYED_TRANSACTION_NOT_RECEIVED = 'CONTRACT_NOT_DEPLOYED_TRANSACTION_NOT_RECEIVED'
    CANNOT_CREATE_ACCOUNT = 'CANNOT_CREATE_ACCOUNT'


class DeployError(Error[ErrorCodes]):
    """
    Ошибки деплоя контрактов
    """
