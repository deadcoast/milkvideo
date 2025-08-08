#!/usr/bin/env python3
"""
Test script for batch functionality.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from videomilker.config.config_manager import ConfigManager
from videomilker.core.batch_processor import BatchProcessor
from videomilker.core.file_manager import FileManager
from rich.console import Console

def test_batch_functionality():
    """Test the batch functionality."""
    console = Console()
    
    # Load configuration
    config_manager = ConfigManager()
    settings = config_manager.load_config()
    
    # Create components
    batch_processor = BatchProcessor(settings, console)
    file_manager = FileManager(settings)
    
    print("Testing Batch Functionality")
    print("=" * 40)
    
    # Test 1: Get batch folder
    print("\n1. Testing batch folder:")
    batch_folder = file_manager.get_batch_folder()
    print(f"Batch folder: {batch_folder}")
    
    # Test 2: Create batch template
    print("\n2. Testing batch template creation:")
    template_path = batch_folder / "test_template.txt"
    try:
        batch_processor.create_batch_template(template_path)
        print(f" Template created: {template_path}")
    except Exception as e:
        print(f" Failed to create template: {e}")
    
    # Test 3: Load URLs from sample file
    print("\n3. Testing URL loading from sample file:")
    sample_file = Path("sample_batch.txt")
    if sample_file.exists():
        try:
            urls = batch_processor.load_urls_from_file(sample_file)
            print(f" Loaded {len(urls)} URLs from sample file")
            for i, url in enumerate(urls[:3]):  # Show first 3
                print(f"  {i+1}. {url}")
            if len(urls) > 3:
                print(f"  ... and {len(urls) - 3} more")
        except Exception as e:
            print(f" Failed to load URLs: {e}")
    else:
        print(" Sample file not found")
    
    # Test 4: Validate batch file
    print("\n4. Testing batch file validation:")
    if sample_file.exists():
        try:
            validation = batch_processor.validate_batch_file(sample_file)
            print(f" Validation results:")
            print(f"  Total URLs: {validation['total_urls']}")
            print(f"  Valid URLs: {validation['valid_urls']}")
            print(f"  Invalid URLs: {validation['invalid_urls']}")
        except Exception as e:
            print(f" Failed to validate: {e}")
    
    print("\n" + "=" * 40)
    print("Batch functionality test completed!")

if __name__ == "__main__":
    test_batch_functionality() 