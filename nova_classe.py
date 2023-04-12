#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gio, Gdk
import os
import sqlite3 as lite

class NovaClasse(object):
    def __init__(self) -> None:
        super(NovaClasse, self).__init__()

        sinais = {
            "on_btn_fechar_clicked":self.fechar,
            "on_btn_salvar_clicked":self.salvar,
            "on_btn_limpar_clicked":self.limpar
        }

        self.path = os.getcwd()

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/nova_classe.glade")

        self.win_nova_classe = self.builder.get_object("win_nova_classe")
        self.entry_classe = self.builder.get_object("entry_classe")
        self.entry_descricao = self.builder.get_object("entry_descricao")
        
        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.win_nova_classe.show()

    def fechar(self, widget):
        self.win_nova_classe.close()

    def salvar(self, widget):
        classe = self.entry_classe.get_text()
        descricao = self.entry_descricao.get_text()

        if classe == "":
            return
        
        sql = "INSERT INTO classes(classe, descricao) VALUES('%s', '%s')" % (classe, descricao)

        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        try:
            cur.execute(sql)
            con.commit()
            con.close()
            self.info_message("Inserido nova classe com Id: %d" % (cur.lastrowid))
        except lite.Error as er:
            if 'UNIQUE' in str(er):
                self.info_message("Classe já foi cadastrada")
    
    def limpar(self, widget):
        self.entry_classe.set_text("")
        self.entry_descricao.set_text("")

        self.entry_classe.grab_focus()

    def info_message(self, message):
        messagedialog = Gtk.MessageDialog(
            parent=None,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=message
        )

        messagedialog.set_title("Nova Classe")

        messagedialog.connect("response", self.info_dialog_response)

        messagedialog.show()

    def info_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            widget.destroy()
