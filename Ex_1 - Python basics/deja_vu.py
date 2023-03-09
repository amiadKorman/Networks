NUMBER_OF_DIGITS = 5


def is_n_digit(number):
    """
    Return if number is with exactly n digits or not
    Args:
         number - a string
    """
    if number.isdigit() and len(number) == NUMBER_OF_DIGITS:
        return True
    else:
        return False


def digits_separate(number):
    """Return the digits of the number, separated with comma
        ARGS:
            number - a string
    """
    return ','.join(number)


def digits_sum(number):
    """ Return the sum of the digits of the number
    Args:
        number - a string
    """
    sum_digits = 0
    for digit in number:
        sum_digits += int(digit)
    return sum_digits


def main():
    assert is_n_digit("12345") is True
    assert is_n_digit("123") is False
    assert is_n_digit("hello") is False
    assert is_n_digit("he110") is False
    assert is_n_digit("") is False

    assert digits_separate("12345") == "1,2,3,4,5"
    assert digits_separate("") == ""

    assert digits_sum("") == 0
    assert digits_sum("123") == 6

    while True:
        number = input(f"Please enter a {NUMBER_OF_DIGITS} digit number:\n")
        if is_n_digit(number):
            break

    print(f"You entered the number: {number}")
    print(f"The digits of this number are: {digits_separate(number)}")
    print(f"The sum of the digits is: {digits_sum(number)}")


if __name__ == "__main__":
    main()
