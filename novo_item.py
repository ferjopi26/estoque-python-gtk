#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import sqlite3 as lite
from datetime import date

class NovoItem(object):
    def __init__(self):
        super(NovoItem, self).__init__()

        sinais = {
            "on_btn_fechar_clicked":self.fechar,
            "on_btn_salvar_clicked":self.salvar,
            "on_btn_limpar_clicked":self.limpar
        }

        self.path = os.getcwd()
        self.curdate = date.today()
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/novo_item.glade")

        self.win_novo_item = self.builder.get_object("win_novo_item")
        self.entry_codigo = self.builder.get_object("entry_codigo")
        self.entry_nome = self.builder.get_object("entry_nome")
        self.txt_descricao = self.builder.get_object("txt_descricao")
        self.buffer = self.txt_descricao.get_buffer()
        self.entry_un = self.builder.get_object("entry_un")
        self.cmb_classe = self.builder.get_object("cmb_classe")
        self.store_classe = self.builder.get_object("store_classe")

        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.get_classes()

        self.win_novo_item.show()

    def get_classes(self):
        self.store_classe.clear()

        sql = "SELECT idclasse, classe, descricao FROM classes ORDER BY descricao"

        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        for row in rows:
            idclasse = "%d" % (row[0])
            descricao = "%s %s" % (row[1], row[2])
            self.store_classe.append([idclasse, descricao])
            self.cmb_classe.set_active(0)
        con.close()

    def fechar(self, widget):
        self.win_novo_item.close()

    def salvar(self, widget):
        codigo = self.entry_codigo.get_text()
        nome = self.entry_nome.get_text()
        buffer = self.txt_descricao.get_buffer()
        descricao = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), 0)
        un = self.entry_un.get_text()

        iter = self.cmb_classe.get_active_iter()
        model = self.cmb_classe.get_model()
        
        try:
            classe = model[iter][0]
        except TypeError as er:
            self.info_message("Nenhuma classe cadastrada")
            return

        if (codigo == ""):
            return
        
        sql = "INSERT INTO itens(codigo, nome, quantidade, un, descricao, classe, deleted) \
            VALUES('%s', '%s', %.2f, '%s', '%s', %s, %s)" % (codigo, nome, 0, un, descricao, classe, 0)
        
        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        try:
            cur.execute(sql)
            con.commit()
        except lite.Error as er:
            if 'UNIQUE' in str(er):
                self.info_message("Item já foi cadastrado")
                return

        sql = "INSERT INTO movimento(iditem, quantidade, obs, tipo, data) VALUES(%d, 0, 'Implantação do estoque', 'E', '%s')" % (cur.lastrowid, self.curdate)
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

        self.info_message("Inserido novo item com Id: %d" % (cur.lastrowid))

        con.close()

    def limpar(self, widget):
        self.entry_codigo.set_text("")
        self.entry_nome.set_text("")
        buffer = self.txt_descricao.get_buffer()
        buffer.set_text("")
        self.entry_un.set_text("")
        
        self.entry_codigo.grab_focus()

    def info_message(self, message):
        messagedialog = Gtk.MessageDialog( parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, message_format=message)

        messagedialog.set_title("Novo Item")

        messagedialog.connect("response", self.info_dialog_response)

        messagedialog.show()

    def info_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            widget.destroy()
