
#create a random password after google signup
def createRndmPassword():
    import random
    import string
    # generate a random password 10 zeichen lang mit zahlen und buchstaben
    password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
    return password