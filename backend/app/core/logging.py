import logging


def setup_loggin(level_info : str = "INFO") -> None:
     numeric_level = getattr(logging, level_info.upper(), logging.INFO)
     logging.basicConfig(
                    level= numeric_level,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")