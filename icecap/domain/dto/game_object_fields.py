from dataclasses import dataclass


@dataclass(frozen=True)
class GameObjectFields:
    entry_id: int
    display_id: int
    owner_guid: int
