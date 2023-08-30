#!/bin/dash

##############################################
# pigs-show : error testing and functionality #
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
pigs-show 0:a > "$actual_output" 2>&1
echo "pigs-show: error: pigs repository directory .pig not found" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: Repository not found"
    exit 1
fi

pigs-init > /dev/null 2>&1

# Test 2: Incorrect usage: must have one argument
pigs-show > "$actual_output" 2>&1
echo "usage: pigs-show <commit>:<filename>" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 2 failed: Incorrect usage - must have one argument"
    exit 1
fi

# Test 3: No colon in the argument
pigs-show 0a > "$actual_output" 2>&1
echo "usage: pigs-show <commit>:<filename>" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 3 failed: No colon in the argument"
    exit 1
fi

# Test 4: Unknown commit
echo "line 1" > a
pigs-add a > /dev/null 2>&1
pigs-show 1:a > "$actual_output" 2>&1
echo "pigs-show: error: unknown commit '1'" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 4 failed: Unknown commit"
    exit 1
fi

# Test 5: File not found in index
pigs-show :b > "$actual_output" 2>&1
echo "pigs-show: error: 'b' not found in index" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 5 failed: File not found in index"
    exit 1
fi

# Test 6: Show file from index
pigs-add a > /dev/null 2>&1
pigs-show :a > "$actual_output" 2>&1
echo "line 1" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 6 failed: Show file from index"
    exit 1
fi

# Test 7: File not found in commit
pigs-commit -m "first commit" > /dev/null 2>&1
echo "line 2" > b
pigs-add b > /dev/null 2>&1
pigs-show 0:b > "$actual_output" 2>&1
echo "pigs-show: error: 'b' not found in commit 0" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 7 failed: File not found in commit"
    exit 1
fi

# Test 8: Show file from commit
pigs-commit -m "second commit" > /dev/null 2>&1
pigs-show 1:b > "$actual_output" 2>&1
echo "line 2" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 8 failed: Show file from commit"
    exit 1
fi

# Test 9: Filename cannot be empty
pigs-show ":" > "$actual_output" 2>&1
echo "pigs-show: error: invalid filename ''" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 9 failed: Filename cannot be empty"
    exit 1
fi

# Test 10: Filename can only contain alphanumeric or . _ -
pigs-show ":file!" > "$actual_output" 2>&1
echo "pigs-show: error: invalid filename 'file!'" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 10 failed: Filename can only contain alphanumeric or . _ -"
    exit 1
fi

# Test 11: Filename must start with alphanumeric
pigs-show ":-file" > "$actual_output" 2>&1
echo "pigs-show: error: invalid filename '-file'" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 11 failed: Filename must start with alphanumeric"
    exit 1
fi

echo "All tests passed"
exit 0
