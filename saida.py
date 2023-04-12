#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import sqlite3 as lite
from datetime import date

class WinSaida(object):
    def __init__(self):
        super(WinSaida, self).__init__()

        sinais = {
            "on_entry_codigo_activate":self.buscar,
            "on_btn_buscar_clicked":self.buscar,
            "on_btn_fechar_clicked":self.fechar,
            "on_btn_salvar_clicked":self.salvar,
            "on_btn_limpar_clicked":self.limpar
        }
        
        self.path = os.getcwd()
        self.quantidade = 0
        self.iditem = ""

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/saida.glade")

        self.win_saida = self.builder.get_object("win_saida")
        self.entry_codigo = self.builder.get_object("entry_codigo")
        self.entry_quantidade = self.builder.get_object("entry_quantidade")
        self.txt_obs = self.builder.get_object("txt_obs")
        self.store_itens = self.builder.get_object("store_itens")
        self.btn_salvar = self.builder.get_object("btn_salvar")
        
        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.win_saida.show()
    
    def get_item(self):
        codigo = self.entry_codigo.get_text()
        
        self.store_itens.clear()

        sql = "SELECT itens.iditem, itens.codigo, itens.nome, itens.descricao, itens.quantidade, itens.un, classes.descricao FROM itens INNER JOIN classes \
            ON itens.classe = classes.idclasse WHERE itens.codigo = '%s'" % codigo
        
        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()
        
        for row in rows:
            self.quantidade = row[4]
            self.iditem = row[0]
            self.store_itens.append(["%d" % row[0], row[1], row[2], row[3], "%0.2f" % row[4], row[5], row[6]])
        
        con.close()

        self.entry_quantidade.grab_focus()
    
    def buscar(self, widget):
        self.get_item()

    def fechar(self, widget):
        self.win_saida.destroy()

    def salvar(self, widget):
        quant = float(self.entry_quantidade.get_text())

        if self.quantidade == 0:
            self.info_message("Saldo zerado no estoque")
            return
        
        if quant > self.quantidade:
            self.info_message("Saldo insuficiente")
            return
        
        self.quantidade -= quant
        buffer = self.txt_obs.get_buffer()
        obs = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), 0)
        curdate = date.today()
        
        sql = "UPDATE itens SET quantidade = %0.2f WHERE iditem = %d" % (self.quantidade, self.iditem)
        
        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

        sql = "INSERT INTO movimento(iditem, quantidade, obs, tipo, data) VALUES(%d, %0.2f, '%s', 'S', '%s')" % (self.iditem, quant, obs, curdate)
        cur = con.cursor()
        cur.execute(sql)
        con.commit()

        con.close()

        self.info_message("Item atualizado no estoque")

    def limpar(self, widget):
        self.entry_codigo.set_text("")
        self.store_itens.clear()
        self.entry_quantidade.set_text("")
        buffer = self.txt_obs.get_buffer()
        buffer.set_text("")

        self.entry_codigo.grab_focus()

    def info_message(self, message):
        messagedialog = Gtk.MessageDialog( parent=None, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, message_format=message)

        messagedialog.set_title("Saída do Estoque")

        messagedialog.connect("response", self.info_dialog_response)

        messagedialog.show()

    def info_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            widget.destroy()

