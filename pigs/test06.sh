#!/bin/dash

#########################################
# pigs-status : error testing and functionality #
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

# Test 1: Error when more than 0 arguments
pigs-status arg > "$actual_output" 2>&1
echo "usage: pigs-status" > "$expected_output"
if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test 1 failed: more than 0 arguments"
    exit 1
fi

# Test all cases at once
# Creating all files in root
touch f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12
# Add files that appear in repo
pigs-add f3 f6 f7 f8 f9 f10 f11 f12
pigs-commit -m 'Add to repo' 1> /dev/null
# Add files that are in index and not repo
pigs-add f2 f4 f5
# Remove files not in index
pigs-rm --cached f3 f6
# Modify files
echo a > f5
echo a > f8
echo a > f10
echo a > f11
echo a > f12
rm f2 f3 f7
pigs-add f8 f11 f12
rm f8
echo b > f12

pigs-status > "$actual_output"
# cat "$actual_output"

cat > "$expected_output" << eof
f1 - untracked
f10 - file changed, changes not staged for commit
f11 - file changed, changes staged for commit
f12 - file changed, different changes staged for commit
f2 - added to index, file deleted
f3 - file deleted, deleted from index
f4 - added to index
f5 - added to index, file changed
f6 - deleted from index
f7 - file deleted
f8 - file deleted, changes staged for commit
f9 - same as repo
eof

if ! diff -u "$expected_output" "$actual_output"
then
    echo "Test failed"
    exit 1
fi

echo "All tests passed"
exit 0
