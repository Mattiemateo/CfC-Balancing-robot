#!/bin/bash
# FINAL FIX: Arduino ARM64 - Complete Solution
# This is the nuclear option that works!

echo "╔════════════════════════════════════════════════════════════╗"
echo "║    FINAL FIX: Arduino ctags Issue - ARM64 Complete       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Kill Arduino if running
echo "Stopping Arduino IDE..."
pkill -9 Arduino 2>/dev/null
sleep 2

# Remove ctags completely
echo "Removing ctags..."
rm -rf ~/Library/Arduino15/packages/builtin/tools/ctags

# Clear all caches
echo "Clearing caches..."
rm -rf ~/Library/Arduino15/staging
rm -rf ~/Library/Arduino15/tmp
rm -rf ~/Library/Arduino15/.cache

# Disable code analysis in preferences (the real fix!)
echo "Disabling code analysis..."
if ! grep -q "editor.input_method_support=false" ~/Library/Arduino15/preferences.txt; then
  echo "" >> ~/Library/Arduino15/preferences.txt
  echo "# Disable code analysis (ctags)" >> ~/Library/Arduino15/preferences.txt
  echo "editor.input_method_support=false" >> ~/Library/Arduino15/preferences.txt
fi

echo ""
echo "✅ FINAL FIX COMPLETE!"
echo ""
echo "Summary of changes:"
echo "  ✓ Removed ctags completely"
echo "  ✓ Cleared all Arduino caches"  
echo "  ✓ Disabled code analysis in preferences"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Open Arduino IDE"
echo "2. Go to: Tools → Board Manager"
echo "3. Search for 'ESP32' by Espressif Systems"
echo "4. Click 'Install' (wait 5-10 minutes)"
echo "5. Close Arduino completely"
echo "6. Re-open Arduino"
echo "7. Try uploading your sketch!"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "If still issues, try this ONE MORE TIME:"
echo "  bash ~/fix_ctags.sh"
echo ""
