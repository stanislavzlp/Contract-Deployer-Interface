from dataclasses import dataclass
from typing import Union


@dataclass(order=True)
class ProjectStructure:
    """
    Project structure dataclass
    """
    build: str = 'build'
    contracts: str = 'contracts'
    interfaces: str = 'interfaces'
    reports: str = 'reports'
    scripts: str = 'scripts'
    tests: str = 'tests'


@dataclass(order=True)
class Development:
    gas_limit: Union[str, int] = 'max'
    gas_buffer: Union[int, float] = 1
    gas_price: Union[str, int] = 0
    max_fee: Union[None, int] = None
    priority_fee: Union[None, int] = None
    reverting_tx_gas_limit: str = 'max'
    default_contract_owner: bool = True
    cmd_settings: bool = False


# Нужен ли в принципе Development?
# Надо ли создать отдельный класс под cmd_setting? Будут ли они в принципе использоваться

@dataclass(order=True)
class Live:
    gas_limit: Union[str, int] = 'auto'
    gas_buffer: Union[int, float] = 1.1
    gas_price: Union[str, int] = 'auto'
    max_fee: Union[None, int] = None
    priority_fee: Union[None, int] = None
    reverting_tx_gas_limit: bool = False
    default_contract_owner: bool = False


@dataclass(order=True)
class Networks:
    """
    Network dataclass
    """
    default: str = 'development'
    development: Development = Development()
    live: Live = Live()


@dataclass(order=True)
class Optimizer:
    enabled: bool = True
    runs: int = 200


@dataclass(order=True)
class Solc:
    version: Union[None, int] = None
    optimizer: Optimizer = Optimizer()
    remappings: bool = False


@dataclass(order=True)
class Vyper:
    version: Union[None, int] = None


@dataclass(order=True)
class Compiler:
    evm_version: Union[None, int] = None
    solc: Solc = Solc()
    vyper: Vyper = Vyper()


@dataclass(order=True)
class Console:
    show_colors: bool = True
    color_style: str = 'monokai'
    auto_suggest: bool = True
    completions: bool = True
    editing_mode: str = 'emacs'


@dataclass(order=True)
class Reports:
    exclude_paths: bool = False
    exclude_contracts: bool = False
    only_include_project: bool = True


@dataclass(order=True)
class Phases:
    explicit: bool = True
    reuse: bool = True
    generate: bool = True
    target: bool = True
    shrink: bool = True


@dataclass(order=True)
class Hypothesis:
    deadline: bool = False
    max_examples: int = 50
    report_multiple_bugs: bool = False
    stateful_step_count: int = 10
    phases: Phases = Phases()


@dataclass(order=True)
class Config:
    """
    Config dataclass
    """
    project_structure: ProjectStructure = ProjectStructure()
    networks: Networks = Networks()
    compiler: Compiler = Compiler()
    console: Console = Console()
    reports: Reports = Reports()
    hypothesis: Hypothesis = Hypothesis()
    autofetch_sources: bool = False
    dependencies: bool = False
    dev_deployment_artifacts: bool = False
    dotenv: str = '.env'
