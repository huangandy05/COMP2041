#!/bin/dash

# NOTE: CODE PARAPHRASED FROM ASSIGNMENT SPEC ~
# Case statement for handling the number of arguments
case $# in
    0)
        echo "You provided no arguments."
        ;;
    1)
        echo "You provided one argument."
        ;;
    2|3|4)
        echo "You provided a few arguments."
        ;;
    *)
        echo "You provided many arguments."
        ;;
esac

# Nested command substitution
current_date=$(date +%Y-%m-%d)
echo "Hello $(whoami), the current date is $current_date"
echo "Double quotes allow command substitution: $(hostname)"
echo 'Single quotes do not allow command substitution: $(this will not be evaluated)'
echo "Your user groups are: $(groups $(whoami))"

# More arithmetic operations
num1=6
num2=7
echo "Sum of $num1 and $num2 is $((num1 + num2))"

# Using && and || in if and while loops
if test -w /dev/null && test -x /dev/null
then
    echo "/dev/null can be written to and executed."
fi

# Checking for the current user in a file
if grep -Eq $(whoami) enrolments.tsv
then
    echo "Your user is enrolled in COMP2041/9044."
fi

# Example of a while loop with test conditions
count=3
while test $count -gt 0
do
    echo "Counting down: $count"
    count=$((count - 1))
done

