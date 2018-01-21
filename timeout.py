import time
from logger import logger


def timeout_occurred(timeout_in_seconds, timeout_start):
    if timeout_in_seconds != 0:
        if timeout_start is None:
            timeout_start = time.time()
        elapsed_time = time.time() - timeout_start
        if elapsed_time >= timeout_in_seconds:
            log_message = "scheduled timeout occurred after {0} seconds".format(str(int(elapsed_time)))
            logger.warning(log_message)
            return True
    return None
