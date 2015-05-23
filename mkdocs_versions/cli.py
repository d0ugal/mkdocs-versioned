import os

import click
from git import Git
import logging

from mkdocs import build, cli, config

log = logging.getLogger('mkdocs.cli')


def _build(cfg, pathspec, output):

    try:
        cfg.load_dict({'site_dir': output})
        build.build(cfg, clean_site_dir=True)
    except Exception:
        log.exception("Failed to build '%s'", pathspec)


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

    cfg = config.load_config(
        config_file=config_file,
        strict=strict,
        site_dir=site_dir
    )

    initial_site_dir = cfg['site_dir']

    log.info("Building %s to /", default)
    g.checkout(default)
    _build(cfg, default, initial_site_dir)

    log.info("Building %s to /latest", latest)
    g.checkout(default)
    _build(cfg, latest, os.path.join(initial_site_dir, 'latest'))

    for tag in sorted(tags):

        g.checkout(tag)

        if not os.path.exists("mkdocs.yml"):
            log.warning("Unable to build %s, as no mkdocs.yml was found", tag)
            continue

        out = "v{0}".format(tag)
        log.info("Building %s to /%s", tag, out)
        _build(cfg, tag, os.path.join(initial_site_dir, out))

    g.checkout('master')
