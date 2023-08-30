#!/bin/dash

#########################################
# pigs-commit : -a option functionality #
#########################################

PATH="$PATH:$(pwd)"

# Create a temporary directory for the test
test_dir="$(mktemp -d)"
cd "$test_dir" || exit 1

# Create files to hold expected and actual output
actual_output="$(mktemp)"
expected_output="$(mktemp)"

# Remove temp directory when test is finished
trap 'rm "$expected_output" "$actual_output" -rf "$test_dir"' INT EXIT

# Test preparation: repo initialization
pigs-init > /dev/null 2>&1

# Test 1: Auto add file before commit
echo "Hello World" > a
pigs-add a > /dev/null 2>&1
echo "Hello World Updated" > a
pigs-commit -am "first commit" > /dev/null 2>&1
pigs-show :a > "$actual_output" 2>&1
echo "Hello World Updated" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: Auto add file before commit"
    exit 1
fi

# Test 2: Correct syntax - pigs-commit -am MESSAGE
echo "Hello Again" > a
pigs-commit -am "second commit" > /dev/null 2>&1
pigs-show :a > "$actual_output" 2>&1
echo "Hello Again" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 2 failed: Correct syntax - pigs-commit -am MESSAGE"
    exit 1
fi

# Test 3: Correct syntax - pigs-commit -amMESSAGE
echo "Another Change" > a
pigs-commit -amthird_commit > /dev/null 2>&1
pigs-show :a > "$actual_output" 2>&1
echo "Another Change" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 3 failed: Correct syntax - pigs-commit -amMESSAGE"
    exit 1
fi

# Test 4: Correct syntax - pigs-commit -a -m MESSAGE
echo "Final Change" > a
pigs-commit -a -m "fourth commit" > /dev/null 2>&1
pigs-show :a > "$actual_output" 2>&1
echo "Final Change" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 4 failed: Correct syntax - pigs-commit -a -m MESSAGE"
    exit 1
fi

echo "All tests passed"
exit 0
