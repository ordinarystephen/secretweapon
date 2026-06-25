python3 <<'PY'
STORE="${DOC_STORE_DIR:-/mnt/private/next-sentinel/doc_store}"
for CID in table-b0199 table-b0202; do
  P=$(find "$STORE" -path "*table_crops/$CID.png" | head -1)
  H=$(echo "$P" | sed -E 's#.*/([^/]+)/extractions/[^/]+/table_crops/.*#\1#')
  M=$(echo "$P" | sed -E 's#.*/extractions/([^/]+)/table_crops/.*#\1#')
  echo ">>> $CID  doc_hash=$H  parser_mode=$M"
  python -m ocr_probe.input_check --doc-hash "$H" --crop-id "$CID" --parser-mode "$M" \
      --out "ocr_probe/INPUT_CHECK_$CID.md"
done
PY

##or this one
STORE="${DOC_STORE_DIR:-/mnt/private/next-sentinel/doc_store}"
for CID in table-b0199 table-b0202; do
  P=$(find "$STORE" -path "*table_crops/$CID.png" | head -1)
  H=$(echo "$P" | sed -E 's#.*/([^/]+)/extractions/[^/]+/table_crops/.*#\1#')
  M=$(echo "$P" | sed -E 's#.*/extractions/([^/]+)/table_crops/.*#\1#')
  echo ">>> $CID  doc_hash=$H  parser_mode=$M"
  python3 -m ocr_probe.input_check --doc-hash "$H" --crop-id "$CID" --parser-mode "$M" \
      --out "ocr_probe/INPUT_CHECK_$CID.md"
done

##or this one
bash <<'SH'
STORE="${DOC_STORE_DIR:-/mnt/private/next-sentinel/doc_store}"
for CID in table-b0199 table-b0202; do
  P=$(find "$STORE" -path "*table_crops/$CID.png" | head -1)
  H=$(echo "$P" | sed -E 's#.*/([^/]+)/extractions/[^/]+/table_crops/.*#\1#')
  M=$(echo "$P" | sed -E 's#.*/extractions/([^/]+)/table_crops/.*#\1#')
  echo ">>> $CID  doc_hash=$H  parser_mode=$M"
  python3 -m ocr_probe.input_check --doc-hash "$H" --crop-id "$CID" --parser-mode "$M" \
      --out "ocr_probe/INPUT_CHECK_$CID.md"
done
SH



##then generate the new reports with
cat ocr_probe/INPUT_CHECK_table-b0199.md
cat ocr_probe/INPUT_CHECK_table-b0202.md
