#!/bin/dash

##############################################
# pigs-log : error testing and functionality #
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
pigs-log > "$actual_output" 2>&1
echo "pigs-log: error: pigs repository directory .pig not found" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: Repository not found"
    exit 1
fi

pigs-init > /dev/null 2>&1

# Test 2: Incorrect usage: must have no arguments
pigs-log "invalid_argument" > "$actual_output" 2>&1
echo "usage: pigs-log" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 2 failed: Incorrect usage - must have no arguments"
    exit 1
fi

# Test 3: One commit
echo "line 1" > a
pigs-add a > /dev/null 2>&1
pigs-commit -m "first commit" > /dev/null 2>&1
pigs-log > "$actual_output" 2>&1
echo "0 first commit" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 3 failed: One commit"
    exit 1
fi

# Test 4: Two commits
echo "line 2" >> a
pigs-add a > /dev/null 2>&1
pigs-commit -m "second commit" > /dev/null 2>&1
pigs-log > "$actual_output" 2>&1
{
    echo "1 second commit"
    echo "0 first commit"
} > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 4 failed: Two commits"
    exit 1
fi

echo "All tests passed"
exit 0
