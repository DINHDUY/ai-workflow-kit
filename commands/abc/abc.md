# command-name

## Overview

A brief description of what this command does and when to use it. Keep it to one or two sentences so the agent understands the purpose at a glance.

## Steps

1. **Understand the request**
   - Extract any details the user provided after the `/command-name` prefix
   - Ask only for information that is missing — do not re-ask what was already given

2. **Execute the task**
   - Describe the concrete actions the agent should take
   - Include exact commands, file paths, or API calls when applicable
   - Use code blocks for any shell commands:
     ```bash
     echo "replace with your actual command"
     ```

3. **Verify the result**
   - Describe how to confirm the task succeeded
   - Include expected output or success criteria

## Configuration

<!-- Remove this section if the command needs no configuration -->

If the command requires configuration, document it here:

| Setting | Required | Default | Description |
|---------|----------|---------|-------------|
| `EXAMPLE_VAR` | Yes | — | What this setting controls |

## Examples

### Basic usage

```
/command-name do something simple
```

### Advanced usage

```
/command-name do something with --option value and extra context
```

## Notes

- Keep notes brief and actionable
- Document any prerequisites (tools, environment, permissions)
- Mention limitations the user should be aware of
