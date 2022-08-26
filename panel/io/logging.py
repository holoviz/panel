import logging
import sys

LOG_FORMAT = '%(asctime)s %(levelname)s: %(name)s - %(message)s'

LOG_PERIODIC_START = 'Session %s executing periodic callback %r (%d)'
LOG_PERIODIC_END = 'Session %s finished executing periodic callback %r (%d)'
LOG_USER_MSG = 'Session %s logged "{msg}"'
LOG_SESSION_CREATED = 'Session %s created'
LOG_SESSION_DESTROYED = 'Session %s destroyed'
LOG_SESSION_LAUNCHING = 'Session %s launching'
LOG_SESSION_RENDERED = 'Session %s rendered'

# Set up logger
panel_logger = logging.getLogger('panel')
panel_logger.setLevel(logging.DEBUG)
panel_logger.handlers.clear()
panel_logger.propagate = False

# Set up default log handler
panel_log_handler = logging.StreamHandler()
panel_log_handler.setStream(sys.stdout)
panel_logger.addHandler(panel_log_handler)
formatter = logging.Formatter(fmt=LOG_FORMAT)
panel_log_handler.setFormatter(formatter)
