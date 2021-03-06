from collections import OrderedDict, namedtuple
from pathlib import Path
from typing import Dict
import yaml
from . import create_logger

logger = create_logger(__name__)


DataSource = namedtuple('DataSource', ['name', 'path', 'file_type', 'strand'])


class AnalysisInfo:
    def __init__(self, job_dir):
        self.result_root = Path(job_dir).resolve()

        yaml_pth = self.result_root / 'analysis_info.yaml'
        logger.debug(
            'Reading analysis info from {:s}'.format(yaml_pth.as_posix())
        )
        with yaml_pth.open() as f:
            self._raw = yaml.load(f)

        self.data_sources = self.parse_data_sources()
        self.conditions = self.parse_conditions()
        self.parameters = self.parse_parameters()
        samples = OrderedDict()
        for condition_samples in self.conditions.values():
            samples.update(condition_samples)
        self.samples = samples

    def parse_data_sources(self) -> Dict[str, DataSource]:
        data_sources = OrderedDict()
        for data_source in self._raw['data_sources']:
            name, info = next(iter(data_source.items()))
            # Ensure it doesnt contain any path
            name = Path(name).name
            data_sources[name] = (
                DataSource(name, info['path'], info['type'], info['strand'])
            )
        return data_sources

    def parse_conditions(self) -> Dict[str, Dict]:
        conditions = OrderedDict()
        for condition in self._raw['conditions']:
            condition_name, samples = next(iter(condition.items()))
            condition_samples = OrderedDict()
            for sample in samples:
                condition_samples.update(sample)
            conditions[condition_name] = condition_samples
        return conditions

    def parse_parameters(self):
        parameters = {}
        for param_name, param_val in self._raw['parameters'].items():
            parameters[param_name] = param_val
        return parameters
