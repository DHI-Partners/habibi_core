"""Этапы канбан-доски, управляемые из интерфейса.

Колонка канбана в Frappe — не подпись, а значение Select-поля, по которому
построена доска. Отсюда два разрыва, которые закрывает этот модуль:

1. `add_column` (frappe/desk/doctype/kanban_board/kanban_board.py:79) дописывает
   колонку только в доску, но не в Options поля, поэтому перетащить карточку
   в новую колонку невозможно — `_validate_selects`
   (frappe/model/base_document.py:1119) отвергает значение вне Options.
2. Переименования колонки в API канбана нет вообще.

Оба механизма работают ТОЛЬКО с пользовательскими Select-полями. Стандартные
поля ERPNext (status, priority) не затрагиваются ни при каких условиях: их
Options — часть схемы приложения, а не пользовательская настройка.
"""

import frappe
from frappe import _
from frappe.utils import now


def get_managed_field(board):
	"""Custom Field типа Select, по которому построена доска, иначе None."""
	if not board.reference_doctype or not board.field_name:
		return None

	name = frappe.db.get_value(
		"Custom Field",
		{"dt": board.reference_doctype, "fieldname": board.field_name},
		"name",
	)
	if not name:
		return None

	field = frappe.get_doc("Custom Field", name)
	return field if field.fieldtype == "Select" else None


def get_options(field):
	return [option for option in (field.options or "").split("\n") if option.strip()]


def set_options(field, options):
	field.options = "\n".join(options)
	field.save(ignore_permissions=True)


def sync_field_options(doc, method=None):
	"""Дописывает колонки доски в Options поля (хук on_update у Kanban Board).

	Значения из Options не удаляются даже при архивировании колонки: иначе
	документы в архивированной колонке стали бы невалидными и перестали бы
	сохраняться.
	"""
	field = get_managed_field(doc)
	if not field:
		return

	options = get_options(field)
	missing = [
		column.column_name
		for column in doc.columns
		if column.column_name and column.column_name not in options
	]
	if not missing:
		return

	set_options(field, options + missing)
	frappe.clear_cache(doctype=doc.reference_doctype)


def is_value_used_by_other_boards(board, value):
	"""Занято ли значение колонкой другой доски по тому же полю."""
	other_boards = frappe.get_all(
		"Kanban Board",
		filters={
			"reference_doctype": board.reference_doctype,
			"field_name": board.field_name,
			"name": ("!=", board.name),
		},
		pluck="name",
	)
	if not other_boards:
		return False

	return bool(
		frappe.db.exists(
			"Kanban Board Column",
			{"parent": ("in", other_boards), "column_name": value},
		)
	)


@frappe.whitelist()
def rename_stage(board_name: str, old_name: str, new_name: str):
	"""Переименовывает этап: колонку доски, значение поля и все документы."""
	old_name = (old_name or "").strip()
	new_name = (new_name or "").strip()

	if not new_name:
		frappe.throw(_("Название этапа не может быть пустым"))

	board = frappe.get_doc("Kanban Board", board_name)
	board.check_permission("write")
	if not frappe.has_permission(board.reference_doctype, "write"):
		frappe.throw(
			_("Нет прав на изменение {0}").format(_(board.reference_doctype)),
			frappe.PermissionError,
		)

	field = get_managed_field(board)
	if not field:
		frappe.throw(
			_("Переименовать этап можно только на доске по пользовательскому Select-полю")
		)

	columns = [column.column_name for column in board.columns]
	if old_name not in columns:
		frappe.throw(_("Колонка {0} на доске не найдена").format(old_name))
	if new_name == old_name:
		return {"board": board.name, "old": old_name, "new": new_name}
	if new_name in columns:
		frappe.throw(_("Колонка {0} на доске уже есть").format(new_name))

	fieldname = field.fieldname
	doctype = board.reference_doctype

	# Порядок важен: сначала расширяем допустимые значения, потом переносим
	# документы и только затем убираем старое значение. Иначе документы на
	# мгновение окажутся с недопустимым для Select значением.
	options = get_options(field)
	if new_name not in options:
		set_options(field, options + [new_name])

	# Массовый UPDATE вместо пообъектного сохранения: это переименование
	# справочного значения, а не смысловое изменение документов. Записи
	# в Version не создаются, но modified обновляем, чтобы не отдавались
	# устаревшие кеши. Имена таблицы и поля берутся из метаданных проверенного
	# Custom Field, а не из пользовательского ввода.
	frappe.db.sql(
		f"update `tab{doctype}` set `{fieldname}`=%s, modified=%s, modified_by=%s where `{fieldname}`=%s",
		(new_name, now(), frappe.session.user, old_name),
	)

	for column in board.columns:
		if column.column_name == old_name:
			column.column_name = new_name
	board.save(ignore_permissions=True)

	# Старое значение убираем, только если его не использует другая доска по
	# тому же полю — иначе сломали бы соседнюю доску.
	if not is_value_used_by_other_boards(board, old_name):
		field.reload()
		set_options(field, [option for option in get_options(field) if option != old_name])

	frappe.clear_cache(doctype=doctype)
	return {"board": board.name, "old": old_name, "new": new_name}
