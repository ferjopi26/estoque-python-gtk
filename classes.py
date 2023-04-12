#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import sqlite3 as lite

from nova_classe import NovaClasse
from listagem_classes import ListagemClasses

class WinClasses(object):
    def __init__(self):
        super(WinClasses, self).__init__()

        sinais = {
            "on_btnFechar_clicked":self.close,
            "on_btnListagem_clicked":self.listagem,
            "on_btnNovaClasse_clicked":self.nova_classe,
            "on_win_classes_focus":self.focus,
            "on_win_classes_focus_in_event":self.focus
        }

        self.path = os.getcwd()

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/classes.glade")

        self.win_classes = self.builder.get_object("win_classes")
        self.store_classe = self.builder.get_object("store_classes")

        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.get_classes()

        self.win_classes.show()

    def focus(self, widget, focus):
        self.get_classes()

    def close(self, widget):
        self.win_classes.destroy()

    def get_classes(self):
        self.store_classe.clear()

        sql = "SELECT idclasse, classe, descricao FROM classes ORDER BY descricao"

        self.con = lite.connect(self.path + '/estoque.db')
        cur = self.con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        for row in rows:
            parent = self.store_classe.append(None, ["%d" % row[0], row[1], row[2], "", "", "", "", ""])
            sql = "SELECT codigo, nome, descricao, quantidade, un FROM itens WHERE classe = %d AND deleted = 0 ORDER BY nome" % (row[0])
            cur1 = self.con.cursor()
            cur1.execute(sql)
            rows1 = cur1.fetchall()
            for row1 in rows1:
                self.store_classe.append(parent, ["", "", "", row1[0], row1[1], row1[2], "%.2f" % (row1[3]), row1[4]])
            
        self.con.close()

    def listagem(self, widget):
        ListagemClasses()

    def nova_classe(self, widget):
        NovaClasse()