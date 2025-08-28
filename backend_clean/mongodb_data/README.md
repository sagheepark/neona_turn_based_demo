# MongoDB Data Export

## Overview
This directory contains exported MongoDB data for the Neona Chat Demo application.

**Export Date:** 2025-08-28 18:28:18
**Database:** neona_chat
**Total Collections:** 4

## Collections Exported

| Collection | Documents | File |
|------------|-----------|------|
| knowledge_base | 3 | knowledge_base.json |
| conversations | 1 | conversations.json |
| characters | 3 | characters.json |
| user_personas | 1 | user_personas.json |


## How to Import

Use the `import_mongodb_data.py` script to import this data:

```bash
cd backend_clean
python3 import_mongodb_data.py
```

Or import manually using MongoDB tools:

```bash
# For each collection
mongoimport --db neona_chat --collection COLLECTION_NAME --file mongodb_data/COLLECTION_NAME.json --jsonArray
```

## Notes
- ObjectIds are stored as strings and will be converted back during import
- DateTime fields are stored in ISO format
- All data is UTF-8 encoded with Korean character support
