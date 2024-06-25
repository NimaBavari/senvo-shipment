import logging

import redis


class RedisHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

    def emit(self, record):
        try:
            message = self.format(record)
            self.redis_client.publish("logs", message)
        except Exception:
            self.handleError(record)


def setup_logger():
    logger = logging.getLogger("redisLogger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    redis_handler = RedisHandler()
    redis_handler.setFormatter(formatter)
    logger.addHandler(redis_handler)
    return logger
