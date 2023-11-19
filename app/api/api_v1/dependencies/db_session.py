import re
from typing import Any

from sqlalchemy import column, or_, select, true
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select
from sqlmodel import Session

import app.db.models as db
from app.api.api_v1.dependencies.filter_params import FilterParameters
from app.db.engine import engine
from app.db.get_char_details import get_character_properties
from app.schemas.enums import CharPropertyGroup
from app.schemas.util import flatten_list2d

CHAR_TABLES = [db.UnicodeCharacter, db.UnicodeCharacterUnihan]


def get_session():
    with Session(engine) as session:
        yield DBSession(session, engine)


class DBSession:
    def __init__(self, session: Session, engine: Engine):
        self.session = session
        self.engine = engine

    def get_character_properties(
        self, codepoint: int, show_props: list[CharPropertyGroup] | None, verbose: bool
    ) -> dict[str, Any]:
        return get_character_properties(self.engine, codepoint, show_props, verbose)

    def filter_all_characters(self, filter_params: FilterParameters) -> list[int]:
        queries = [
            query for table in CHAR_TABLES if (query := construct_filter_query(filter_params, table)) is not None
        ]
        return apply_filter(self.session, queries)


def construct_filter_query(  # noqa: C901
    filter_params: FilterParameters, table: db.UnicodeCharacter | db.UnicodeCharacterUnihan
) -> Select | None:
    if table == db.UnicodeCharacter and filter_params.cjk_definition:
        return None
    query = select(column("codepoint_dec")).select_from(table)
    if filter_params.name:
        char_name_regex = f"\\b{filter_params.name.upper()}\\b"
        query = query.where(column("name").regexp_match(char_name_regex))
    if filter_params.cjk_definition:
        cjk_def_regex = f"\\b{filter_params.cjk_definition.lower()}\\b"
        query = query.where(column("description").regexp_match(cjk_def_regex))
    if filter_params.blocks:
        query = query.where(column("block_id").in_(filter_params.blocks))
    if filter_params.categories:
        filtered_categories = flatten_list2d([cat.values for cat in filter_params.categories])
        query = query.where(column("general_category").in_(filtered_categories))
    if filter_params.age_list:
        query = query.where(column("age").in_(filter_params.age_list))
    if filter_params.scripts:
        script_conditions = [column("script_extensions").contains(script.code) for script in filter_params.scripts]
        query = query.where(or_(*script_conditions))
    if filter_params.bidi_class_list:
        query = query.where(column("bidirectional_class").in_(filter_params.bidi_class_list))
    if filter_params.decomp_types:
        query = query.where(column("decomposition_type").in_(filter_params.decomp_types))
    if filter_params.line_break_types:
        query = query.where(column("line_break").in_(filter_params.line_break_types))
    if filter_params.ccc_list:
        query = query.where(column("combining_class").in_(filter_params.ccc_list))
    if filter_params.num_types:
        query = query.where(column("numeric_type").in_(filter_params.num_types))
    if filter_params.join_types:
        query = query.where(column("joining_type").in_(filter_params.join_types))
    if filter_params.flags and len(filter_params.flags) > 0:
        flag_conditions = [column(flag.db_column_name) == true() for flag in filter_params.flags if flag]
        query = query.where(or_(*flag_conditions))

    return query


def apply_filter(session: Session, queries: list[Select]) -> list[int]:
    matching_codepoints = []
    for query in queries:
        results = session.execute(query).scalars().all()
        matching_codepoints.extend(results)
    return sorted(set(matching_codepoints))
