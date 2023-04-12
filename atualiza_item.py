#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gio, Gdk
import os
import sqlite3 as lite

class AtualizaItem(object):
    def __init__(self, list):
        super(AtualizaItem, self).__init__()
        
        self.item = list

        sinais = {
            "on_btn_fechar_clicked":self.fechar,
            "on_btn_salvar_clicked":self.salvar,
            "on_btn_excluir_clicked":self.excluir
        }

        self.path = os.getcwd()

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/atualiza_item.glade")

        self.win_atualiza_item = self.builder.get_object("win_atualiza_item")
        self.entry_codigo = self.builder.get_object("entry_codigo")
        self.entry_nome = self.builder.get_object("entry_nome")
        self.txt_descricao = self.builder.get_object("txt_descricao")
        self.buffer = self.txt_descricao.get_buffer()
        self.entry_un = self.builder.get_object("entry_un")
        self.cmb_classe = self.builder.get_object("cmb_classe")
        self.store_classe = self.builder.get_object("store_classe")
        buffer = self.txt_descricao.get_buffer()

        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.get_classes()

        self.entry_codigo.set_text(list[0])
        self.entry_nome.set_text(list[1])
        buffer.set_text(list[2])
        self.entry_un.set_text(list[4])

        for i in range(len(self.store_classe)):
            self.cmb_classe.set_active(i)
            tree_iter = self.cmb_classe.get_active_iter()
            model = self.cmb_classe.get_model()
            if(model[tree_iter][0] == self.item[7]):
                self.cmb_classe.set_active(i)
                break    

        self.win_atualiza_item.show()

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
        self.win_atualiza_item.close()

    def salvar(self, widget):
        codigo = self.entry_codigo.get_text()
        nome = self.entry_nome.get_text()
        buffer = self.txt_descricao.get_buffer()
        descricao = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), 0)
        un = self.entry_un.get_text()

        iter = self.cmb_classe.get_active_iter()
        model = self.cmb_classe.get_model()
        classe = model[iter][0]

        iditem = self.item[7]
        
        sql = "UPDATE itens SET codigo = '%s', nome = '%s', un = '%s', descricao = '%s', classe = %s WHERE iditem = %s" % (codigo, nome, un, descricao, classe, iditem)
        
        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

        self.info_message("Item Atualizado")

        con.close()

    def excluir(self, widget):
        message = "O item será excluído"
        messagedialog = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.WARNING, buttons=Gtk.ButtonsType.OK_CANCEL, message_format=message)

        messagedialog.set_title("Atualiza Item")

        response = messagedialog.run()
        if response == Gtk.ResponseType.OK:
            sql = "UPDATE itens SET deleted = 1 WHERE iditem = %s" % self.item[6]
            con = lite.connect(self.path + '/estoque.db')
            cur = con.cursor()
            cur.execute(sql)

            con.commit()
            con.close()

            messagedialog.destroy()
            self.info_message("Item Excluído")

        elif response == Gtk.ResponseType.CANCEL:
            messagedialog.destroy()
            self.win_atualiza_item.close()
        
    def info_message(self, message):
        messagedialog = Gtk.MessageDialog(parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, message_format=message)

        messagedialog.set_title("Atualiza Item")

        messagedialog.connect("response", self.info_dialog_response)

        messagedialog.show()

    def info_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            widget.destroy()
            self.win_atualiza_item.close()

