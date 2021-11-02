import random


def random_str(min_length, max_length):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    return ''.join(random.choice(alphabet + numbers) for _ in range(random.randint(min_length, max_length)))
