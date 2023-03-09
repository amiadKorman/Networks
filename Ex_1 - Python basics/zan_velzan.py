def zan_velzan():
    number = input("Please enter a 5 digit number\n")
    print(f"You entered the number: {number}")
    print(f"The digits of this number are: {','.join(number)}")
    digits_sum = 0
    for digit in number:
        digits_sum += int(digit)
    print(f"The sum of the digits is: {digits_sum}")


zan_velzan()
