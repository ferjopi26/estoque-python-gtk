#!/usr/bin/python
# -*- coding: utf-8 -*-

from calendar import month
from multiprocessing import parent_process
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import sqlite3 as lite
from list_movimento import ListMovimento

class WinMovimento(object):
    def __init__(self):
        super(WinMovimento, self).__init__()

        m = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        sinais = {
            "on_btnFechar_clicked":self.fechar,
            "on_btnRelatorio_clicked":self.print,
            "on_entry_data_ini_button_release_event":self.on_entry_data_ini_button_press_event,
            "on_entry_data_fin_button_release_event":self.data_fin,
            "on_data_inicial_day_selected":self.on_data_inicial_day_selected,
            "on_data_final_day_selected":self.on_data_final_day_selected,
            "on_btnBuscar_clicked":self.buscar,
            "on_entry_codigo_activate":self.buscar
        }

        self.path = os.getcwd()
        self.movimento = []
        
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.path + "/movimento.glade")

        self.win_movimento = self.builder.get_object("win_movimento")
        self.store_movimento = self.builder.get_object("store_movimento")
        self.pp_data_inicial = self.builder.get_object("pp_data_inicial")
        self.pp_data_final = self.builder.get_object("pp_data_final")
        self.data_inicial = self.builder.get_object("data_inicial")
        self.entry_data_ini = self.builder.get_object("entry_data_ini")
        self.data_final = self.builder.get_object("data_final")
        self.entry_data_fin = self.builder.get_object("entry_data_fin")
        self.entry_codigo = self.builder.get_object("entry_codigo")
        self.list_movimento = self.builder.get_object("list_movimento")

        self.data_inicial.select_day(1)
        
        year, month, day =  self.data_inicial.get_date()
        self.entry_data_ini.set_text("%02d/%02d/%d" % (day, month+1, year))
        
        self.data_final.select_day(m[month])
        
        year, month, day =  self.data_final.get_date()
        self.entry_data_fin.set_text("%02d/%02d/%d" % (day, month+1, year))

        self.builder.connect_signals(sinais)

        screen = Gdk.Screen.get_default()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.path + '/style.css')

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.get_movimento()

        self.win_movimento.show()

    def fechar(self, widget):
        self.win_movimento.destroy()

    def print(self, widget):
        ListMovimento(self.movimento)
    
    def on_entry_data_ini_button_press_event(self, widget, user_data):
        self.pp_data_inicial.popup()
        
    def data_fin(self, widget, user_data):
        self.pp_data_final.popup()

    def on_data_inicial_day_selected(self, Widget):
        year, month, day =  self.data_inicial.get_date()
        self.entry_data_ini.set_text("%02d/%02d/%d" % (day, month+1, year))
        self.pp_data_inicial.popdown()
        self.get_movimento()

    def on_data_final_day_selected(self, Widget):
        year, month, day = self.data_final.get_date()
        self.entry_data_fin.set_text("%02d/%02d/%d" % (day, month+1, year))
        self.pp_data_final.popdown()
        self.get_movimento()

    def get_movimento(self):
        year, month, day = self.data_inicial.get_date()
        dataini = "%d-%02d-%02d" % (year, month + 1, day)
        
        year, month, day = self.data_final.get_date()
        datafin = "%d-%02d-%02d" % (year, month + 1, day)
        
        sql = "SELECT strftime('%%d/%%m/%%Y', movimento.data), movimento.iditem, itens.nome, itens.descricao, movimento.quantidade, itens.un, movimento.obs, \
            movimento.tipo, movimento.idmov, itens.codigo FROM movimento INNER JOIN itens ON movimento.iditem = itens.iditem WHERE data BETWEEN '%s' AND '%s'" % (dataini, datafin)
        
        self.con = lite.connect(self.path + '/estoque.db')
        cur = self.con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        self.movimento = rows

        self.store_movimento.clear()
        
        for row in rows:
            self.store_movimento.append([row[0], "%d" % row[1], row[2], row[3], "%0.2f" % row[4], row[5], row[6], row[7], "%d" % row[8], row[9]])

    def buscar(self, widget):
        codigo = self.entry_codigo.get_text()
        sql = ""

        year, month, day = self.data_inicial.get_date()
        dataini = "%d-%02d-%02d" % (year, month + 1, day)

        year, month, day = self.data_final.get_date()
        datafin = "%d-%02d-%02d" % (year, month + 1, day)

        if codigo == "":

            sql = "SELECT strftime('%%d/%%m/%%Y', movimento.data), movimento.iditem, itens.nome, itens.descricao, movimento.quantidade, itens.un, movimento.obs, \
                movimento.tipo, movimento.idmov, itens.codigo FROM movimento INNER JOIN itens ON movimento.iditem = itens.iditem WHERE data BETWEEN '%s' AND '%s'" % (dataini, datafin)
            
        elif len(codigo) == 7:
            sql = "SELECT strftime('%%d/%%m/%%Y', movimento.data), movimento.iditem, itens.nome, itens.descricao, movimento.quantidade, itens.un, movimento.obs, \
            movimento.tipo, movimento.idmov, itens.codigo FROM movimento INNER JOIN itens ON movimento.iditem = itens.iditem WHERE data BETWEEN '%s' AND '%s' AND itens.codigo LIKE '%%%s%%'" % (dataini, datafin, codigo)
        
        else:
            sql = "SELECT strftime('%%d/%%m/%%Y', movimento.data), movimento.iditem, itens.nome, itens.descricao, movimento.quantidade, itens.un, movimento.obs, \
            movimento.tipo, movimento.idmov, itens.codigo FROM movimento INNER JOIN itens ON movimento.iditem = itens.iditem WHERE data BETWEEN '%s' AND '%s' \
                AND codigo = '%s'" % (dataini, datafin, codigo)
        
        self.store_movimento.clear()

        self.con = lite.connect(self.path + '/estoque.db')
        cur = self.con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()
        self.movimento = rows
        
        for row in rows:
            self.store_movimento.append([row[0], "%d" % row[1], row[2], row[3], "%0.2f" % row[4], row[5], row[6], row[7], "%d" % row[8], row[9]])
