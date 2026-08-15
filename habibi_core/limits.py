"""Ограничение числа пользователей на сайте.

Лимит приезжает из управляющей плоскости (saas_bridge) и лежит в site_config.json
самого сайта — `saas_bridge_max_users`. Именно там, а не в документе внутри базы:
до site_config.json изнутри сайта хода нет, поэтому свой лимит System Manager
тенанта поднять не может. Документ в базе он бы отредактировал, а закрыли бы
правами — поменял бы и права.

Здесь только применение лимита. Откуда взялось само число — тариф, ручное
решение, внешний биллинг — сайт не знает и знать не должен: ему достаточно
готового числа.
"""

import frappe
from frappe import _
from frappe.utils import cint

MAX_USERS_KEY = "saas_bridge_max_users"

# Guest — фикстура фреймворка: он есть на каждом сайте и под ним никто не входит,
# это сессионный пользователь анонимных запросов. Administrator место занимает —
# это рабочий вход, пароль от него выдаётся при создании сайта.
NOT_A_SEAT = ("Guest",)


def user_limit():
	"""Сколько мест разрешено. 0 — лимита нет (ключ не задан)."""
	return cint(frappe.conf.get(MAX_USERS_KEY))


def used_seats():
	"""Сколько мест занято: включённые System User, кроме служебных."""
	return frappe.db.count(
		"User",
		{"enabled": 1, "user_type": "System User", "name": ["not in", NOT_A_SEAT]},
	)


def enforce_user_limit(doc, method=None):
	"""Не даёт занять место сверх лимита. Хук на User.validate.

	Именно validate, а не before_insert: иначе лимит обходится в два шага —
	создать выключенного пользователя, затем включить его.
	"""
	limit = user_limit()
	if not limit:
		return

	# user_type здесь уже пересчитан: User.validate выводит его из ролей
	# (set_system_user → has_desk_access), а хуки doc_events идут после метода
	# контроллера. Поэтому место занимает именно тот, у кого есть доступ в Desk,
	# а портальный пользователь — нет.
	if doc.user_type != "System User" or not cint(doc.enabled) or doc.name in NOT_A_SEAT:
		return

	# установка приложений, миграции и импорт заводят пользователей сами;
	# ронять их из-за тарифа нельзя, сайт останется недостроенным
	if (
		frappe.flags.in_install
		or frappe.flags.in_migrate
		or frappe.flags.in_patch
		or frappe.flags.in_import
	):
		return

	# правка уже занятого места нового места не добавляет. Проверяем и user_type:
	# выдача роли с доступом в Desk превращает бесплатного портального
	# пользователя в занимающего место, и это тоже надо ловить
	if (
		not doc.is_new()
		and not doc.has_value_changed("enabled")
		and not doc.has_value_changed("user_type")
	):
		return

	# сам doc в подсчёт не попадает: он либо ещё не в базе, либо в базе выключен
	if used_seats() >= limit:
		frappe.throw(
			_("На сайте разрешено пользователей: {0}. Отключите одного из существующих или расширьте тариф.").format(
				limit
			),
			title=_("Достигнут лимит пользователей"),
		)


def add_limits_to_bootinfo(bootinfo):
	"""Кладёт лимит и расход мест в bootinfo, чтобы интерфейс мог их показать.

	Регистрируется как extend_bootinfo (см. hooks.py). Без лимита ключа нет
	вовсе — сайту вне SaaS показывать нечего.
	"""
	limit = user_limit()
	if not limit:
		return

	bootinfo.habibi_limits = {"max_users": limit, "used_users": used_seats()}
