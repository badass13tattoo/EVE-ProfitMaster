"""
Cache Service
Handles data caching with both memory and database storage
"""

import json
import time
import datetime
from typing import Optional, Any
from flask_sqlalchemy import SQLAlchemy
from models.cache_entry import CacheEntry


class CacheService:
    """Service for managing data caching"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.memory_cache = {}
        self.cache_duration = 3600  # 1 hour default
    
    def get(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        # Check memory cache first
        if key in self.memory_cache:
            data, timestamp = self.memory_cache[key]
            if time.time() - timestamp < self.cache_duration:
                return data
            else:
                del self.memory_cache[key]
        
        # Check database cache
        try:
            cache_entry = CacheEntry.query.filter_by(cache_key=key).first()
            if cache_entry and cache_entry.expires_at > datetime.datetime.utcnow():
                data = json.loads(cache_entry.cache_data)
                # Store in memory cache for faster access
                self.memory_cache[key] = (data, time.time())
                return data
            elif cache_entry:
                # Expired entry, remove it
                self.db.session.delete(cache_entry)
                self.db.session.commit()
        except Exception as e:
            print(f"Error getting from cache: {e}")
        
        return None
    
    def set(self, key: str, data: Any, ttl: int = None) -> None:
        """Set data in cache"""
        if ttl is None:
            ttl = self.cache_duration
        
        # Store in memory cache
        self.memory_cache[key] = (data, time.time())
        
        # Store in database cache
        try:
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl)
            
            # Remove existing entry if it exists
            existing_entry = CacheEntry.query.filter_by(cache_key=key).first()
            if existing_entry:
                self.db.session.delete(existing_entry)
            
            # Create new entry
            cache_entry = CacheEntry(
                cache_key=key,
                cache_data=json.dumps(data),
                expires_at=expires_at
            )
            self.db.session.add(cache_entry)
            self.db.session.commit()
        except Exception as e:
            print(f"Error setting cache: {e}")
    
    def delete(self, key: str) -> None:
        """Delete data from cache"""
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from database cache
        try:
            cache_entry = CacheEntry.query.filter_by(cache_key=key).first()
            if cache_entry:
                self.db.session.delete(cache_entry)
                self.db.session.commit()
        except Exception as e:
            print(f"Error deleting from cache: {e}")
    
    def clear_expired(self) -> None:
        """Clear expired cache entries"""
        try:
            # Clear expired memory cache
            current_time = time.time()
            expired_keys = [
                key for key, (data, timestamp) in self.memory_cache.items()
                if current_time - timestamp >= self.cache_duration
            ]
            for key in expired_keys:
                del self.memory_cache[key]
            
            # Clear expired database cache
            expired_entries = CacheEntry.query.filter(
                CacheEntry.expires_at < datetime.datetime.utcnow()
            ).all()
            for entry in expired_entries:
                self.db.session.delete(entry)
            self.db.session.commit()
        except Exception as e:
            print(f"Error clearing expired cache: {e}")
    
    def clear_all(self) -> None:
        """Clear all cache entries"""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear database cache
        try:
            CacheEntry.query.delete()
            self.db.session.commit()
        except Exception as e:
            print(f"Error clearing all cache: {e}")
