"""
This modules contains helping functionalities for setting up logging mechanism
"""


def setup_logging(name, filename, max_file_size, backup_files):
    """
    This function sets up logging for class
    :param name: name of the module calling logging setup function
    :param filename: filename for storing log information
    :param max_file_size: maximum size of log file.
    :param backup_files: number of backup files.
    :return:
    """
    import os
    import logging
    from logging.handlers import RotatingFileHandler

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    log_format = logging.Formatter('%(asctime)s - %(name)s '
                                   '%(levelname)s - %(message)s')

    if not os.path.exists(path=filename):
        superMakedirs('/'.join(filename.split('/')[:-1]), 775)

    log_fh = RotatingFileHandler(filename,
                                 maxBytes=max_file_size,
                                 backupCount=backup_files)
    log_fh.setLevel(logging.INFO)
    log_fh.setFormatter(log_format)

    # Set up stream handler for important logs
    log_stream = logging.StreamHandler()
    log_stream.setLevel(logging.ERROR)

    # Add handlers
    logger.addHandler(log_fh)
    logger.addHandler(log_stream)

    return logger


def super_make_dirs(path, mode):
    """
    Make directories recursively with specific permissions
    :param path: path to be created
    :param mode: permissions for the directory
    :return:
    """
    import os
    if not path or os.path.exists(path):
        return []
    (head, tail) = os.path.split(path)
    res = super_make_dirs(head, mode)
    os.mkdir(path)
    os.chmod(path, mode)
    res += [path]
    return res
