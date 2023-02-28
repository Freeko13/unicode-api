import json
from functools import cache, cached_property

import app.db.engine as db
from app.core.config import BLOCKS_JSON, CHAR_NAME_MAP, CHAR_NO_NAME_MAP, PLANES_JSON
from app.data.constants import (
    CJK_COMPATIBILITY_BLOCK_IDS,
    CJK_UNIFIED_BLOCK_IDS,
    CONTROL_CHARACTER_CODEPOINTS,
    MAX_CODEPOINT,
    NON_CHARACTER_CODEPOINTS,
    NULL_BLOCK,
    NULL_PLANE,
    PRIVATE_USE_BLOCK_IDS,
    SURROGATE_BLOCK_IDS,
    TANGUT_BLOCK_IDS,
)
from app.data.encoding import get_codepoint_string
from app.schemas.enums import UnassignedCharacterType


class UnicodeDataCache:
    @cached_property
    def unique_name_character_map(self) -> dict[int, str]:
        json_map = json.loads(CHAR_NAME_MAP.read_text())
        return {int(codepoint): name for (codepoint, name) in json_map.items()}

    @cached_property
    def unique_name_character_choices(self) -> dict[int, str]:
        return {codepoint: name.lower() for (codepoint, name) in self.unique_name_character_map.items()}

    @property
    def total_unique_name_characters(self) -> int:
        return len(self.unique_name_character_map)

    @cached_property
    def generic_name_character_map(self) -> dict[int, str]:
        json_map = json.loads(CHAR_NO_NAME_MAP.read_text())
        return {int(codepoint): name for (codepoint, name) in json_map.items()}

    @cached_property
    def blocks(self) -> list[db.UnicodeBlock]:
        blocks = [db.UnicodeBlock(**block) for block in json.loads(BLOCKS_JSON.read_text())]
        for block in blocks:
            block.plane = self.get_unicode_plane_containing_block_id(block.id if block.id else 0)
        return blocks

    @cached_property
    def block_id_map(self) -> dict[int, db.UnicodeBlock]:
        return {block.id: block for block in self.blocks if block and block.id}

    @cached_property
    def block_name_map(self) -> dict[str, db.UnicodeBlock]:
        return {block.name: block for block in self.blocks}

    @cached_property
    def block_name_choices(self) -> dict[int, str]:
        return {block.id: block.name.lower() for block in self.blocks if block and block.id}

    @property
    def total_block_name_choices(self) -> int:
        return len(self.blocks)

    @cached_property
    def all_characters_block(self) -> db.UnicodeBlock:
        block = db.UnicodeBlock(
            id=0,
            name="All Unicode Characters",
            plane_id=-1,
            start_dec=0,
            start="0000",
            finish_dec=1114111,
            finish="10FFFF",
            total_allocated=1114112,
            total_defined=self._calculate_total_defined_characters(),
        )
        block.plane = self.all_characters_plane
        return block

    @cached_property
    def planes(self) -> list[db.UnicodePlane]:
        return [db.UnicodePlane(**plane) for plane in json.loads(PLANES_JSON.read_text())]

    @cached_property
    def plane_number_map(self) -> dict[int, db.UnicodePlane]:
        return {plane.number: plane for plane in self.planes}

    @cached_property
    def plane_name_map(self) -> dict[str, db.UnicodePlane]:
        return {plane.name: plane for plane in self.planes}

    @cached_property
    def all_characters_plane(self) -> db.UnicodePlane:
        return db.UnicodePlane(
            number=-1,
            name="All Unicode Characters",
            abbreviation="ALL",
            start="0000",
            start_dec=0,
            finish="10FFFF",
            finish_dec=1114111,
            start_block_id=1,
            finish_block_id=327,
            total_allocated=1114112,
            total_defined=self._calculate_total_defined_characters(),
        )

    @property
    def all_assigned_codepoints(self) -> set[int]:
        return set(list(self.unique_name_character_map.keys()) + list(self.generic_name_character_map.keys()))

    def get_unicode_block_by_id(self, block_id: int) -> db.UnicodeBlock:
        return self.block_id_map.get(block_id, db.UnicodeBlock(**NULL_BLOCK))

    def get_unicode_block_by_name(self, block_name: str) -> db.UnicodeBlock:
        return self.block_name_map.get(block_name, db.UnicodeBlock(**NULL_BLOCK))

    def get_unicode_block_containing_codepoint(self, codepoint: int) -> db.UnicodeBlock:
        found = [block for block in self.blocks if block.start_dec <= codepoint and codepoint <= block.finish_dec]
        return found[0] if found else db.UnicodeBlock(**NULL_BLOCK)

    def get_unicode_plane_by_number(self, plane_number: int) -> db.UnicodePlane:
        return self.plane_number_map.get(plane_number, db.UnicodePlane(**NULL_PLANE))

    def get_unicode_plane_containing_block_id(self, block_id: int) -> db.UnicodePlane:
        found = [
            plane for plane in self.planes if plane.start_block_id <= block_id and block_id <= plane.finish_block_id
        ]
        return found[0] if found else db.UnicodePlane(**NULL_PLANE)

    def codepoint_is_assigned(self, codepoint: int) -> bool:
        return codepoint in self.all_assigned_codepoints

    def codepoint_is_surrogate(self, codepoint: int) -> bool:
        block = self.get_unicode_block_containing_codepoint(codepoint)
        return block.id in SURROGATE_BLOCK_IDS

    @cache
    def get_character_name(self, codepoint: int) -> str:
        return (
            self.get_unique_name_for_codepoint(codepoint)
            if self.character_is_uniquely_named(codepoint)
            else self.get_generic_name_for_codepoint(codepoint)
            if self.character_is_generically_named(codepoint)
            else self.get_label_for_unassigned_codepoint(codepoint)
        )

    def character_is_uniquely_named(self, codepoint: int) -> bool:
        return codepoint in self.unique_name_character_map

    def get_unique_name_for_codepoint(self, codepoint: int) -> str:
        return self.unique_name_character_map.get(codepoint, "")

    def character_is_generically_named(self, codepoint: int) -> bool:
        return codepoint in self.generic_name_character_map

    def get_generic_name_for_codepoint(self, codepoint: int) -> str:
        block = self.get_unicode_block_containing_codepoint(codepoint)
        return (
            f"CJK UNIFIED IDEOGRAPH-{codepoint:04X}"
            if block.id in CJK_UNIFIED_BLOCK_IDS
            else f"CJK COMPATIBILITY IDEOGRAPH-{codepoint:04X}"
            if block.id in CJK_COMPATIBILITY_BLOCK_IDS
            else f"TANGUT IDEOGRAPH-{codepoint:04X}"
            if block.id in TANGUT_BLOCK_IDS
            else f"{block} ({get_codepoint_string(codepoint)})"
            if block.id in SURROGATE_BLOCK_IDS or block.id in PRIVATE_USE_BLOCK_IDS
            else ""
        )

    def get_label_for_unassigned_codepoint(self, codepoint: int) -> str:
        block = self.get_unicode_block_containing_codepoint(codepoint)
        char_type = self.get_unassigned_character_type(codepoint, block)
        return (
            f"<{char_type}-{codepoint:04X}> (Block: {block.name}, Start: U+{block.start}, End: U+{block.finish})"
            if char_type == UnassignedCharacterType.RESERVED
            else f"<{char_type}-{codepoint:04X}>"
            if char_type != UnassignedCharacterType.INVALID
            else f"Invalid Codepoint ({get_codepoint_string(codepoint)})"
        )

    def get_unassigned_character_type(self, codepoint: int, block: db.UnicodeBlock) -> UnassignedCharacterType:
        return (
            UnassignedCharacterType.NONCHARACTER
            if f"{codepoint:X}" in NON_CHARACTER_CODEPOINTS
            else UnassignedCharacterType.SURROGATE
            if block.id in SURROGATE_BLOCK_IDS
            else UnassignedCharacterType.PRIVATE_USE
            if block.id in PRIVATE_USE_BLOCK_IDS
            else UnassignedCharacterType.RESERVED
            if self.codepoint_is_in_unicode_range(codepoint)
            else UnassignedCharacterType.INVALID
        )

    def codepoint_is_in_unicode_range(self, codepoint: int) -> bool:
        return codepoint >= 0 and codepoint <= MAX_CODEPOINT

    def _calculate_total_defined_characters(self) -> int:
        return len([cp for cp in self.all_assigned_codepoints if not cp in CONTROL_CHARACTER_CODEPOINTS])


cached_data = UnicodeDataCache()
