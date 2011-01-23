#!/usr/bin/env python

import gtk
from os.path import join, dirname

from categories import categories

class AddWidgetDialog(object):

    def __init__(self, widgets):
        self.widgets = {}

        interface = gtk.Builder()
        interface.add_from_file(join(dirname(__file__), 'add_dialog.glade'))

        self.dialog =  interface.get_object('dialog')
        self.category_liststore =  interface.get_object('categories')
        self.category_view =  interface.get_object('category_view')
        self.widget_liststore =  interface.get_object('widgets')
        self.widget_view =  interface.get_object('widget_view')
        self.category_image =  interface.get_object('category_image')
        self.category_description =  interface.get_object('category_description')

        # connect signals
        self.dialog.connect('delete_event', lambda *x: self.dialog.hide())
        self.category_view.connect('cursor-changed',
                                    lambda *x: self.on_category_change()
        )

        # add the categories to the liststore alphabetically
        categories_ = sorted(categories.iteritems(),
                             key=lambda c: c[1]['name']
        )
        for id, category in categories_:
            icon = gtk.gdk.pixbuf_new_from_file_at_size(category['icon'], 25, 25)
            self.category_liststore.append((category['name'], id, icon))

        # group widgets into categories
        for widget in widgets:
            if not widget.get('categories'):
                category = 'org.cream.melange.CategoryMiscellaneous'
                self._add_to_category(category, widget)
            for category in widget['categories']:
                self._add_to_category(category['id'], widget)

        self.category_view.set_cursor(0)

    def _add_to_category(self, category, widget):
        if category in self.widgets:
            self.widgets[category].append(widget)
        else:
            self.widgets[category] = [widget]

    def update_info_bar(self):
        """
        Update the description of a category which is displayed above
        the widget listview
        """

        category = categories[self.selected_category]
        if 'icon' in category:
            icon = gtk.gdk.pixbuf_new_from_file_at_size(category['icon'], 35, 35)
            self.category_image.set_from_pixbuf(icon)

        description = split_string(category['description'])
        self.category_description.set_text(description)

    def on_category_change(self):
        """
        Whenever a new category is selected, clear the liststore and add the
        widgets corresponding to the category to it
        """

        self.widget_liststore.clear()
        self.update_info_bar()
        category = self.selected_category
        if not category in self.widgets:
            return

        for widget in self.widgets[category]:
            if 'icon' in widget:
                path = widget['icon']
            else:
                path = join(dirname(__file__), 'images/melange.png')

            icon = gtk.gdk.pixbuf_new_from_file_at_size(path, 35, 35)
            label = '<b>{0}</b>\n{1}'.format(widget['name'],
                                             split_string(widget['description'])
                                      )
            self.widget_liststore.append((icon, label, widget['name']))

    @property
    def selected_widget(self):
        selection = self.widget_view.get_selection()
        model, iter = selection.get_selected()
        if iter:
            return model.get_value(iter, 2)

    @property
    def selected_category(self):
        selection = self.category_view.get_selection()
        model, iter = selection.get_selected()
        return model.get_value(iter, 1)

def split_string(description):
    """split a long string into multiple lines"""
    lst = []
    chars = 0
    for word in description.split():
        if chars > 30:
            lst.append('\n')
            chars = 0
        lst.append(word)
        chars += len(word)

    return ' '.join(lst)
