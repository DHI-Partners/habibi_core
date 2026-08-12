// Пункт меню «Переименовать этап» на канбан-доске.
//
// Хука для канбан-вью во Frappe нет, поэтому единственная точка входа —
// обернуть KanbanView.prototype.push_menu_items. Сам класс грузится лениво
// вместе с бандлом канбана, и на момент выполнения этого файла его обычно
// ещё не существует. Поэтому перехватываем присваивание frappe.views.KanbanView
// через геттер/сеттер: как только бандл определит класс, патч применится.

frappe.provide("frappe.views");

function patch_kanban_view(KanbanView) {
	const proto = KanbanView && KanbanView.prototype;
	if (!proto || proto.__habibi_rename_stage) return;
	proto.__habibi_rename_stage = true;

	const original_push_menu_items = proto.push_menu_items;
	proto.push_menu_items = function () {
		original_push_menu_items.apply(this, arguments);

		if (!this.board_perms || !this.board_perms.write) return;

		this.menu_items.push({
			label: __("Переименовать этап"),
			action: () => show_rename_stage_dialog(this),
		});
	};
}

function show_rename_stage_dialog(view) {
	const columns = ((view.board && view.board.columns) || []).map((column) => column.column_name);

	if (!columns.length) {
		frappe.msgprint(__("На доске нет колонок"));
		return;
	}

	const dialog = new frappe.ui.Dialog({
		title: __("Переименовать этап"),
		fields: [
			{
				fieldname: "old_name",
				label: __("Этап"),
				fieldtype: "Select",
				options: columns,
				default: columns[0],
				reqd: 1,
			},
			{
				fieldname: "new_name",
				label: __("Новое название"),
				fieldtype: "Data",
				reqd: 1,
			},
		],
		primary_action_label: __("Переименовать"),
		primary_action: (values) => {
			dialog.disable_primary_action();
			frappe
				.xcall("habibi_core.kanban_stages.rename_stage", {
					board_name: view.board_name,
					old_name: values.old_name,
					new_name: values.new_name,
				})
				.then(() => {
					dialog.hide();
					// Колонки живут в уже отрисованном компоненте доски, и
					// частичное обновление оставило бы старое название в
					// заголовке. Перезагрузка честнее, а переименование —
					// операция редкая.
					window.location.reload();
				})
				.catch(() => dialog.enable_primary_action());
		},
	});

	dialog.show();
}

if (frappe.views.KanbanView) {
	patch_kanban_view(frappe.views.KanbanView);
} else {
	let kanban_view;
	Object.defineProperty(frappe.views, "KanbanView", {
		configurable: true,
		get: () => kanban_view,
		set: (value) => {
			kanban_view = value;
			patch_kanban_view(value);
		},
	});
}
