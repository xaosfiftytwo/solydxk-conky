#! /usr/bin/env python3

from gi.repository import Gtk, GObject

# Show message dialog
# Usage:
# MessageDialog(_("My Title"), "Your (error) message here", Gtk.MessageType.ERROR).show()
# Message types:
# Gtk.MessageType.INFO
# Gtk.MessageType.WARNING
# Gtk.MessageType.ERROR
# MessageDialog can be called from a working thread
class MessageDialog(Gtk.MessageDialog):
    def __init__(self, title, message, style, parent=None):
        Gtk.MessageDialog.__init__(self, parent, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, style, Gtk.ButtonsType.OK, message)
        self.set_default_response(Gtk.ResponseType.OK)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_markup("<b>%s</b>" % title)
        self.format_secondary_markup(message)
        if parent is not None:
            self.set_icon(parent.get_icon())
        self.connect('response', self._handle_clicked)

    def _handle_clicked(self, *args):
        self.destroy()

    def show(self):
        GObject.timeout_add(0, self._do_show_dialog)

    def _do_show_dialog(self):
        self.show_all()
        return False


# Show unthreaded message dialog
# Usage:
# MessageDialog(_("My Title"), "Your (error) message here", Gtk.MessageType.ERROR).show()
# Message types:
# Gtk.MessageType.INFO
# Gtk.MessageType.WARNING
# Gtk.MessageType.ERROR
# MessageDialogSave can NOT be called from a working thread, only from main (UI) thread
class MessageDialogSave(object):
    def __init__(self, title, message, style, parent=None):
        self.title = title
        self.message = message
        self.parent = parent
        self.style = style

    def show(self):
        dialog = Gtk.MessageDialog(self.parent, Gtk.DialogFlags.MODAL, self.style, Gtk.ButtonsType.OK, self.message)
        dialog.set_markup("<b>%s</b>" % self.title)
        dialog.format_secondary_markup(self.message)
        if self.parent is not None:
            dialog.set_icon(self.parent.get_icon())
        dialog.run()
        dialog.destroy()


# Create question dialog
# Usage:
# dialog = QuestionDialog(_("My Title"), _("Put your question here?"))
#    if (dialog.show()):
# QuestionDialog can NOT be called from a working thread, only from main (UI) thread
class QuestionDialog(object):
    def __init__(self, title, message, parent=None):
        self.title = title
        self.message = message
        self.parent = parent

    #''' Show me on screen '''
    def show(self):
        dialog = Gtk.MessageDialog(self.parent, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, self.message)
        dialog.set_markup("<b>%s</b>" % self.title)
        dialog.format_secondary_markup(self.message)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        if self.parent is not None:
            dialog.set_icon(self.parent.get_icon())
        answer = dialog.run()
        if answer == Gtk.ResponseType.YES:
            return_value = True
        else:
            return_value = False
        dialog.destroy()
        return return_value
