import os

import click
from git import Git
import logging

from mkdocs import build, cli, config

log = logging.getLogger('mkdocs.cli')


@click.command()
@click.option('--config-file', type=click.File('rb'), help=cli.config_file_help)
@click.option('--strict', is_flag=True, help=cli.strict_help)
@click.option('--site-dir', type=click.Path(), help=cli.site_dir_help)
@click.option('--tags', '-t', multiple=True)
@click.option('--default', '-d', default='master')
@click.option('--latest', '-l', default='master')
def build_command(config_file, strict, site_dir, tags, default, latest):
    """Build the MkDocs documentation"""

    cli.configure_logging()

    g = Git()
    tags = tags or g.tag().splitlines()
    g.checkout(default)
    clean = True

    cfg = config.load_config(
        config_file=config_file,
        strict=strict,
        site_dir=site_dir
    )

    initial_site_dir = cfg['site_dir']

    log.info("Building branch %s to %s", default, initial_site_dir)

    try:
        build.build(cfg, clean_site_dir=clean)
    except Exception:
        log.exception("Failed to build branch %s", default)

    for tag in tags:
        g.checkout(tag)

        if not os.path.exists("mkdocs.yml"):
            log.warning(
                "Unable to build branch %s, as no mkdocs.yml was found", tag)
            continue

        output = os.path.join(initial_site_dir, "v{0}".format(tag))
        log.info("Building branch %s to %s", tag, output)
        cfg.load_dict({'site_dir': output})
        try:
            build.build(cfg, clean_site_dir=clean)
        except Exception:
            log.exception("Failed to build branch %s", tag)

    git.checkout('master')
