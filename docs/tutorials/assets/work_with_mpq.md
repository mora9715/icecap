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

### Complete Example

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

## Working with Archive Chains

World of Warcraft uses multiple MPQ archives to store game data. These archives are loaded in a specific priority order, allowing newer content to override older content without replacing entire archives. This system is known as an "archive chain."

### Understanding Archive Chains

In WoW, when the game needs to read a file, it checks multiple archives in order of priority:

1. Patch archives (highest priority)
2. Expansion-specific archives
3. Base game archives
4. Common archives (lowest priority)

This allows game updates to modify only specific files while leaving the rest untouched. The `MPQArchiveChain` class in Icecap implements this same behavior.

### Creating an Archive Chain

To work with multiple archives in a priority order, use the `MPQArchiveChain` class:

```python
from icecap.infrastructure.resource.mpq import MPQArchiveChain

# Create an archive chain with default WoW priorities
chain = MPQArchiveChain()
```

### Adding Archives to the Chain

You can add multiple archives to the chain. The chain will automatically determine the priority based on the archive name:

```python
from icecap.infrastructure.resource.mpq import MPQArchive, MPQArchiveChain

# Create an archive chain
chain = MPQArchiveChain()

# Add archives to the chain
base_archive = MPQArchive("path/to/base.mpq")
patch_archive = MPQArchive("path/to/patch.mpq")

chain.add_archive(base_archive)
chain.add_archive(patch_archive)
```

### Reading Files from the Chain

When reading a file from the chain, it will check each archive in order of priority until it finds the file:

```python
# Read a file from the chain
filename = "Textures/Minimap/md5translate.trs"
file_data = chain.read_file(filename)

if file_data:
    print(f"Successfully read '{filename}' from the archive chain")
```

### Understanding WoW Archive Priorities

The default priority system used by `MPQArchiveChain` matches the one used by World of Warcraft:

```python
WOW_ARCHIVE_PRIORITIES = (
    r"patch-([a-z]+)-(\d+)",  # Highest priority (e.g., patch-enUS-3)
    r"patch-(\d+)",           # (e.g., patch-2)
    "patch",                  # (e.g., patch.mpq)
    r"lichking-([a-z]+)",     # (e.g., lichking-enUS)
    r"lichking",              # (e.g., lichking.mpq)
    r"expansion-([-a-z]+)",   # (e.g., expansion-enUS)
    "expansion",              # (e.g., expansion.mpq)
    r"base-([a-z]+)",         # (e.g., base-enUS)
    "base",                   # (e.g., base.mpq)
    r"locale-([a-z]+)",       # (e.g., locale-enUS)
    r"common-(\d+)",          # (e.g., common-2)
    "common",                 # (e.g., common.mpq)
    ".*",                     # Lowest priority (any other archives)
)
```

Archives are matched against these patterns in order, and the first match determines the archive's priority.

### Complete Chain Example

Here's a complete example that demonstrates how to use an archive chain to read files from multiple archives:

```python
from icecap.infrastructure.resource.mpq import MPQArchive, MPQArchiveChain

# Create an archive chain
chain = MPQArchiveChain()

# Add multiple archives to the chain
base_archive = MPQArchive("path/to/base.mpq")
expansion_archive = MPQArchive("path/to/expansion.mpq")
patch_archive = MPQArchive("path/to/patch.mpq")

# Add archives to the chain (order doesn't matter as priority is determined by name)
chain.add_archive(base_archive)
chain.add_archive(expansion_archive)
chain.add_archive(patch_archive)

# Read a file that might exist in multiple archives
filename = "Textures/Minimap/md5translate.trs"
file_data = chain.read_file(filename)

if file_data:
    print(f"Successfully read '{filename}' from the archive chain")
    print(f"File size: {len(file_data)} bytes")

    # The chain automatically used the highest priority archive that contains the file
    # In this case, if the file exists in patch.mpq, it will be read from there
    # even if it also exists in base.mpq or expansion.mpq
```

## Next Steps

Now that you understand how to work with MPQ archives and archive chains, you can:

- Extract game resources for analysis
- Create tools to browse and extract MPQ contents
- Analyze game data for research purposes
- Work with multiple archives in the same way WoW does

For more information about the MPQ format, check out the [WoWDev Wiki](https://wowdev.wiki/MPQ).
