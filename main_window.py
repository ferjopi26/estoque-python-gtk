#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import sqlite3 as lite

from novo_item import NovoItem
from listagem import Listagem
from classes import WinClasses
from atualiza_item import AtualizaItem
from movimento import WinMovimento
from entrada import WinEntrada
from saida import WinSaida

class MainWindow(object):
    def __init__(self):
        super(MainWindow, self).__init__()

        sinais = {
            "on_itm_sair_activate":self.destroy,
            "on_btnNovoItem_clicked":self.novo_item,
            "on_mainwindow_focus":self.focus,
            "on_mainwindow_focus_in_event":self.focus,
            "on_mainwindow_destroy":self.destroy,
            "on_btnListagem_clicked":self.listagem,
            "on_itm_classes_activate":self.show_classes,
            "on_list_itens_row_activated":self.atualiza_item,
            "on_itm_movimento_activate":self.movimento,
            "on_itmEntrada_activate":self.entrada,
            "on_itm_saida_activate":self.saida,
            "on_btn_buscar_clicked":self.buscar,
            "on_entry_codigo_activate":self.buscar
        }

        self.path = os.getcwd()

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/mainwindow.glade")

        main_window = self.builder.get_object("mainwindow")
        self.list_itens = self.builder.get_object("list_itens")
        self.entry_codigo = self.builder.get_object("entry_codigo")

        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        main_window.show()

    def focus(self, widget, focus):
        self.readFromItens()
        
    def destroy(self, widget):
        Gtk.main_quit()

    def buscar(self, widget):
        self.readFromItens()

    def readFromItens(self):
        store_itens = self.builder.get_object("store_itens")
        codigo = self.entry_codigo.get_text()
        
        store_itens.clear()

        if codigo == "":
            sql = "SELECT itens.codigo, itens.nome,itens.descricao, itens.quantidade, itens.un, classes.descricao AS classe, itens.iditem, itens.classe AS idclasse \
        FROM itens INNER JOIN classes ON itens.classe = classes.idclasse WHERE deleted = 0 GROUP BY itens.nome"
            
        elif len(codigo) == 7:
            sql = "SELECT itens.codigo, itens.nome,itens.descricao, itens.quantidade, itens.un, classes.descricao AS classe, itens.iditem, itens.classe AS idclasse \
        FROM itens INNER JOIN classes ON itens.classe = classes.idclasse WHERE deleted = 0 AND itens.codigo LIKE '%%%s%%' GROUP BY itens.nome" % codigo
        
        else:
            sql = "SELECT itens.codigo, itens.nome,itens.descricao, itens.quantidade, itens.un, classes.descricao AS classe, itens.iditem, itens.classe AS idclasse \
        FROM itens INNER JOIN classes ON itens.classe = classes.idclasse WHERE deleted = 0 AND itens.codigo = '%s' GROUP BY itens.nome" % codigo
        
        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        for row in rows:
            store_itens.append([row[0], row[1], row[2], '%.2f' %row[3], row[4], row[5], "%d" % row[6], "%d" % row[7]])
            
        con.close()

    def novo_item(self, widget):
        NovoItem()

    def listagem(self, widget):
        Listagem()

    def show_classes(self, widget):
        WinClasses()

    def main(self):
        Gtk.main()

    def atualiza_item(self, widget, var1, var2):
        selection = self.list_itens.get_selection()
        iter = selection.get_selected()
        if selection is not None:
            model, paths = selection.get_selected_rows()
            list = [model[paths][0], model[paths][1], model[paths][2], model[paths][3], model[paths][4], model[paths][5], model[paths][6],model[paths][7]]
            
            AtualizaItem(list)

    def movimento(self, widget):
        WinMovimento()
        
    def entrada(self, widget):
        WinEntrada()

    def saida(self, widget):
        WinSaida()
    
main_window = MainWindow()
main_window.main()
