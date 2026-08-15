import frappe
from frappe.tests import IntegrationTestCase

from habibi_core.limits import MAX_USERS_KEY, enforce_user_limit, used_seats

EMAIL = "limit-test-{0}@habibi.test"
# Место занимает не всякий User, а тот, у кого есть доступ в Desk: User.validate
# сам пересчитывает user_type из ролей. Пользователь без ролей стал бы Website
# User и в лимит бы не попал — поэтому роль здесь обязательна.
DESK_ROLE = "System Manager"


def drop_user(email):
	if frappe.db.exists("User", email):
		frappe.delete_doc("User", email, force=True, ignore_permissions=True)


def make_user(index, enabled=1, roles=(DESK_ROLE,)):
	email = EMAIL.format(index)
	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": f"Limit {index}",
			"enabled": enabled,
			"send_welcome_email": 0,
			"roles": [{"role": role} for role in roles],
		}
	)
	user.insert(ignore_permissions=True)
	return user


class TestUserLimit(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		# Лимит читается из frappe.conf; в тесте правим только копию текущего
		# процесса, файл site_config.json остаётся нетронутым.
		self.addCleanup(frappe.local.conf.pop, MAX_USERS_KEY, None)

		# Откат транзакции IntegrationTestCase вешает на класс
		# (addClassCleanup(_rollback_db)), а не на тест: пользователь соседнего
		# теста дожил бы сюда и сместил счёт занятых мест. Каждый тест считает
		# лимит от текущего числа мест, поэтому старт должен быть чистым.
		for index in range(1, 10):
			drop_user(EMAIL.format(index))

	def set_limit(self, limit):
		frappe.local.conf[MAX_USERS_KEY] = limit

	def test_no_limit_allows_any_user(self):
		make_user(1)
		make_user(2)  # без ключа в конфиге лимита нет вовсе

	def test_limit_blocks_user_over_it(self):
		self.set_limit(used_seats() + 1)
		make_user(1)

		with self.assertRaises(frappe.ValidationError):
			make_user(2)

	def test_disabled_user_does_not_take_a_seat(self):
		self.set_limit(used_seats() + 1)
		make_user(1, enabled=0)
		make_user(2)  # выключенный место не занял

	def test_enabling_a_user_at_the_limit_is_refused(self):
		self.set_limit(used_seats() + 1)
		user = make_user(1, enabled=0)
		make_user(2)  # лимит выбран включённым пользователем

		user.enabled = 1
		with self.assertRaises(frappe.ValidationError):
			user.save(ignore_permissions=True)

	def test_portal_user_is_not_a_seat(self):
		self.set_limit(used_seats())
		user = make_user(1, roles=())  # без ролей — Website User

		self.assertEqual(user.user_type, "Website User")

	def test_giving_desk_access_at_the_limit_is_refused(self):
		self.set_limit(used_seats() + 1)
		portal_user = make_user(1, roles=())
		make_user(2)  # лимит выбран

		# выдача роли с доступом в Desk превращает бесплатного пользователя в
		# занимающего место — обход лимита в два шага
		portal_user.append("roles", {"role": DESK_ROLE})
		with self.assertRaises(frappe.ValidationError):
			portal_user.save(ignore_permissions=True)

	def test_editing_an_existing_user_at_the_limit_is_allowed(self):
		self.set_limit(used_seats() + 1)
		user = make_user(1)

		# лимит выбран, но сохранение места не добавляет
		user.first_name = "Renamed"
		user.save(ignore_permissions=True)

	def test_install_and_migrate_are_not_blocked(self):
		self.set_limit(1)
		doc = frappe.get_doc(
			{
				"doctype": "User",
				"email": EMAIL.format(9),
				"first_name": "Install",
				"user_type": "System User",
				"enabled": 1,
			}
		)

		frappe.flags.in_migrate = True
		self.addCleanup(frappe.flags.pop, "in_migrate", None)
		enforce_user_limit(doc)  # не бросает: иначе миграция оставила бы сайт недостроенным
