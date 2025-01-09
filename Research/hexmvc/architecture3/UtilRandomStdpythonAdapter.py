import secrets


def RandomIntFunction(n, m):
    print("python random")
    return secrets.SystemRandom().randint(n, m)
