EXPORT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../test/data" &> /dev/null && pwd )"
EXPORT_FILE="$EXPORT_DIR/emulator.overall_export_metadata"
curl -X POST -H 'Content-Type: application/json' -d "{\"input_url\": \"$EXPORT_FILE\"}" "$DATASTORE_EMULATOR_HOST/v1/projects/$GOOGLE_CLOUD_PROJECT:import"
