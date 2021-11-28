EXPORT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../test/data" &> /dev/null && pwd )"
rm -r $EXPORT_DIR
curl -X POST -H 'Content-Type: application/json' -d "{\"output_url_prefix\": \"$EXPORT_DIR\"}" "$DATASTORE_EMULATOR_HOST/v1/projects/$GOOGLE_CLOUD_PROJECT:export"
GENERATED_EXPORT_DIR=$(find $EXPORT_DIR/* -maxdepth 0 -type d)
mv $GENERATED_EXPORT_DIR/* $EXPORT_DIR
rmdir $GENERATED_EXPORT_DIR
GENERATED_EXPORT_FILE=$(find $EXPORT_DIR/* -maxdepth 1 -type f)
mv $GENERATED_EXPORT_FILE $EXPORT_DIR/emulator.overall_export_metadata
