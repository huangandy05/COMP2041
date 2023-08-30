#!/bin/dash

#########################################
# pigs-branch : error testing and functionality #
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

# Test 1: Repo not found
pigs-branch > "$actual_output" 2>&1
echo "pigs-branch: error: pigs repository directory .pig not found" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: Repository not found"
    exit 1
fi

# Test preparation: repo initialization
pigs-init > /dev/null 2>&1

echo "All tests passed"
exit 0