import frappe

# Подписи, которые НЕ проходят через функцию перевода и потому не покрываются
# записями Translation из fixtures/translation.json. Их приходится править
# прямо в загрузочных данных (bootinfo), пока Frappe их формирует.
BRAND = {"ERPNext": "Habibi ERP"}


def rebrand_bootinfo(bootinfo):
	"""Заменяет заголовок приложения «ERPNext» на «Habibi ERP» в bootinfo.

	Регистрируется как extend_bootinfo (см. hooks.py). Вызывается в
	frappe/sessions.py после того, как boot.py заполнил bootinfo.app_data.

	Заголовок рядом с логотипом в сайдбаре нового Desk (/desk/) берётся из
	bootinfo.app_data[].app_title сырым, без __(), — поэтому перевод его не
	трогает. Здесь и подменяем. Это то единственное место, ради которого
	раньше существовал форк ERPNext: app_title правился в его hooks.py.

	Идемпотентно и безопасно: если структура bootinfo изменится, просто
	ничего не делаем, а не роняем загрузку сессии.
	"""
	for app in bootinfo.get("app_data") or []:
		title = app.get("app_title")
		if title in BRAND:
			app["app_title"] = BRAND[title]
