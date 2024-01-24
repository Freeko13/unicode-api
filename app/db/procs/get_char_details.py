import operator
from functools import reduce
from typing import Any

from sqlalchemy.engine import Engine
from sqlmodel import column, select

import app.db.models as db
from app.data.cache import cached_data
from app.db.character_props import PROPERTY_GROUPS
from app.schemas.enums import CharacterFilterFlags, CharPropertyGroup


def get_character_properties(
    engine: Engine, codepoint: int, show_props: list[CharPropertyGroup] | None, verbose: bool
) -> dict[str, Any]:
    group_dicts = [get_prop_values(engine, codepoint, group) for group in get_prop_groups(codepoint, show_props)]
    character_props = reduce(operator.ior, group_dicts, {})
    return trim_irrelevent_values(codepoint, character_props) if not verbose else character_props


def get_prop_groups(codepoint: int, show_props: list[CharPropertyGroup] | None) -> list[CharPropertyGroup]:
    unihan = cached_data.character_is_unihan(codepoint)
    show_props = show_props or []
    # If all property groups are requested, return appropriate property groups for non-unihan/unihan
    if CharPropertyGroup.ALL in show_props:
        return (
            CharPropertyGroup.get_all_non_unihan_character_prop_groups()
            if not unihan
            else CharPropertyGroup.get_all_unihan_character_prop_groups()
        )
    # else, ensure that the Minimum property group appropriate for non-unihan/unihan is included
    show_props = [
        prop_group
        for prop_group in show_props
        if prop_group not in [CharPropertyGroup.MINIMUM, CharPropertyGroup.CJK_MINIMUM]
    ]
    show_props += [CharPropertyGroup.MINIMUM] if not unihan else [CharPropertyGroup.CJK_MINIMUM]
    # if Basic property group is requested, ensure property group appropriate for non-unihan/unihan is included
    if CharPropertyGroup.BASIC in show_props or CharPropertyGroup.CJK_BASIC in show_props:
        show_props = [
            prop_group
            for prop_group in show_props
            if prop_group not in [CharPropertyGroup.BASIC, CharPropertyGroup.CJK_BASIC]
        ]
        show_props += [CharPropertyGroup.BASIC] if not unihan else [CharPropertyGroup.CJK_BASIC]
    # then, if character is non-unihan, ensure that any unihan-specific property groups are not included
    if not unihan and any("CJK" in prop_group.name for prop_group in show_props):
        show_props = [prop_group for prop_group in show_props if "CJK" not in prop_group.name]
    return show_props


def get_prop_values(engine: Engine, codepoint: int, prop_group: CharPropertyGroup) -> dict[str, Any]:
    columns = [column(prop_map["name_in"]) for prop_map in PROPERTY_GROUPS[prop_group] if prop_map["db_column"]]
    char_props = get_prop_values_from_database(engine, codepoint, columns) if columns else {"codepoint_dec": codepoint}
    return {prop_map["name_out"]: prop_map["response_value"](char_props) for prop_map in PROPERTY_GROUPS[prop_group]}


def get_prop_values_from_database(engine: Engine, codepoint: int, columns):
    char_props = {"codepoint_dec": codepoint}
    table = db.UnicodeCharacter if cached_data.character_is_non_unihan(codepoint) else db.UnicodeCharacterUnihan
    query = select(*columns).select_from(table).where(column("codepoint_dec") == codepoint)
    with engine.connect() as con:
        for row in con.execute(query):
            char_props.update(dict(row._mapping))
    return char_props


def trim_irrelevent_values(codepoint: int, response_dict: dict[str, Any]) -> dict[str, Any]:
    for prop_name in get_prop_names_with_irrelevant_values(codepoint, response_dict):
        response_dict.pop(prop_name)
    return response_dict


def get_prop_names_with_irrelevant_values(codepoint: int, char_props: dict[str, Any]) -> list[str]:
    remove_props = (
        get_unset_flag_properties(char_props)
        + remove_irrelevant_casing_properties(char_props, codepoint)
        + remove_irrelevant_indic_properties(char_props)
        + get_all_other_properties_with_irrelevant_values(char_props, codepoint)
    )
    if cached_data.character_is_unihan(codepoint):
        remove_props.extend(get_unihan_prop_names_with_null_values(char_props))
    return list(set(remove_props))


