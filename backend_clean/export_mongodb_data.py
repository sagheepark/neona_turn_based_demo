#!/usr/bin/env python3
"""
MongoDB Data Export Script
Exports all collections from MongoDB to JSON files for easy replication
"""

import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def export_mongodb_data():
    """Export all MongoDB collections to JSON files"""
    
    # Connect to MongoDB
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/neona_chat')
    client = MongoClient(mongodb_url)
    
    # Get database name from URL
    db_name = mongodb_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    # Create export directory
    export_dir = 'mongodb_data'
    os.makedirs(export_dir, exist_ok=True)
    
    # Export metadata
    metadata = {
        'exported_at': datetime.now().isoformat(),
        'database': db_name,
        'collections': []
    }
    
    print(f"📦 Exporting MongoDB database: {db_name}")
    print(f"📁 Export directory: {export_dir}/")
    print("-" * 50)
    
    # Get all collections
    collections = db.list_collection_names()
    
    for collection_name in collections:
        collection = db[collection_name]
        documents = list(collection.find())
        
        # Convert ObjectId and datetime for JSON serialization
        def convert_document(doc):
            if isinstance(doc, dict):
                for key, value in doc.items():
                    if isinstance(value, ObjectId):
                        doc[key] = str(value)
                    elif isinstance(value, datetime):
                        doc[key] = value.isoformat()
                    elif isinstance(value, dict):
                        doc[key] = convert_document(value)
                    elif isinstance(value, list):
                        doc[key] = [convert_document(item) if isinstance(item, dict) else 
                                   str(item) if isinstance(item, ObjectId) else
                                   item.isoformat() if isinstance(item, datetime) else item
                                   for item in value]
            return doc
        
        documents = [convert_document(doc) for doc in documents]
        
        # Save to JSON file
        file_path = os.path.join(export_dir, f"{collection_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        
        # Update metadata
        metadata['collections'].append({
            'name': collection_name,
            'count': len(documents),
            'file': f"{collection_name}.json"
        })
        
        print(f"✅ Exported {collection_name}: {len(documents)} documents")
    
    # Save metadata
    metadata_path = os.path.join(export_dir, '_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print("-" * 50)
    print(f"✅ Export complete! {len(collections)} collections exported")
    print(f"📋 Metadata saved to: {metadata_path}")
    
    # Create a README for the exported data
    readme_path = os.path.join(export_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(f"""# MongoDB Data Export

## Overview
This directory contains exported MongoDB data for the Neona Chat Demo application.

**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** {db_name}
**Total Collections:** {len(collections)}

## Collections Exported

| Collection | Documents | File |
|------------|-----------|------|
""")
        for col in metadata['collections']:
            f.write(f"| {col['name']} | {col['count']} | {col['file']} |\n")
        
        f.write("""

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
""")
    
    print(f"📄 README created: {readme_path}")
    
    client.close()

if __name__ == "__main__":
    export_mongodb_data()