# OpenVPN Config Extractor

A command-line tool for extracting OpenVPN configuration files from binary data sources such as memory dumps, backups, or disk images.

## Overview

OpenVPN Config Extractor scans binary files for patterns that match OpenVPN configuration blocks and extracts them into separate `.ovpn` files. This can be useful for forensic analysis, data recovery, or extracting configs from system backups.

## Features

- Extract OpenVPN configurations from any binary file
- Process multiple files in a single command
- Customizable output location and file naming
- Robust detection of various OpenVPN config formats
- **Custom pattern specification** to precisely target specific config formats
- Filtering options to reduce false positives
- Detailed logging for troubleshooting

## Installation

### Prerequisites

- Python 3.6 or higher

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ovpn-extractor.git
cd ovpn-extractor

# Make the script executable
chmod +x ovpn-extractor.py
```

### Optional: Install as a global command

```bash
# Create a symbolic link in a directory in your PATH
sudo ln -s "$(pwd)/ovpn-extractor.py" /usr/local/bin/ovpn-extractor
```

## Usage

### Basic Usage

```bash
./ovpn-extractor.py -f <binary_file>
```

This will scan the binary file and save any found OpenVPN configurations as `config_1.ovpn`, `config_2.ovpn`, etc. in the current directory.

### Advanced Options

```bash
./ovpn-extractor.py -f <binary_file1> <binary_file2> -o ./configs -p vpn_ -m 50 -v
```

#### Arguments

| Option | Description |
|--------|-------------|
| `-f, --files` | Binary file(s) to extract OpenVPN configurations from (required) |
| `-o, --output-dir` | Directory to save extracted configurations |
| `-p, --prefix` | Prefix for output filenames (default: `config_`) |
| `-m, --min-length` | Minimum config length in lines to be considered valid (default: 50) |
| `--start-pattern` | Custom pattern(s) to identify the start of an OpenVPN config |
| `--end-pattern` | Custom pattern(s) to identify the end of an OpenVPN config |
| `-v, --verbose` | Enable verbose output |
| `-h, --help` | Show help message and exit |

### Examples

#### Extract configs from a memory dump

```bash
./ovpn-extractor.py -f mem_dump.bin
```

#### Extract configs with custom output directory and prefix

```bash
./ovpn-extractor.py -f backup.bin -o ./configs -p vpn_
```

#### Use custom start and end patterns

```bash
./ovpn-extractor.py -f mem_dump.bin --start-pattern "dev tun" --end-pattern "key-direction 1"
```

#### Specify multiple patterns

```bash
./ovpn-extractor.py -f mem_dump.bin --start-pattern "dev tun" "client" --end-pattern "</tls-auth>" "key-direction 1"
```

#### Process multiple files with verbose logging

```bash
./ovpn-extractor.py -f mem_dump1.bin mem_dump2.bin -v
```

## How It Works

1. The tool reads the binary file and extracts all printable ASCII strings
2. It searches for patterns indicating the start of an OpenVPN configuration
3. It captures all lines until it finds an appropriate ending pattern
4. Configurations that meet the minimum length requirement are saved as separate `.ovpn` files

## Detection Patterns

By default, the tool recognizes OpenVPN configurations by looking for common patterns:

### Default Start Patterns:
- Lines starting with `client`
- Lines starting with `# OpenVPN`
- Lines starting with `dev tun`

### Default End Patterns:
- `</tls-auth>`
- `</ca>`
- `</cert>`
- `</key>`
- `key-direction 1` or any number

### Custom Patterns:
You can override these defaults using the `--start-pattern` and `--end-pattern` arguments for more precise extraction. This is particularly useful when:

- Dealing with non-standard OpenVPN configurations
- Searching for specific configurations in large memory dumps
- Extracting partial configurations with known delimiters
- Working with binary files that contain multiple different configuration formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is provided for legitimate purposes such as data recovery and system administration. Always ensure you have appropriate authorization before extracting configurations from any system or file. The authors are not responsible for any misuse of this tool.