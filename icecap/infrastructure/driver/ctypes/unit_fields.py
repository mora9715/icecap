from .base import CTypeMixin
from dataclasses import dataclass, field
import ctypes


@dataclass(frozen=True, slots=True)
class UnitFields(CTypeMixin):
    """Structure representing the fields of a unit."""

    guid: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    type: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    entry: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    scale_x: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    padding: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    charm: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    summon: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    critter: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    charmed_by: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    summoned_by: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    created_by: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    target: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    channel_object: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ulonglong})
    channel_spell: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    bytes_0_race: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    bytes_0_class: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    bytes_0_gender: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    bytes_0_power_type: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint8})
    health: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power3: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power4: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power5: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power6: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power7: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_health: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power3: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power4: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power5: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power6: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    max_power7: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_regen_flat_modifier_mana: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_flat_modifier_rage: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_flat_modifier_focus: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_flat_modifier_energy: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_flat_modifier_happiness: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_flat_modifier_runes: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_flat_modifier_runic_power: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_mana: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_rage: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_focus: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_energy: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_happiness: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_runes: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    power_regen_interrupted_flat_modifier_runic_power: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    level: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    faction_template: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    virtual_item_slot_id_0: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    virtual_item_slot_id_1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    virtual_item_slot_id_2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    flags: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    flags_2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    aurastate: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    base_attack_time_primary: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    base_attack_time_secondary: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    ranged_attack_time: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    bounding_radius: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    combat_reach: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    display_id: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    native_display_id: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    mount_display_id: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    min_damage: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    max_damage: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    min_offhand_damage: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    max_offhand_damage: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    bytes_1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pet_number: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pet_name_timestamp: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pet_experience: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pet_next_level_exp: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    dynamic_flags: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    mod_cast_speed: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    created_by_spell: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    npc_flags: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    npc_emote_state: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    stat0: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    stat1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    stat2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    stat3: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    stat4: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pos_stat0: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pos_stat1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pos_stat2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pos_stat3: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    pos_stat4: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    neg_stat0: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    neg_stat1: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    neg_stat2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    neg_stat3: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    neg_stat4: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_normal: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_holy: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_fire: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_nature: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_frost: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_shadow: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_arcane: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    resistance_buff_mods_positive_normal: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_positive_holy: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_positive_fire: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_positive_nature: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_positive_frost: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_positive_shadow: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_positive_arcane: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_normal: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_holy: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_fire: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_nature: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_frost: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_shadow: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    resistance_buff_mods_negative_arcane: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint}
    )
    base_mana: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    base_health: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    bytes_2: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    attack_power: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    attack_power_mod_positive: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ushort})
    attack_power_mod_negative: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_ushort})
    attack_power_multiplier: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    ranged_attack_power: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    ranged_attack_power_mod_positive: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_ushort}
    )
    ranged_attack_power_mod_negative: int = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_ushort}
    )
    ranged_attack_power_multiplier: float = field(
        metadata={CTypeMixin.METADATA_KEY: ctypes.c_float}
    )
    min_ranged_damage: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    max_ranged_damage: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_modifier_normal: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_modifier_holy: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_modifier_fire: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_modifier_nature: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_modifier_frost: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_modifier_shadow: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_modifier_arcane: int = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_uint})
    power_cost_multiplier_normal: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_multiplier_holy: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_multiplier_fire: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_multiplier_nature: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_multiplier_frost: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_multiplier_shadow: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    power_cost_multiplier_arcane: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    max_health_modifier: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
    hover_height: float = field(metadata={CTypeMixin.METADATA_KEY: ctypes.c_float})
