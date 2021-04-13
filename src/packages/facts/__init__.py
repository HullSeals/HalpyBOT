"""
This module is due for a rewrite, and not documented.
"""

from .facthandler import (on_connect, clear_facts, get_facts,
                          add_fact, remove_fact, recite_fact,
                          facts, fact_index, basic_facts, update_fact_index,
                          get_offline_facts)

__all__ = ["on_connect",
           "clear_facts",
           "get_facts",
           "add_fact",
           "remove_fact",
           "recite_fact",
           "facts",
           "fact_index",
           "basic_facts",
           "update_fact_index",
           "get_offline_facts"]
