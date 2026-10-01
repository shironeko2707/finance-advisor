# Bash Compatibility Fix for run_dev.sh

## Issue
The original `run_dev.sh` script failed with the error:
```
run_dev.sh: line 100: declare: -A: invalid option
```

## Root Cause
- The script used `declare -A` (associative arrays), which requires **Bash 4.0+**
- macOS ships with **Bash 3.2.57** by default
- Associative arrays are not available in Bash 3.2

## Fix Applied
Replaced the two-pass associative array approach (lines 95-134) with a simpler single-pass approach compatible with Bash 3.2.

### Before (Bash 4+ only):
```bash
declare -A env_vars
while IFS= read -r line; do
    # ... parse line ...
    env_vars["$var_name"]="$var_value"
done < .env.local

for var_name in "${!env_vars[@]}"; do
    export "$var_name"="${env_vars[$var_name]}"
done
```

### After (Bash 3.2 compatible):
```bash
while IFS= read -r line || [ -n "$line" ]; do
    # ... parse line ...
    export "$var_name"="$var_value"
    echo -e "  ${NC}$var_name = $var_value"
done < .env.local
```

## How to Use
Now you can run the script normally:
```bash
cd API.FastPy
bash run_dev.sh
```

Or make it executable and run directly:
```bash
chmod +x run_dev.sh
./run_dev.sh
```

## Alternative Solutions

### Option 1: Upgrade to Bash 4+ (Recommended for Development)
Install Bash 4+ via Homebrew:
```bash
# Install Bash 5
brew install bash

# Add to your shell PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="/opt/homebrew/bin:$PATH"

# Verify version
bash --version
```

### Option 2: Force Script to Use Bash 4+
Change the shebang line:
```bash
#!/usr/bin/env bash  # Uses whatever bash is in PATH
```

Or:
```bash
#!/opt/homebrew/bin/bash  # Uses Homebrew bash directly
```

### Option 3: Keep Bash 3.2 Compatibility (Current Fix)
Use the simplified version without associative arrays.

## Testing
Verify the script syntax:
```bash
bash -n run_dev.sh
```

Run the script:
```bash
bash run_dev.sh
```

## Notes
- The simplified version removes variable expansion in .env values
- If you need variable expansion (e.g., `DATABASE_URL=${HOST}:${PORT}`), consider upgrading to Bash 4+
- For production deployments, Docker containers use modern Bash versions, so this issue only affects local development on macOS

## Related Files
- [run_dev.sh](run_dev.sh) - Fixed development script
- [.env.local](.env.local) - Environment configuration file

---

**Fixed By**: Claude AI Assistant
**Date**: 2026-02-01
**Bash Version Tested**: 3.2.57 (macOS default)
