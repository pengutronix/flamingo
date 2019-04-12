import shutil
import os


def mkdir_p(context, path, logger=None):
    logger = logger or context.logger
    dirname = os.path.dirname(path)

    if not os.path.exists(dirname):
        logger.debug('mkdir -p %s', dirname)
        os.makedirs(dirname)


def rm_rf(context, path, logger=None):
    logger = logger or context.logger

    logger.debug('rm -rf %s', context.settings.OUTPUT_ROOT)
    shutil.rmtree(path)


def cp(context, source, destination, mkdir_p=mkdir_p, logger=None):
    logger = logger or context.logger

    mkdir_p(context, destination, logger=logger)
    logger.debug('cp %s %s', source, destination)
    shutil.copy(source, destination)


def ln_s(context, source, destination, mkdir_p=mkdir_p, logger=None):
    logger = logger or context.logger

    mkdir_p(context, destination, logger=logger)
    source = os.path.abspath(source)
    logger.debug('ln -s %s %s', source, destination)

    try:
        os.symlink(source, destination)

    except FileExistsError:
        pass
