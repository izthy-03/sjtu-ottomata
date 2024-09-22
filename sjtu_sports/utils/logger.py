import logging


def get_logger(
    name: str,
    log_file_path: str = None,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(name)s] %(asctime)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s"
    )

    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger