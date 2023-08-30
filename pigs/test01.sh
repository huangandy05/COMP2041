#!/bin/dash

##############################################
# pigs-commit : error testing and functionality #
##############################################

PATH="$PATH:$(pwd)"

# Create a temporary directory for the test
test_dir="$(mktemp -d)"
cd "$test_dir" || exit 1

# Create files to hold expected and actual output
actual_output="$(mktemp)"
expected_output="$(mktemp)"

# Remove temp directory when test is finished
trap 'rm "$expected_output" "$actual_output" -rf "$test_dir"' INT EXIT

# Test 1: Repo not found
pigs-commit -m "message" > "$actual_output" 2>&1
echo "pigs-commit: error: pigs repository directory .pig not found" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: Repository not found"
    exit 1
fi

pigs-init > /dev/null 2>&1

# Test 2: Incorrect usage: pigs-commit -incorrect
pigs-commit -incorrect > "$actual_output" 2>&1
echo "usage: pigs-commit [-a] -m commit-message" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 2 failed: Incorrect usage - invalid flag"
    exit 1
fi

# Test 3: Incorrect usage: no message attached to message
pigs-commit -m > "$actual_output" 2>&1
echo "usage: pigs-commit [-a] -m commit-message" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 3 failed: Incorrect usage - no message attached to -m"
    exit 1
fi

# Test 4: Incorrect usage: too many arguments after -m
pigs-commit -m "message1" "message2" > "$actual_output" 2>&1
echo "usage: pigs-commit [-a] -m commit-message" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 4 failed: Incorrect usage - too many arguments after -m"
    exit 1
fi

# Test 5: Incorrect usage: doesn't contain args
pigs-commit > "$actual_output" 2>&1
echo "usage: pigs-commit [-a] -m commit-message" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 5 failed: Incorrect usage - doesn't contain arg"
    exit 1
fi

# Test 6: No error from "pigs-commit -m'hello there'"
touch file0
pigs-add file0 > /dev/null 2>&1
pigs-commit -m "hello there" > "$actual_output" 2>&1
echo "Committed as commit 0" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 6 failed: Correct usage - pigs-commit -m'hello there'"
    exit 1
fi

# Test 7: Scramble arguments, no error from "pigs-commit -mmessage1"
touch file1
pigs-add file1 > /dev/null 2>&1
pigs-commit -m"message1" > "$actual_output" 2>&1
echo "Committed as commit 1" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 7 failed: Correct usage - pigs-commit -mMessage1"
    exit 1
fi

# Test 8: Successfully commit 2 things
touch file3 file2
pigs-add file3 file2 > /dev/null 2>&1
pigs-commit -m "message2" > "$actual_output" 2>&1
echo "Committed as commit 2" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 8 failed: Successfully commit 2 things"
    exit 1
fi

# Test 9: Nothing to commit
pigs-commit -m "message3" > "$actual_output" 2>&1
echo "nothing to commit" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 9 failed: Nothing to commit"
    exit 1
fi

echo "All tests passed"
exit 0
