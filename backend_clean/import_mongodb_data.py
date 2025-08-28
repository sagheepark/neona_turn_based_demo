#!/usr/bin/env python3
"""
MongoDB Data Import Script
Imports JSON files to MongoDB for replicating the database
"""

import json
import os
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def convert_to_objectid(doc):
    """Convert string _id back to ObjectId"""
    if '_id' in doc and isinstance(doc['_id'], str):
        try:
            doc['_id'] = ObjectId(doc['_id'])
        except:
            # If invalid ObjectId format, keep as string
            pass
    return doc

def convert_dates(doc):
    """Convert ISO format strings back to datetime objects"""
    for key, value in doc.items():
        if isinstance(value, str):
            # Check if it looks like an ISO datetime
            if 'T' in value and (value.endswith('Z') or '+' in value or value.count(':') >= 2):
                try:
                    # Remove timezone info for simplicity
                    clean_date = value.split('+')[0].split('Z')[0]
                    doc[key] = datetime.fromisoformat(clean_date)
                except:
                    # Keep as string if conversion fails
                    pass
        elif isinstance(value, dict):
            doc[key] = convert_dates(value)
        elif isinstance(value, list):
            doc[key] = [convert_dates(item) if isinstance(item, dict) else item for item in value]
    return doc

def import_mongodb_data():
    """Import all JSON files to MongoDB"""
    
    # Connect to MongoDB
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/neona_chat')
    client = MongoClient(mongodb_url)
    
    # Get database name from URL
    db_name = mongodb_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    # Check for export directory
    export_dir = 'mongodb_data'
    if not os.path.exists(export_dir):
        print(f"❌ Export directory not found: {export_dir}/")
        print("Please run export_mongodb_data.py first or ensure mongodb_data/ exists")
        return
    
    # Load metadata
    metadata_path = os.path.join(export_dir, '_metadata.json')
    if not os.path.exists(metadata_path):
        print(f"❌ Metadata file not found: {metadata_path}")
        print("Using all JSON files in directory...")
        # Get all JSON files except metadata
        json_files = [f for f in os.listdir(export_dir) if f.endswith('.json') and f != '_metadata.json']
        collections_to_import = [{'file': f, 'name': f.replace('.json', '')} for f in json_files]
    else:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        collections_to_import = metadata['collections']
        print(f"📋 Import metadata loaded from: {metadata['exported_at']}")
    
    print(f"📦 Importing to MongoDB database: {db_name}")
    print(f"📁 Import directory: {export_dir}/")
    print("-" * 50)
    
    # Ask for confirmation
    print(f"\n⚠️  WARNING: This will modify the database: {db_name}")
    print("Collections will be REPLACED with imported data.")
    response = input("Do you want to continue? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("❌ Import cancelled")
        return
    
    print("\nImporting collections...")
    print("-" * 50)
    
    # Import each collection
    imported_count = 0
    for col_info in collections_to_import:
        file_path = os.path.join(export_dir, col_info['file'])
        collection_name = col_info['name']
        
        if not os.path.exists(file_path):
            print(f"⚠️  Skipping {collection_name}: file not found")
            continue
        
        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Convert documents
            for doc in documents:
                doc = convert_to_objectid(doc)
                doc = convert_dates(doc)
            
            # Clear existing collection
            collection = db[collection_name]
            collection.delete_many({})
            
            # Insert documents
            if documents:
                collection.insert_many(documents)
            
            print(f"✅ Imported {collection_name}: {len(documents)} documents")
            imported_count += 1
            
        except Exception as e:
            print(f"❌ Error importing {collection_name}: {e}")
    
    print("-" * 50)
    print(f"✅ Import complete! {imported_count} collections imported")
    
    # Verify import
    print("\n📊 Database Statistics:")
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"  - {collection_name}: {count} documents")
    
    client.close()

def import_selective():
    """Import only specific collections"""
    collections = input("Enter collection names to import (comma-separated): ").strip().split(',')
    collections = [c.strip() for c in collections if c.strip()]
    
    if not collections:
        print("No collections specified")
        return
    
    # Connect to MongoDB
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/neona_chat')
    client = MongoClient(mongodb_url)
    
    # Get database name from URL
    db_name = mongodb_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    export_dir = 'mongodb_data'
    
    print(f"\n📦 Selective import to: {db_name}")
    print(f"📁 Collections to import: {', '.join(collections)}")
    print("-" * 50)
    
    for collection_name in collections:
        file_path = os.path.join(export_dir, f"{collection_name}.json")
        
        if not os.path.exists(file_path):
            print(f"⚠️  Skipping {collection_name}: file not found")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            # Convert documents
            for doc in documents:
                doc = convert_to_objectid(doc)
                doc = convert_dates(doc)
            
            # Clear and insert
            collection = db[collection_name]
            collection.delete_many({})
            if documents:
                collection.insert_many(documents)
            
            print(f"✅ Imported {collection_name}: {len(documents)} documents")
            
        except Exception as e:
            print(f"❌ Error importing {collection_name}: {e}")
    
    client.close()

if __name__ == "__main__":
    print("MongoDB Data Import Tool")
    print("========================")
    print("1. Import all collections")
    print("2. Import specific collections")
    
    choice = input("\nEnter your choice (1/2): ").strip()
    
    if choice == '1':
        import_mongodb_data()
    elif choice == '2':
        import_selective()
    else:
        print("Invalid choice")