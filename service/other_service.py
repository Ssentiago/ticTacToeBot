async def get_the_pair(pool: dict, id):
    for pair in pool['pairs']:
        if id in pair:
            return pair
