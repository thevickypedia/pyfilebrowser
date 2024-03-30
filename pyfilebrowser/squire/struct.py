import logging
from typing import Any, Dict, List, Tuple


class LoggerConfig:
    """Creates a dictionary of the given logger's configuration.

    >>> LoggerConfig

    """

    def __init__(self, logger: logging.Logger):
        """Instantiates the object.

        Args:
            logger: Custom logger.
        """
        self.logger = logger
        self.base_level = "INFO" if logger.level == "NOT_SET" else logger.level

    def extract(self) -> Tuple[dict, dict]:
        """Extracts the handlers and formatters.

        Returns:
            Tuple[dict, dict]:
            Returns a tuple of handlers and formatters, each as dictionary representation.
        """
        handlers = {}
        formatters = {'standard': {}}
        for handler in self.logger.handlers:
            formatter = handler.formatter
            formatters['standard']['format'] = formatter.__dict__.get(
                '_fmt', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            if formatter.datefmt:
                formatters['standard']['datefmt'] = formatter.datefmt
            if formatter.converter:
                formatters['standard']['converter'] = formatter.converter
            handler_format = {
                'class': f"logging.{handler.__class__.__name__}",
                'formatter': 'standard',
                'level': self.base_level,
            }
            if hasattr(handler, "baseFilename"):
                handler_format['filename'] = handler.baseFilename
                name = "file"
            else:
                name = "console"
            handlers[name] = handler_format
        return handlers, formatters

    def get(self) -> Dict[str, dict | int | Dict[str, Dict[str, str | int | bool | List[str]]]]:
        """Returns logger's full configuration which can be re-used to create new logger objects with the same config.

        Returns:
            Dict[str, dict | int | Dict[str, Dict[str, str | int | bool | List[str]]]]:
            Returns the log configration.
        """
        handlers, formatters = self.extract()
        logging_config = {
            'version': 1,
            'formatters': formatters,
            'handlers': handlers,
            'loggers': {
                'proxy': {
                    'handlers': list(handlers.keys()),
                    'level': self.base_level,
                    'propagate': True
                }
            }
        }
        return logging_config


def update_log_level(data: dict, new_value: Any) -> dict:
    """Recursively update the value where any key equals "level", for loggers and handlers.

    Parameters:
        data: The nested dictionary to traverse.
        new_value: The new value to set where the key equals "level".

    Returns:
        dict:
        The updated nested dictionary.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = update_log_level(value, new_value)
        elif key == "level":
            data[key] = new_value
    return data
