#!/bin/bash

# -------- CONFIG --------
CONTRACT_DIR="/home/kabir-nagpal/Desktop/soltgp/myproject"
OUTPUT_ROOT="$(pwd)/test_combined"
TIMEOUT=40
MODE=0


mkdir -p "$OUTPUT_ROOT"

FAILED_LOG="$OUTPUT_ROOT/failed_contracts.txt"
> "$FAILED_LOG"

echo "📄 Failed contracts will be logged at:"
echo "   $FAILED_LOG"
echo "==============================================="

# -------- RUN TOOL --------
for contract in "$CONTRACT_DIR"/*.sol; do
  if [ ! -f "$contract" ]; then
    echo "⚠️  No Solidity files found in $CONTRACT_DIR"
    exit 0
  fi

  contract_name=$(basename "$contract" .sol)
  echo "🚀 Running SolTG++ on: $contract_name.sol"

  # Ensure clean workspace
  rm -rf test

  # Run tool
  python -m soltgfrontend.solTg.RunAll \
    -i "$contract" \
    -t "$TIMEOUT" \

  RETVAL=$?

  # Handle failure
  if [ $RETVAL -ne 0 ] || [ ! -d "test" ]; then
    echo "❌ FAILED: $contract_name (exit code=$RETVAL)" | tee -a "$FAILED_LOG"
    rm -rf test
    echo "-----------------------------------------------"
    continue
  fi

  # Move output
  DEST="$OUTPUT_ROOT/test_$contract_name"
  mkdir -p "$DEST"
  mv test "$DEST"

  echo "✅ Success: $DEST/test/SolTGP_Report.html"
  echo "-----------------------------------------------"
done

echo "🎉 Processing complete."
echo "📁 Results directory: $OUTPUT_ROOT"

if [ -s "$FAILED_LOG" ]; then
  echo "⚠️  Some contracts failed. See:"
  echo "   $FAILED_LOG"
else
  echo "✅ All contracts processed successfully."
fi
