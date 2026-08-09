app_name = "habibi_core"
app_title = "Habibi Core"
app_publisher = "Habeebe"
app_description = "Customization layer on top of ERPNext"
app_email = "dosnet2200@gmail.com"
app_license = "mit"

# Apps
# ------------------

# Everything in this app customises ERPNext, so bench refuses to install it on a site
# without erpnext and always installs erpnext first.
required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "habibi_core",
# 		"logo": "/assets/habibi_core/logo.png",
# 		"title": "Habibi Core",
# 		"route": "/habibi_core",
# 		"has_permission": "habibi_core.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/habibi_core/css/habibi_core.css"
# app_include_js = "/assets/habibi_core/js/habibi_core.js"

# include js, css files in header of web template
# web_include_css = "/assets/habibi_core/css/habibi_core.css"
# web_include_js = "/assets/habibi_core/js/habibi_core.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "habibi_core/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "habibi_core/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "habibi_core.utils.jinja_methods",
# 	"filters": "habibi_core.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "habibi_core.install.before_install"
# after_install = "habibi_core.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "habibi_core.uninstall.before_uninstall"
# after_uninstall = "habibi_core.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "habibi_core.utils.before_app_install"
# after_app_install = "habibi_core.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "habibi_core.utils.before_app_uninstall"
# after_app_uninstall = "habibi_core.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "habibi_core.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "habibi_core.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"habibi_core.tasks.all"
# 	],
# 	"daily": [
# 		"habibi_core.tasks.daily"
# 	],
# 	"hourly": [
# 		"habibi_core.tasks.hourly"
# 	],
# 	"weekly": [
# 		"habibi_core.tasks.weekly"
# 	],
# 	"monthly": [
# 		"habibi_core.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "habibi_core.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "habibi_core.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "habibi_core.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "habibi_core.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["habibi_core.utils.before_request"]
# after_request = ["habibi_core.utils.after_request"]

# Job Events
# ----------
# before_job = ["habibi_core.utils.before_job"]
# after_job = ["habibi_core.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"habibi_core.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []



# Ребрендинг ERPNext
# ------------------
# Раньше это жило в форке DHI-Partners/habibi_erp: четыре коммита правили
# app_title в hooks.py и метки в трёх JSON-фикстурах ERPNext. Форк стоил
# ребейза на каждом обновлении ERPNext — ради трёх подписей в интерфейсе.
#
# Теперь то же самое делается отсюда, переводами. Работает потому, что все
# эти строки уходят на экран через функцию перевода:
#
#   frappe/apps.py:42                    "title": _(app_detail.get("title"))
#   .../views/workspace/workspace.js     __(this._page.title), __(this._page.name)
#
# Записи лежат в fixtures/translation.json и импортируются на каждом
# bench migrate: sync_fixtures() (frappe/migrate.py:171) читает все *.json
# из каталога fixtures независимо от списка ниже, а import_file идёт
# с force=True, поэтому применяется всегда и не плодит дублей.
#
# Плюс к форку: запись Workspace остаётся с именем "ERPNext Settings", и
# ссылки на неё (link_to в desktop_icon, name в workspace_sidebar) остаются
# целыми. Форку приходилось править их синхронно, иначе ломался переход.
#
# Список ниже нужен только для обратной выгрузки: bench export-fixtures.
fixtures = [
	{
		"doctype": "Translation",
		"filters": [["source_text", "in", ["ERPNext", "ERPNext Settings"]]],
	},
]

# Заголовок приложения рядом с логотипом в сайдбаре нового Desk (/desk/)
# переводы НЕ покрывают: frappe/boot.py кладёт app_title в bootinfo.app_data
# сырым, а фронт выводит его без __(). Поэтому подменяем прямо в bootinfo
# через extend_bootinfo (вызывается в frappe/sessions.py после заполнения
# app_data). Это второе — и последнее — место, ради которого держали форк.
extend_bootinfo = ["habibi_core.boot.rebrand_bootinfo"]

# Единственное место, где название останется английским, — диалог «О программе»
# со списком версий: frappe/utils/change_log.py:130 берёт app_title каждого
# приложения напрямую, без перевода. Экран информационный, открывается редко.
