#!/usr/bin/env python3
"""
Index Rebuild Script for Nebula Graph

This script rebuilds indexes after waiting for asynchronous index creation to complete.
Index creation in Nebula Graph is asynchronous and requires waiting ~2 heartbeats (≈20s)
before running REBUILD statements.
"""

import argparse
import logging
import time
from pathlib import Path
from typing import List, Dict, Any
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndexRebuilder:
    def __init__(self, host: str = "localhost", port: int = 9669, 
                 username: str = "root", password: str = "nebula"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection_pool = None
        self.session = None
    
    def connect(self):
        """Connect to Nebula Graph"""
        try:
            config = Config()
            self.connection_pool = ConnectionPool()
            self.connection_pool.init([(self.host, self.port)], config)
            self.session = self.connection_pool.get_session(self.username, self.password)
            logger.info(f"Connected to Nebula Graph at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Nebula Graph: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Nebula Graph"""
        if self.session:
            self.session.release()
        if self.connection_pool:
            self.connection_pool.close()
        logger.info("Disconnected from Nebula Graph")
    
    def use_space(self, space_name: str) -> bool:
        """Switch to the specified space"""
        try:
            result = self.session.execute(f'USE {space_name};')
            if result.is_succeeded():
                logger.info(f"Switched to space: {space_name}")
                return True
            else:
                logger.error(f"Failed to switch to space {space_name}: {result.error_msg()}")
                return False
        except Exception as e:
            logger.error(f"Error switching to space {space_name}: {e}")
            return False
    
    def get_existing_indexes(self, space_name: str) -> List[str]:
        """Get list of existing indexes in the space"""
        if not self.connect():
            return []
        
        if not self.use_space(space_name):
            self.disconnect()
            return []
        
        try:
            result = self.session.execute('SHOW TAG INDEXES;')
            if not result.is_succeeded():
                logger.error(f"Failed to get index list: {result.error_msg()}")
                self.disconnect()
                return []
            
            indexes = []
            for row in result:
                try:
                    # Use get_value_by_key to get the index name
                    index_name = row.get_value_by_key('Index Name')
                    if index_name:
                        # Remove quotes if present
                        if isinstance(index_name, str) and index_name.startswith('"') and index_name.endswith('"'):
                            index_name = index_name[1:-1]
                        indexes.append(index_name)
                except Exception as e:
                    logger.warning(f"Could not parse index row: {row}, error: {e}")
            
            logger.info(f"Found {len(indexes)} indexes: {indexes}")
            self.disconnect()
            return indexes
            
        except Exception as e:
            logger.error(f"Error getting index list: {e}")
            self.disconnect()
            return []
    
    def rebuild_indexes(self, space_name: str, wait_seconds: int = 20) -> bool:
        """Rebuild all indexes in the space"""
        logger.info(f"Waiting {wait_seconds} seconds for index creation to complete...")
        time.sleep(wait_seconds)
        
        if not self.connect():
            return False
        
        if not self.use_space(space_name):
            self.disconnect()
            return False
        
        try:
            # Get list of existing indexes
            result = self.session.execute('SHOW TAG INDEXES;')
            if not result.is_succeeded():
                logger.error(f"Failed to get index list: {result.error_msg()}")
                self.disconnect()
                return False
            
            indexes = []
            for row in result:
                try:
                    # Use get_value_by_key to get the index name
                    index_name = row.get_value_by_key('Index Name')
                    if index_name:
                        # Remove quotes if present
                        if isinstance(index_name, str) and index_name.startswith('"') and index_name.endswith('"'):
                            index_name = index_name[1:-1]
                        indexes.append(index_name)
                except Exception as e:
                    logger.warning(f"Could not parse index row: {row}, error: {e}")
            
            if not indexes:
                logger.info("No indexes found to rebuild")
                self.disconnect()
                return True
            
            logger.info(f"Found {len(indexes)} indexes to rebuild: {indexes}")
            
            success_count = 0
            for index_name in indexes:
                try:
                    # Remove quotes from index name if present
                    clean_index_name = index_name
                    if isinstance(index_name, str) and index_name.startswith('"') and index_name.endswith('"'):
                        clean_index_name = index_name[1:-1]
                    query = f'REBUILD TAG INDEX {clean_index_name};'
                    logger.info(f"Rebuilding index: {query}")
                    logger.info(f"Rebuilding index: {query}")
                    
                    result = self.session.execute(query)
                    if result.is_succeeded():
                        logger.info(f"✓ Successfully rebuilt index: {index_name}")
                        success_count += 1
                    else:
                        logger.warning(f"✗ Failed to rebuild index {index_name}: {result.error_msg()}")
                        
                except Exception as e:
                    logger.error(f"✗ Error rebuilding index {index_name}: {e}")
            
            logger.info(f"Index rebuild completed: {success_count}/{len(indexes)} successful")
            self.disconnect()
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error during index rebuild: {e}")
            self.disconnect()
            return False
    
    def rebuild_specific_indexes(self, space_name: str, index_names: List[str], wait_seconds: int = 20) -> bool:
        """Rebuild specific indexes"""
        logger.info(f"Waiting {wait_seconds} seconds for index creation to complete...")
        time.sleep(wait_seconds)
        
        if not self.connect():
            return False
        
        if not self.use_space(space_name):
            self.disconnect()
            return False
        
        success_count = 0
        total_count = len(index_names)
        
        for index_name in index_names:
            try:
                # Remove quotes from index name if present
                clean_index_name = index_name
                if isinstance(index_name, str) and index_name.startswith('"') and index_name.endswith('"'):
                    clean_index_name = index_name[1:-1]
                query = f'REBUILD TAG INDEX {clean_index_name};'
                logger.info(f"Rebuilding index: {query}")
                
                result = self.session.execute(query)
                if result.is_succeeded():
                    logger.info(f"✓ Successfully rebuilt index: {index_name}")
                    success_count += 1
                else:
                    logger.warning(f"✗ Failed to rebuild index {index_name}: {result.error_msg()}")
                    
            except Exception as e:
                logger.error(f"✗ Error rebuilding index {index_name}: {e}")
        
        logger.info(f"Specific index rebuild completed: {success_count}/{total_count} successful")
        self.disconnect()
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description='Rebuild indexes for Nebula Graph spaces')
    parser.add_argument('--space-name', required=True, help='Name of the space to rebuild indexes for')
    parser.add_argument('--host', default='localhost', help='Nebula Graph host')
    parser.add_argument('--port', type=int, default=9669, help='Nebula Graph port')
    parser.add_argument('--username', default='root', help='Nebula Graph username')
    parser.add_argument('--password', default='nebula', help='Nebula Graph password')
    parser.add_argument('--wait', type=int, default=20, help='Seconds to wait before rebuilding (default: 20)')
    parser.add_argument('--indexes', nargs='+', help='Specific indexes to rebuild (if not specified, rebuilds all)')
    parser.add_argument('--list', action='store_true', help='List existing indexes without rebuilding')
    
    args = parser.parse_args()
    
    rebuilder = IndexRebuilder(args.host, args.port, args.username, args.password)
    
    if args.list:
        logger.info("Listing existing indexes...")
        indexes = rebuilder.get_existing_indexes(args.space_name)
        if indexes:
            print(f"Indexes in space '{args.space_name}':")
            for idx in indexes:
                print(f"  - {idx}")
        else:
            print(f"No indexes found in space '{args.space_name}'")
    else:
        if args.indexes:
            logger.info(f"Rebuilding specific indexes: {args.indexes}")
            rebuilder.rebuild_specific_indexes(args.space_name, args.indexes, args.wait)
        else:
            logger.info("Rebuilding all indexes...")
            rebuilder.rebuild_indexes(args.space_name, args.wait)

if __name__ == "__main__":
    main()
