"""Этапы канбан-доски, управляемые из интерфейса.

Скелет: реализация появится после того, как тесты покажут красный.
"""

import frappe


def sync_field_options(doc, method=None):
	pass


@frappe.whitelist()
def rename_stage(board_name: str, old_name: str, new_name: str):
	pass
