import sublime
import sublime_plugin


def _set_reference_from_file(base_view: sublime.View, file: str) -> None:
	try:
		with open(file, encoding="utf-8") as f:
			base_view.set_reference_document(f.read())
	except UnicodeDecodeError:
		sublime.status_message("Binary file, you shouldn't set this as a reference document.")

def _set_reference_from_view(base_view: sublime.View, ref_view: sublime.View) -> None:
	if ref_view.encoding() == "Hexadecimal":
		sublime.status_message("Binary file, you shouldn't set this as a reference document.")
		return
	base_view.set_reference_document(ref_view.substr(sublime.Region(0, ref_view.size())))


class ToggleAllDiffsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		sel = self.view.sel()
		old_sel = list(sel)
		sel.clear()
		sel.add(sublime.Region(0, self.view.size()))
		self.view.run_command("toggle_inline_diff", {"args": {"prefer_hide": True}})
		sel.clear()
		sel.add_all(old_sel)

	def is_enabled(self):
		return self.view.encoding() != "Hexadecimal"

	def is_visible(self):
		return self.view.settings().get("mini_diff", True) is not False


class SetReferenceDocumentCommand(sublime_plugin.WindowCommand):
	def run(self, group=-1, index=-1):
		if group != -1 and index != -1:
			base_view = self.window.views_in_group(group)[index]
		else:
			base_view = self.window.active_view()
		if base_view is None or base_view.encoding() == "Hexadecimal": return
		other_views = [view for view in self.window.views()
					   if view != base_view
					   and view.encoding() != "Hexadecimal"
					   and view.substr(0) != '\x00']
		if not other_views: return

		def on_select(i: int):
			if i == -1: return
			ref_view = other_views[i]
			base_view.set_reference_document(ref_view.substr(sublime.Region(0, ref_view.size())))

		self.window.show_quick_panel([view.file_name() or view.name() for view in other_views], on_select)

	def is_visible(self, group=-1, index=-1):
		if group != -1 and index != -1:
			view = self.window.sheets_in_group(group)[index].view()
		else:
			view = self.window.active_view()
		return view is not None and view.encoding() != "Hexadecimal"


class SetReferenceDocumentFromFileCommand(sublime_plugin.WindowCommand):
	base_view = None
	ref_document = None

	def run(self, files):
		base_view = self.window.find_open_file(files[0])
		ref_view = self.window.find_open_file(files[1])
		if base_view is not None:
			if ref_view is not None:
				_set_reference_from_view(base_view, ref_view)
			else:
				_set_reference_from_file(base_view, files[1])
		else:
			SetReferenceDocumentFromFileCommand.base_view = self.window.open_file(files[0])
			SetReferenceDocumentFromFileCommand.ref_document = ref_view or files[1]


	def is_visible(self, files):
		return len(files) == 2


class BaseViewEventListener(sublime_plugin.EventListener):
	def on_load_async(self, view: sublime.View):
		if view != SetReferenceDocumentFromFileCommand.base_view:
			return
		if isinstance(SetReferenceDocumentFromFileCommand.ref_document, sublime.View):
			_set_reference_from_view(SetReferenceDocumentFromFileCommand.base_view,  # type: ignore
				SetReferenceDocumentFromFileCommand.ref_document)
		elif isinstance(SetReferenceDocumentFromFileCommand.ref_document, str):
			_set_reference_from_file(SetReferenceDocumentFromFileCommand.base_view,  # type: ignore
				SetReferenceDocumentFromFileCommand.ref_document)
		SetReferenceDocumentFromFileCommand.base_view = None
		SetReferenceDocumentFromFileCommand.ref_document = None