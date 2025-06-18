#### Global Offsets ####
CLIENT_CONNECTION_OFFSET = 0x00C79CE0
LOCAL_PLAYER_GUID_STATIC_OFFSET = 0x00CA1238

#### Object Manager Offsets ####
# Relative to the client connection address.
OBJECT_MANAGER_OFFSET = 0x2ED0

# Relative to object manager address.
FIRST_OBJECT_OFFSET = 0xAC

# Relative to the object manager address.
LOCAL_PLAYER_GUID_OFFSET = 0xC0

#### Object Offsets ####
# Relative to the object address.
OBJECT_TYPE_OFFSET = 0x14

# Relative to the object address.
OBJECT_GUID_OFFSET = 0x30

# Relative to the object address.
NEXT_OBJECT_OFFSET = 0x3C

# Relative to the object address.
OBJECT_X_POSITION_OFFSET = 0x79C

# Relative to the object address.
OBJECT_Y_POSITION_OFFSET = 0x798

# Relative to the object address.
OBJECT_Z_POSITION_OFFSET = 0x7A0

# Relative to the object address.
OBJECT_ROTATION_OFFSET = 0x7A8

# Relative to the object address.
OBJECT_FIELDS_OFFSET = 0x8

# Relative to the unit fields address.
OBJECT_LEVEL_OFFSET = 0xD8
OBJECT_HIT_POINTS_OFFSET = 0x60
OBJECT_ENERGY_OFFSET = 0x64
OBJECT_MAX_HIT_POINTS_OFFSET = 0x80
OBJECT_MAX_ENERGY_OFFSET = 0x84
OBJECT_UNIT_BYTE_0_OFFSET = 0x5C


# Relative to the object address.
UNIT_NAMEBLOCK_OFFSET = 0x964
UNIT_NAMEBLOCK_NAME_OFFSET = 0x5C


#### Name Store Offsets ####
NAME_STORE_BASE = 0x00C5D938 + 0x8
NAME_MASK_OFFSET = 0x24
NAME_TABLE_ADDRESS_OFFSET = 0x1C
NAME_NODE_NAME_OFFSET = 0x20


#### Game object Offsets ####
# Relative to the descriptor address.

OBJECT_CREATED_BY_OFFSET = 0x18
OBJECT_DISPLAY_ID_OFFSET = 0x20
OBJECT_ENTRY_ID_OFFSET = 0xC
