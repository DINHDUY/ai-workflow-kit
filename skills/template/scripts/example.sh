#!/usr/bin/env bash
# Example script for the skill
# This script demonstrates best practices for skill scripts

set -euo pipefail

# Display help if no arguments provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <argument>"
    echo ""
    echo "Description of what this script does."
    echo ""
    echo "Arguments:"
    echo "  argument    Description of the argument"
    echo ""
    echo "Examples:"
    echo "  $0 example-value"
    exit 1
fi

ARGUMENT="$1"

echo "Running example script with argument: $ARGUMENT"

# Add your script logic here
# - Include helpful error messages
# - Handle edge cases gracefully
# - Exit with appropriate status codes

echo "Script completed successfully."
