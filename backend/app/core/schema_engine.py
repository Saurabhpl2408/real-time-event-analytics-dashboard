from sqlalchemy import text
from typing import Dict, Any
import json


class SchemaEngine:
    """Handles dynamic schema operations"""
    
    @staticmethod
    async def create_event_table(db, schema_name: str, properties: Dict[str, Any]):
        """Create a table for a specific schema"""
        table_name = f"events_{schema_name}"
        
        # Base columns that all event tables have
        base_columns = """
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            event_type VARCHAR(100) NOT NULL,
            user_id VARCHAR(100),
            session_id VARCHAR(100),
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            properties JSONB,
            metadata JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW()
        """
        
        # Create table
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {base_columns}
        );
        """
        
        await db.execute(text(create_table_sql))
        
        # Create indexes
        await db.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_timestamp ON {table_name}(timestamp);"))
        await db.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_event_type ON {table_name}(event_type);"))
        await db.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_user_id ON {table_name}(user_id);"))
        await db.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_session_id ON {table_name}(session_id);"))
        
        await db.commit()
        print(f"✅ Created table: {table_name}")
    
    @staticmethod
    async def insert_event(db, schema_name: str, event_data: Dict[str, Any]):
        """Insert event into schema-specific table"""
        table_name = f"events_{schema_name}"
        
        insert_sql = text(f"""
        INSERT INTO {table_name} 
        (event_type, user_id, session_id, timestamp, properties, metadata)
        VALUES 
        (:event_type, :user_id, :session_id, :timestamp, :properties, :metadata)
        RETURNING id
        """)
        
        result = await db.execute(
            insert_sql,
            {
                "event_type": event_data.get("event_type"),
                "user_id": event_data.get("user_id"),
                "session_id": event_data.get("session_id"),
                "timestamp": event_data.get("timestamp"),
                "properties": json.dumps(event_data.get("properties", {})),
                "metadata": json.dumps(event_data.get("metadata", {}))  # Use 'metadata' key
            }
        )
        
        await db.commit()
        return result.fetchone()[0]
    
        """Insert event into schema-specific table"""
        table_name = f"events_{schema_name}"
        
        insert_sql = text(f"""
        INSERT INTO {table_name} 
        (event_type, user_id, session_id, timestamp, properties, metadata)
        VALUES 
        (:event_type, :user_id, :session_id, :timestamp, :properties, :metadata)
        RETURNING id
        """)
        
        result = await db.execute(
            insert_sql,
            {
                "event_type": event_data.get("event_type"),
                "user_id": event_data.get("user_id"),
                "session_id": event_data.get("session_id"),
                "timestamp": event_data.get("timestamp"),
                "properties": json.dumps(event_data.get("properties", {})),
                "metadata": json.dumps(event_data.get("metadata", {}))
            }
        )
        
        await db.commit()
        return result.fetchone()[0]
    
    @staticmethod
    def validate_event_against_schema(event_data: Dict[str, Any], schema_properties: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate event data against schema definition
        Flexible validation - only checks if event type exists
        Allows extra properties from tag manager (tracked_at, page_url, etc.)
        """
        event_type = event_data.get("event_type")
        
        # Check if event type exists in schema
        if event_type not in schema_properties:
            return False, f"Event type '{event_type}' not defined in schema"
        
        # If schema properties for this event type is empty dict, allow all properties
        if not schema_properties[event_type]:
            return True, "Valid"
        
        # Otherwise, validate only the properties defined in schema
        # But allow extra properties that aren't defined
        properties = event_data.get("properties", {})
        expected_props = schema_properties[event_type]
        
        for prop_name, prop_type in expected_props.items():
            if prop_name in properties:
                value = properties[prop_name]
                
                # Basic type validation (only for defined properties)
                if prop_type == "string" and not isinstance(value, str):
                    return False, f"Property '{prop_name}' should be string, got {type(value).__name__}"
                elif prop_type == "number" and not isinstance(value, (int, float)):
                    return False, f"Property '{prop_name}' should be number, got {type(value).__name__}"
                elif prop_type == "boolean" and not isinstance(value, bool):
                    return False, f"Property '{prop_name}' should be boolean, got {type(value).__name__}"
                elif prop_type == "array" and not isinstance(value, list):
                    return False, f"Property '{prop_name}' should be array, got {type(value).__name__}"
        
        return True, "Valid"