#!/bin/dash
message="hello"
cat <<EOF >> ".pig/logs.txt"
$message
EOF
