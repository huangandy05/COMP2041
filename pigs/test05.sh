#!/bin/dash

#########################################
# pigs-rm : error testing and functionality #
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

# Test 1: Error when no file in index
pigs-rm hi > "$actual_output" 2>&1
echo "pigs-rm: error: 'hi' is not in the pigs repository" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: file not in index"
    exit 1
fi

# Test 2: Successful removal of file from the index
echo "content" > testfile
pigs-add testfile > /dev/null 2>&1
pigs-rm --cached testfile > /dev/null 2>&1
pigs-show :testfile > "$actual_output" 2>&1
echo "pigs-show: error: 'testfile' not found in index" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 2 failed: removal from index"
    exit 1
fi

# Test 3: Successful removal of file from the directory and index
echo "content" > testfile
pigs-add testfile > /dev/null 2>&1
pigs-commit -m "commit message" > /dev/null 2>&1
pigs-rm testfile > /dev/null 2>&1
if [ -f testfile ]
then
    echo "Test 3 failed: removal from directory"
    exit 1
fi
pigs-show :testfile > "$actual_output" 2>&1
echo "pigs-show: error: 'testfile' not found in index" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 3 failed: removal from index"
    exit 1
fi

# Test 4: Use --force option
echo "content" > testfile
pigs-add testfile > /dev/null 2>&1
echo "modified content" > testfile
pigs-rm --force testfile > /dev/null 2>&1
if [ -f testfile ]
then
    echo "Test 4 failed: force removal"
    exit 1
fi
pigs-show :testfile > "$actual_output" 2>&1
echo "pigs-show: error: 'testfile' not found in index" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 4 failed: removal from index"
    exit 1
fi

echo "All tests passed"
exit 0