def get_unihan_prop_names_with_null_values(char_props: dict[str, Any]) -> list[str]:
    unihan_list_properties = [
        "traditional_variant",
        "simplified_variant",
        "z_variant",
        "compatibility_variant",
        "semantic_variant",
        "specialized_semantic_variant",
        "spoofing_variant",
    ]
    remove_list_props = [
        prop_name for prop_name in unihan_list_properties if prop_name in char_props and char_props[prop_name] == [""]
    ]

    unihan_properties = [
        "ideo_frequency",
        "ideo_grade_level",
        "rs_count_unicode",
        "rs_count_kangxi",
        "total_strokes",
        "accounting_numeric",
        "primary_numeric",
        "other_numeric",
        "hangul",
        "cantonese",
        "mandarin",
        "japanese_kun",
        "japanese_on",
        "vietnamese",
    ]
    remove_props = [
        prop_name for prop_name in unihan_properties if prop_name in char_props and not char_props[prop_name]
    ]
    return remove_list_props + remove_props


def get_unset_flag_properties(char_props: dict[str, Any]) -> list[str]:
    return [
        flag.db_column_name
        for flag in get_removable_flag_properties(char_props)
        if flag.db_column_name in char_props and not char_props[flag.db_column_name]
    ]


def get_removable_flag_properties(char_props: dict[str, Any]) -> list[CharacterFilterFlags]:
    removable_flags = list(CharacterFilterFlags)
    set_flag_props = [
        flag for flag in CharacterFilterFlags if flag.db_column_name in char_props and char_props[flag.db_column_name]
    ]
    if any(CharacterFilterFlags.is_emoji_flag(flag) for flag in set_flag_props):
        removable_flags = [
            flag for flag in CharacterFilterFlags if int(CharacterFilterFlags.EMOJI_GROUP) & flag != flag
        ]
    return removable_flags


def remove_irrelevant_casing_properties(char_props: dict[str, Any], codepoint: int) -> list[str]:
    remove_props = []
    if "uppercase" in char_props and not char_props["uppercase"]:
        remove_props.append("uppercase")
    if "lowercase" in char_props and not char_props["lowercase"]:
        remove_props.append("lowercase")

    other_casing_props = [
        "simple_uppercase_mapping",
        "simple_lowercase_mapping",
        "simple_titlecase_mapping",
        "simple_case_folding",
    ]
    remove_props.extend(
        prop_name
        for prop_name in other_casing_props
        if prop_name in char_props
        and (
            char_props[prop_name] == cached_data.get_mapped_codepoint_from_int(codepoint) or char_props[prop_name] == ""
        )
    )
    return remove_props


def remove_irrelevant_indic_properties(char_props: dict[str, Any]) -> list[str]:
    indic_properties = [
        "indic_syllabic_category",
        "indic_matra_category",
        "indic_positional_category",
    ]
    if (
        all(prop_name in char_props for prop_name in indic_properties)
        and "Other" in char_props["indic_syllabic_category"]
        and "NA" in char_props["indic_matra_category"]
        and "NA" in char_props["indic_positional_category"]
    ):
        return indic_properties
    return []


def get_all_other_properties_with_irrelevant_values(char_props: dict[str, Any], codepoint: int) -> list[str]:
    remove_props = []
    if "description" in char_props and not char_props["description"]:
        remove_props.append("description")

    if (
        "bidirectional_is_mirrored" in char_props
        and "bidirectional_mirroring_glyph" in char_props
        and not char_props["bidirectional_is_mirrored"]
    ):
        remove_props.append("bidirectional_mirroring_glyph")

    if ("paired_bracket_type" in char_props and "None" in char_props["paired_bracket_type"]) and (
        "paired_bracket_property" in char_props and char_props["codepoint"] in char_props["paired_bracket_property"]
    ):
        remove_props.append("paired_bracket_type")
        remove_props.append("paired_bracket_property")

    if "decomposition_type" in char_props and "None" in char_props["decomposition_type"]:
        remove_props.append("decomposition_type")

    if "numeric_type" in char_props and "None" in char_props["numeric_type"]:
        remove_props.append("numeric_type")
        remove_props.append("numeric_value")
        remove_props.append("numeric_value_parsed")

    if "joining_type" in char_props and "Non Joining" in char_props["joining_type"]:
        remove_props.append("joining_type")
        remove_props.append("joining_group")

    if "hangul_syllable_type" in char_props and "Not Applicable" in char_props["hangul_syllable_type"]:
        remove_props.append("hangul_syllable_type")

    if "equivalent_unified_ideograph" in char_props and not char_props["equivalent_unified_ideograph"]:
        remove_props.append("equivalent_unified_ideograph")

    return remove_props
