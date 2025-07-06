# Working with MPQ Archives in Icecap

This guide will help you understand how to work with MPQ (Mo'PaQ) archives, which are proprietary archive files used by Blizzard Entertainment games like World of Warcraft.

## What are MPQ Files?

MPQ (Mo'PaQ or Mike O'Brien Pack) is a proprietary archive format developed by Blizzard Entertainment for their games. These archives contain game data such as textures, models, sounds, and other resources. Understanding how to work with MPQ files allows you to extract and analyze game resources.


## Basic Usage

Use an external tool such as `MPQ editor` to browse the resources and explore the assets layout. Once you are ready to access the resources programmatically, proceed to the next sections.

### Opening an MPQ Archive

To work with an MPQ archive, you first need to open it using the `MPQArchive` class:

```python
from icecap.infrastructure.resource.mpq.archive import MPQArchive

# Open an MPQ archive
archive = MPQArchive("path/to/your/archive.mpq")
```

### Listing Files in an Archive

You can get a list of all files contained in the archive:

```python
# Get a list of all files in the archive
file_list = archive.get_file_names()

# Print the first 10 files
for filename in file_list[:10]:
    print(filename)
```

### Reading Files from an Archive

To read a specific file from the archive:

```python
# Read a file from the archive
filename = "Textures/Minimap/md5translate.trs"
file_data = archive.read_file(filename)

# If the file is a text file, you can decode it
if file_data:
    text_content = file_data.decode()
    print(text_content[:300])  # Print the first 300 characters
```

### Checking if a File Exists

You can check if a specific file exists in the archive:

```python
# Check if a file exists
filename = "Textures/Minimap/md5translate.trs"
if archive.file_exists(filename):
    print(f"The file '{filename}' exists in the archive.")
else:
    print(f"The file '{filename}' does not exist in the archive.")
```

## Advanced Usage

### Working with Hash Functions

MPQ archives use hash functions for file lookup. You can calculate these hashes for a filename:

```python
from icecap.infrastructure.resource.mpq.enums import HashType

# Calculate hash values for a filename
filename = "Textures/Minimap/md5translate.trs"
hash_a = archive.crypt.hash(filename, HashType.HASH_A)
hash_b = archive.crypt.hash(filename, HashType.HASH_B)

print(f"Hash A: {hex(hash_a)}")
print(f"Hash B: {hex(hash_b)}")
```

### Accessing Archive Metadata

You can access metadata about the archive:

```python
# Get the archive header
header = archive.get_header()
print(f"Archive format version: {header.format_version}")
print(f"Block size: {header.block_size}")
print(f"Hash table size: {header.hash_table_size}")
print(f"Block table size: {header.block_table_size}")

# Get the hash table
hash_table = archive.get_hash_table()
print(f"Number of hash table entries: {len(hash_table.entries)}")

# Get the block table
block_table = archive.get_block_table()
print(f"Number of block table entries: {len(block_table.entries)}")
```

### Understanding File Flags

Files in MPQ archives have flags that indicate their properties:

```python
from icecap.infrastructure.resource.mpq.flags import (
    MPQ_FILE_EXISTS,
    MPQ_FILE_ENCRYPTED,
    MPQ_FILE_COMPRESS,
    MPQ_FILE_SINGLE_UNIT,
)

# Get a hash table entry for a file
hash_entry = archive.get_hash_table_entry(filename)
if hash_entry:
    # Get the corresponding block table entry
    block_entry = archive.get_block_table().entries[hash_entry.block_index]
    
    # Check file flags
    print(f"File exists: {bool(block_entry.flags & MPQ_FILE_EXISTS)}")
    print(f"File is encrypted: {bool(block_entry.flags & MPQ_FILE_ENCRYPTED)}")
    print(f"File is compressed: {bool(block_entry.flags & MPQ_FILE_COMPRESS)}")
    print(f"File is a single unit: {bool(block_entry.flags & MPQ_FILE_SINGLE_UNIT)}")
    
    # Print file sizes
    print(f"Compressed size: {block_entry.compressed_size} bytes")
    print(f"Uncompressed size: {block_entry.uncompressed_size} bytes")
```

## Complete Example

Here's a complete example that demonstrates how to open an MPQ archive, list its contents, and read a specific file:

```python
from icecap.infrastructure.resource.mpq.archive import MPQArchive
from icecap.infrastructure.resource.mpq.enums import HashType

# Open an MPQ archive
archive = MPQArchive("path/to/your/archive.mpq")

# Get a list of all files in the archive
file_list = archive.get_file_names()
print(f"The archive contains {len(file_list)} files.")

# Find files matching a pattern
texture_files = [f for f in file_list if f.startswith("Textures/")]
print(f"Found {len(texture_files)} texture files.")

# Read a specific file
if texture_files:
    filename = texture_files[0]
    file_data = archive.read_file(filename)
    
    if file_data:
        print(f"Successfully read '{filename}' ({len(file_data)} bytes)")
        
        # Calculate hash values for the filename
        hash_a = archive.crypt.hash(filename, HashType.HASH_A)
        hash_b = archive.crypt.hash(filename, HashType.HASH_B)
        
        print(f"Filename: {filename}")
        print(f"Hash A: {hex(hash_a)}")
        print(f"Hash B: {hex(hash_b)}")
```

## Next Steps

Now that you understand how to work with MPQ archives, you can:

- Extract game resources for analysis
- Create tools to browse and extract MPQ contents
- Analyze game data for research purposes

For more information about the MPQ format, check out the [WoWDev Wiki](https://wowdev.wiki/MPQ).