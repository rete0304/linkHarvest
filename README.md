# linkHarvest

A web crawler that traverses all pages within a website and collects links to files with specified extensions (default: `.pdf`), outputting a plain-text URL list for use with download managers.

## Features

- Crawls all pages within the same domain starting from a given URL
- Collects file links matching one or more target extensions
- Deduplicates results automatically
- Skips static assets (images, CSS, JS, fonts) to avoid unnecessary requests
- Outputs a plain-text file with one complete URL per line, compatible with `aria2c`, `wget`, and similar tools

## Requirements

```
requests
beautifulsoup4
```

Install dependencies:

```bash
pip install requests beautifulsoup4
```

## Usage

```bash
python linkHarvest.py <URL> [--ext EXT [EXT ...]] [--output FILENAME]
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `url` | *(required)* | Starting URL to crawl |
| `--ext` | `.pdf` | One or more file extensions to collect |
| `--output` | `URL列表.txt` | Output file path |

### Examples

```bash
# Collect all PDF links (default)
python linkHarvest.py https://example.com

# Collect multiple file types
python linkHarvest.py https://example.com --ext .pdf .zip .docx

# Specify output file
python linkHarvest.py https://example.com --ext .pdf --output downloads.txt
```

## Output

Each line in the output file contains one complete URL:

```
https://example.com/files/document1.pdf
https://example.com/files/document2.pdf
https://example.com/archive/report.pdf
```

The output file can be passed directly to download managers:

```bash
# aria2c
aria2c -i URL列表.txt

# wget
wget -i URL列表.txt
```

## License

MIT
