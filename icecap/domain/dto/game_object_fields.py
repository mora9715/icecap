from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameObjectFields:
    """Data class representing the fields of a game object.

    **Important note:** The DTO does not contain all fields of the game object.
    For ah exhaustive list of available data, please refer to the **C structs**
    definitions in the infrastructure layer.

    """

    entry_id: int
    """The entry ID of the game object.
    
    It indicates the game which template to use when placing the object in the world.
    """

    display_id: int
    """The display ID of the game object.
    
    It is used to determine the visual representation of the game object.
    """

    owner_guid: int
    """The GUID of the owner of the game object."""

    state: int
    """The state of the game object.
    
    For example, it can be used to check if a bobber is bobbing or not.
    """
