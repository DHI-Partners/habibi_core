import frappe
from frappe.tests import IntegrationTestCase

from habibi_core.kanban_stages import rename_stage

CUSTOM_FIELD = "Task-custom_test_stage"
FIELDNAME = "custom_test_stage"


def make_board(name, field_name, columns):
	# Прогон должен быть повторяемым: доска могла пережить прошлый прогон,
	# если тот упал до отката транзакции.
	if frappe.db.exists("Kanban Board", name):
		frappe.delete_doc("Kanban Board", name, force=True, ignore_permissions=True)
	board = frappe.get_doc(
		{
			"doctype": "Kanban Board",
			"kanban_board_name": name,
			"reference_doctype": "Task",
			"field_name": field_name,
			"columns": [{"column_name": c} for c in columns],
		}
	)
	board.insert(ignore_permissions=True)
	return board


def field_options(fieldname=FIELDNAME):
	options = frappe.db.get_value("Custom Field", {"dt": "Task", "fieldname": fieldname}, "options")
	return [o for o in (options or "").split("\n") if o.strip()]


class TestKanbanStages(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Custom Field создаётся один раз: это ALTER TABLE, транзакцией не откатывается.
		if not frappe.db.exists("Custom Field", CUSTOM_FIELD):
			frappe.get_doc(
				{
					"doctype": "Custom Field",
					"dt": "Task",
					"fieldname": FIELDNAME,
					"label": "Тестовый этап",
					"fieldtype": "Select",
					"options": "Бэклог\nВ работе",
					"insert_after": "status",
				}
			).insert(ignore_permissions=True)
			frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		# Откат до удаления поля: иначе commit ниже зафиксировал бы доски и
		# задачи, созданные тестами, и следующий прогон падал бы на дубликатах.
		frappe.db.rollback()
		frappe.delete_doc("Custom Field", CUSTOM_FIELD, force=True, ignore_permissions=True)
		frappe.db.commit()
		super().tearDownClass()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.set_value("Custom Field", CUSTOM_FIELD, "options", "Бэклог\nВ работе")
		frappe.clear_cache(doctype="Task")

	def make_task(self, subject, stage):
		task = frappe.get_doc({"doctype": "Task", "subject": subject, FIELDNAME: stage})
		task.insert(ignore_permissions=True)
		return task

	# --- синхронизация колонок доски со значениями поля ---

	def test_new_column_is_added_to_field_options(self):
		board = make_board("Стенд синхронизации", FIELDNAME, ["Бэклог", "В работе"])

		board.append("columns", {"column_name": "На проверке"})
		board.save(ignore_permissions=True)

		self.assertIn("На проверке", field_options())

	def test_card_can_be_moved_to_newly_added_column(self):
		board = make_board("Стенд перетаскивания", FIELDNAME, ["Бэклог"])
		board.append("columns", {"column_name": "Сдано"})
		board.save(ignore_permissions=True)

		task = self.make_task("Задача для переноса", "Бэклог")
		task.db_set(FIELDNAME, "Сдано")
		task.reload()
		task.save(ignore_permissions=True)

		self.assertEqual(task.get(FIELDNAME), "Сдано")

	def test_standard_field_options_are_never_touched(self):
		before = frappe.get_meta("Task").get_field("priority").options
		board = make_board("Стенд приоритетов", "priority", ["Low", "Medium"])

		board.append("columns", {"column_name": "Космический"})
		board.save(ignore_permissions=True)

		frappe.clear_cache(doctype="Task")
		self.assertEqual(frappe.get_meta("Task").get_field("priority").options, before)

	def test_archived_column_value_stays_in_options(self):
		board = make_board("Стенд архива", FIELDNAME, ["Бэклог", "В работе"])

		board.columns[1].status = "Archived"
		board.save(ignore_permissions=True)

		self.assertIn("В работе", field_options())

	# --- переименование этапа ---

	def test_rename_moves_tasks_to_new_stage(self):
		board = make_board("Стенд переименования", FIELDNAME, ["Бэклог", "В работе"])
		task = self.make_task("Задача под переименование", "В работе")

		rename_stage(board.name, "В работе", "В процессе")

		self.assertEqual(frappe.db.get_value("Task", task.name, FIELDNAME), "В процессе")

	def test_rename_updates_field_options(self):
		board = make_board("Стенд опций", FIELDNAME, ["Бэклог", "В работе"])

		rename_stage(board.name, "В работе", "В процессе")

		options = field_options()
		self.assertIn("В процессе", options)
		self.assertNotIn("В работе", options)

	def test_rename_updates_board_column(self):
		board = make_board("Стенд колонки", FIELDNAME, ["Бэклог", "В работе"])

		rename_stage(board.name, "В работе", "В процессе")

		board.reload()
		self.assertEqual([c.column_name for c in board.columns], ["Бэклог", "В процессе"])

	def test_rename_keeps_old_value_used_by_another_board(self):
		other = make_board("Стенд соседней доски", FIELDNAME, ["В работе"])
		board = make_board("Стенд общего значения", FIELDNAME, ["Бэклог", "В работе"])

		rename_stage(board.name, "В работе", "В процессе")

		self.assertIn("В работе", field_options())
		self.assertEqual([c.column_name for c in other.reload().columns], ["В работе"])

	def test_rename_rejects_blank_name(self):
		board = make_board("Стенд пустого имени", FIELDNAME, ["Бэклог"])

		with self.assertRaises(frappe.ValidationError):
			rename_stage(board.name, "Бэклог", "   ")

	def test_rename_rejects_duplicate_name(self):
		board = make_board("Стенд дубля", FIELDNAME, ["Бэклог", "В работе"])

		with self.assertRaises(frappe.ValidationError):
			rename_stage(board.name, "Бэклог", "В работе")

	def test_rename_rejects_unknown_column(self):
		board = make_board("Стенд неизвестной колонки", FIELDNAME, ["Бэклог"])

		with self.assertRaises(frappe.ValidationError):
			rename_stage(board.name, "Такого нет", "Что угодно")

	def test_rename_rejects_standard_field(self):
		board = make_board("Стенд стандартного поля", "priority", ["Low", "Medium"])

		with self.assertRaises(frappe.ValidationError):
			rename_stage(board.name, "Low", "Низкий")

	def test_rename_requires_write_permission(self):
		board = make_board("Стенд прав", FIELDNAME, ["Бэклог", "В работе"])
		user = "stage-reader@example.com"
		if not frappe.db.exists("User", user):
			frappe.get_doc(
				{"doctype": "User", "email": user, "first_name": "Stage Reader"}
			).insert(ignore_permissions=True)

		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				rename_stage(board.name, "В работе", "В процессе")
		finally:
			frappe.set_user("Administrator")
