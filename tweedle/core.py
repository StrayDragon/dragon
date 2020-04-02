__all__ = ["cli"]

import logging
import os
from pathlib import Path

import attr
import click
from box import Box

from tweedle import PROJECT_NAME, __version__
from tweedle.util import clickx, fs

logging.basicConfig()
logger = logging.getLogger(__name__)


class RawTypeSerializationMixin:
    def as_raw_dict(self, filter=None) -> dict:
        """
        Convert attr.s obj to dict with raw type (serializatable type)

        `pathlib.Path` is very convenient, I don't want to use `str` with old `os.path`,
        Of course, because `Path` is a normal object,
        `attrs` asdict will not make a convert(from `Path` to `str`, ...),
        but in order to let serialize to json|yaml|toml as espected, this fn will do these:

        - `pathlib.Path` -> `str`

        :param filter attr.filters.<fn> or Callable: filter callback
        :rtype dict: raw type dict
        """
        kv: dict = attr.asdict(self, filter=filter)
        will_convert_to_str = []
        for k, v in kv.items():
            if isinstance(v, Path):
                will_convert_to_str.append(k)
        for k in will_convert_to_str:
            kv[k] = str(kv[k])
        return kv


@attr.s
class Tweedle(RawTypeSerializationMixin):
    """Read and mapping initialize info to ctx"""
    app_home_path: Path = attr.ib()

    @classmethod
    def init(
        cls,
        generate_default_config=False,
        dev=os.environ.get(f'{PROJECT_NAME}_DEV_FLAG', False),
        dev_prefix=os.environ.get(f'{PROJECT_NAME}_DEV_DIR_PREFIX', None),
    ):
        default_app_home_path = fs.get_default_app_dir(
            name=PROJECT_NAME,
            dev=dev,
            dev_prefix=dev_prefix,
        )
        o = cls(app_home_path=default_app_home_path)
        config_path: Path = default_app_home_path / 'rc.toml'
        if config_path.exists():
            box = Box.from_toml(filename=str(config_path))
            for k, v in box.items():
                converter = getattr(attr.fields(Tweedle), k).type
                setattr(o, k, converter(v))
        if generate_default_config:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch(exist_ok=True)
            self = attr.fields(Tweedle)
            # kv = attr.asdict(
            #     o,
            #     filter=attr.filters.exclude(self.app_home_path),
            # )
            kv = o.as_raw_dict(filter=attr.filters.exclude(self.app_home_path))
            Box(**kv).to_toml(filename=str(config_path), encoding='utf-8')
        return o


@clickx.with_plugins(f'{PROJECT_NAME.lower()}.plugins')
@click.group(f'{PROJECT_NAME.lower()}')
@click.version_option(help='show version details', version=__version__)
@clickx.option_of_common_help
@click.pass_context
def cli(ctx):
    """
    Welcome to use tweedle, enjoy it and be efficient :P\n
    Please use "tweedle COMMAND --help" to get more detail of usages
    """
    # if verbose:
    #     logger.setLevel(logging.INFO)
    # else:
    #     logger.setLevel(logging.CRITICAL)
    # ctx.obj.flag_debug = False

    logger.info(f'{PROJECT_NAME} starting')
    # logger.error(f'[ERROR] {PROJECT_NAME} get error')
    # logger.debug(f'[DEBUG] {PROJECT_NAME} get debug')
    # logger.warning(f'[WARNING] {PROJECT_NAME} get warning')
    # logger.critical(f'[!!!] {PROJECT_NAME} get critical')
    logger.info(f'check tweedle obj: {ctx.obj}')
    logger.debug(f'check tweedle self.asdict {ctx.obj.as_raw_dict()}')
    pass


def main():
    from tweedle.cmd import manage, project
    cli.add_command(manage.cli)
    cli.add_command(project.cli)
    cli(
        auto_envvar_prefix=PROJECT_NAME,
        obj=Tweedle.init(generate_default_config=True),
    )
