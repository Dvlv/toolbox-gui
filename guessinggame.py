import random 

def main():
    while 1:
        target = random.randint(1,100)
        print("I'm thinking of a number between 1 and 100")

        found = False
        while not found:
            guess = get_guess()

            if guess == target:
                print("U win!")
                found = True
            elif guess < target:
                print("Higher")
            else:
                print("Lower")

def get_guess():
    guess = input("Guess: ")
    guess = int(guess)

    return guess


if __name__ == "__main__":
    main()
