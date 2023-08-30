#!/bin/dash

##############################################
# pigs-add : error testing and functionality #
##############################################

# Note: these tests assume working functionality of pigs-show

PATH="$PATH:$(pwd)"

# Create a temporary directory for the test
test_dir="$(mktemp -d)"
cd "$test_dir" || exit 1

# Create files to hold expected and actual output
actual_output="$(mktemp)"
expected_output="$(mktemp)"

# Remove temp directory when test is finished
trap 'rm "$expected_output" "$actual_output" -rf "$test_dir"' INT EXIT


# Test 1: Repo no found (not runnign pigs-init)
pigs-add file1 > "$actual_output" 2>&1
echo "pigs-add: error: pigs repository directory .pig not found" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: Repository not found (not running pigs-init)"
    exit 1
fi


# Test 2: Check for correct number of arguments
pigs-init > /dev/null 2>&1
pigs-add > "$actual_output" 2>&1
echo "usage: pigs-add <filenames>" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 2 failed: Check for correct number of arguments"
    exit 1
fi


# Test 3: Check file exists in root
pigs-add file2 > "$actual_output" 2>&1
echo "pigs-add: error: can not open 'file2'" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 3 failed: Check file exists in index"
    exit 1
fi

# Test 4: Add multiple files but one doesn't exist
touch a b
pigs-add a b c > "$actual_output" 2>&1
echo "pigs-add: error: can not open 'c'" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 4 failed: Check add multiple files, one doesn't exist"
    exit 1
fi

# Test 5: Add a file
echo "hello world" > x
pigs-add x > /dev/null 2>&1
pigs-show :x > "$actual_output" 2>&1
echo "hello world"> "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 5 failed: Check adding one file"
    exit 1
fi

# Test 6: Add multiple files (NOTE THIS IS NOT A BLACKBOX TEST)
echo "greetings world" > p
echo "hi world" > q
pigs-add p q > /dev/null 2>&1
pigs-show :p > "$actual_output" 2>&1
echo "greetings world"> "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 6 failed: Check adding multiple files"
    exit 1
fi
pigs-show :q > "$actual_output" 2>&1
echo "hi world"> "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 6 failed: Check adding multiple files"
    exit 1
fi


echo "All tests passed"
exit 0