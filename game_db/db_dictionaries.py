"""Dictionary builders for status and platform dictionaries."""

from __future__ import annotations

import configparser
import logging
import os

logger = logging.getLogger("game_db.sql")


class DictionariesBuilder:
    """Build SQL for dictionaries (status/platform)."""

    def __init__(
        self,
        table_names: configparser.ConfigParser,
        column_table_names: configparser.ConfigParser,
        values_dictionaries: configparser.ConfigParser,
    ) -> None:
        self.table_names = table_names
        self.column_table_names = column_table_names
        self.values_dictionaries = values_dictionaries

    def create_dml_dictionaries(self, sql_dictionaries: str) -> None:
        """Generate SQL inserts for dictionaries from values_dictionaries.ini.

        Dynamically generates SQL INSERT statements for all statuses and platforms
        defined in values_dictionaries.ini, so new entries only need to be added
        to the configuration file.
        """
        if os.path.isfile(sql_dictionaries):
            os.remove(sql_dictionaries)

        with open(sql_dictionaries, "a+", encoding="utf-8") as f:
            # Generate status dictionary inserts
            status_table = self.table_names["TABLES"]["status_dictionary"]
            status_name_col = self.column_table_names["status_dictionary"][
                "status_name"
            ]
            f.write("INSERT INTO " f"{status_table} " f"({status_name_col})\n")
            f.write("VALUES\n")

            # Dynamically iterate over all status entries
            status_items = list(self.values_dictionaries["STATUS"].items())
            for idx, (key, value) in enumerate(status_items):
                if idx == len(status_items) - 1:
                    # Last item - no comma
                    f.write(f'   ("{value}");\n')
                else:
                    f.write(f'   ("{value}"),\n')

            # Generate platform dictionary inserts
            platform_table = self.table_names["TABLES"]["platform_dictionary"]
            platform_name_col = self.column_table_names["platform_dictionary"][
                "platform_name"
            ]
            f.write("INSERT INTO " f"{platform_table} " f"({platform_name_col})\n")
            f.write("VALUES\n")

            # Dynamically iterate over all platform entries
            platform_items = list(self.values_dictionaries["PLATFORM"].items())
            for idx, (key, value) in enumerate(platform_items):
                if idx == len(platform_items) - 1:
                    # Last item - no comma
                    f.write(f'   ("{value}");\n')
                else:
                    f.write(f'   ("{value}"),\n')
