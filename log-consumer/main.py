import redis

redis_instance = redis.Redis(decode_responses=True)
pubsub = redis_instance.pubsub()

pubsub.subscribe("logs")
for message in pubsub.listen():
    # Do anything with the received messages
    print(message["data"], flush=True)
