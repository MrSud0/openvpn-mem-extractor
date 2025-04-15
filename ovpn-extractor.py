#!/usr/bin/env python3
"""
OpenVPN Config Extractor - CLI tool for extracting OpenVPN configurations from binary files

This tool scans binary files for OpenVPN configuration blocks and extracts them into
separate .ovpn files. It can be used for memory dumps, binary backups, or any file
that might contain OpenVPN configurations.
"""

import re
import os
import sys
import argparse
from pathlib import Path
import logging

def setup_logging(verbose=False):
    """Configure logging based on verbosity level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def extract_strings_from_binary(file_path):
    """
    Extract printable strings from a binary file.
    
    Args:
        file_path (str): Path to the binary file to extract strings from
        
    Returns:
        list: A list of extracted strings
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        IOError: If there's an error reading the file
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Use a regular expression to find sequences of printable ASCII characters
        strings = re.findall(b'[ -~]{4,}', data)
        return [s.decode('utf-8', errors='ignore') for s in strings]
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise

def extract_ovpn_configs(strings, min_length=50, start_patterns=None, end_patterns=None):
    """
    Extract OpenVPN configuration blocks from the list of strings.
    
    Args:
        strings (list): List of strings to search for OpenVPN configurations
        min_length (int): Minimum length of a valid configuration in lines
        start_patterns (list): Custom patterns to identify the start of an OpenVPN config
        end_patterns (list): Custom patterns to identify the end of an OpenVPN config
        
    Returns:
        list: A list of complete OpenVPN configuration blocks
    """
    configs = []
    current_config = []
    capturing = False
    
    # Default patterns if none provided
    if start_patterns is None:
        start_patterns = [
            r'^client\s*$',
            r'^# OpenVPN',
            r'^dev tun'
        ]
    
    if end_patterns is None:
        end_patterns = [
            r'^</tls-auth>\s*$',
            r'^</ca>\s*$',
            r'^</cert>\s*$',
            r'^</key>\s*$',
            r'^key-direction \d+\s*$'
        ]
    
    # Compile patterns for efficiency
    start_patterns = [re.compile(pattern) for pattern in start_patterns]
    end_patterns = [re.compile(pattern) for pattern in end_patterns]
    
    for line in strings:
        line_stripped = line.strip()
        
        # Check if line matches any start pattern
        if not capturing:
            for pattern in start_patterns:
                if pattern.search(line):
                    current_config = [line]
                    capturing = True
                    logging.debug(f"Started capturing config at: {line[:30]}...")
                    break
        elif capturing:
            current_config.append(line)
            
            # Check if line matches any end pattern
            for pattern in end_patterns:
                if pattern.search(line):
                    # Only save configs that are reasonably sized
                    if len(current_config) >= min_length:
                        full_config = '\n'.join(current_config)
                        configs.append(full_config)
                        logging.debug(f"Captured config with {len(current_config)} lines")
                    else:
                        logging.debug(f"Skipped short config ({len(current_config)} lines)")
                    
                    capturing = False
                    current_config = []
                    break
    
    # Check for any unfinished configs that might still be valid
    if capturing and len(current_config) >= min_length:
        full_config = '\n'.join(current_config)
        configs.append(full_config)
        logging.debug(f"Captured final config with {len(current_config)} lines")
    
    return configs

def save_configs(configs, output_dir=None, prefix="config_"):
    """
    Save each configuration to a separate .ovpn file.
    
    Args:
        configs (list): List of OpenVPN configuration blocks to save
        output_dir (str): Directory to save the configuration files in
        prefix (str): Prefix for the output filenames
        
    Returns:
        list: Paths of the saved configuration files
    """
    saved_files = []
    
    # Create output directory if it doesn't exist
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    for idx, config in enumerate(configs):
        filename = f"{prefix}{idx + 1}.ovpn"
        if output_dir:
            filepath = os.path.join(output_dir, filename)
        else:
            filepath = filename
            
        try:
            with open(filepath, 'w') as f:
                f.write(config)
            logging.info(f"Saved: {filepath}")
            saved_files.append(filepath)
        except IOError as e:
            logging.error(f"Error saving {filepath}: {e}")
    
    return saved_files

def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract OpenVPN configurations from binary files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract configs from a memory dump
  %(prog)s -f mem_dump.bin
  
  # Extract configs with custom output directory and prefix
  %(prog)s -f backup.bin -o ./configs -p vpn_
  
  # Use custom start and end patterns
  %(prog)s -f mem_dump.bin --start-pattern "dev tun" --end-pattern "key-direction 1"
  
  # Process multiple files
  %(prog)s -f mem_dump1.bin mem_dump2.bin -v
"""
    )
    
    parser.add_argument('-f', '--files', nargs='+', required=True,
                        help='Binary file(s) to extract OpenVPN configurations from')
    parser.add_argument('-o', '--output-dir', 
                        help='Directory to save extracted configurations')
    parser.add_argument('-p', '--prefix', default='config_',
                        help='Prefix for output filenames (default: config_)')
    parser.add_argument('-m', '--min-length', type=int, default=50,
                        help='Minimum config length in lines to be considered valid (default: 50)')
    parser.add_argument('--start-pattern', nargs='+',
                        help='Custom pattern(s) to identify the start of an OpenVPN config')
    parser.add_argument('--end-pattern', nargs='+',
                        help='Custom pattern(s) to identify the end of an OpenVPN config')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    
    return parser.parse_args()

def process_file(file_path, output_dir, prefix, min_length, start_patterns, end_patterns):
    """Process a single file to extract OpenVPN configurations."""
    try:
        logging.info(f"Processing file: {file_path}")
        
        strings = extract_strings_from_binary(file_path)
        logging.info(f"Extracted {len(strings)} strings from {file_path}")
        
        configs = extract_ovpn_configs(strings, min_length, start_patterns, end_patterns)
        logging.info(f"Found {len(configs)} potential OpenVPN configurations")
        
        # Use file basename for more specific output filenames
        file_basename = os.path.splitext(os.path.basename(file_path))[0]
        file_specific_prefix = f"{prefix}{file_basename}_"
        
        saved_files = save_configs(configs, output_dir, file_specific_prefix)
        return saved_files
    except Exception as e:
        logging.error(f"Failed to process {file_path}: {e}")
        return []

def main():
    """Main entry point for the script."""
    args = parse_arguments()
    setup_logging(args.verbose)
    
    logging.info(f"OpenVPN Config Extractor starting...")
    
    all_saved_files = []
    
    for file_path in args.files:
        saved_files = process_file(
            file_path, 
            args.output_dir, 
            args.prefix, 
            args.min_length,
            args.start_pattern,
            args.end_pattern
        )
        all_saved_files.extend(saved_files)
    
    if all_saved_files:
        logging.info(f"Successfully extracted {len(all_saved_files)} OpenVPN configurations")
    else:
        logging.warning("No OpenVPN configurations were found or extracted")
    
    return 0 if all_saved_files else 1

if __name__ == '__main__':
    sys.exit(main())