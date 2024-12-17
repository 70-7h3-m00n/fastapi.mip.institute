import logging
import os


def setup_logger(log_file_name='app.log', log_folder='logs'):
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_file_path = os.path.join(log_folder, log_file_name)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, mode='a'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    return logger


logger = setup_logger()
