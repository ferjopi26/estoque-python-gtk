#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, PangoCairo, Pango
import os
import sqlite3 as lite
from datetime import datetime

class ListagemClasses(object):
    def __init__(self) -> None:
        super(ListagemClasses, self).__init__()
        
        self.fill = 1
        self.now = datetime.now()
        self.path = os.getcwd()
        self.page = 1
        papersize = Gtk.PaperSize.new_custom("A4", "A4", 570, 830, Gtk.Unit.POINTS)
        setup = Gtk.PageSetup()
        setup.set_paper_size(papersize)
        setup.set_orientation(Gtk.PageOrientation.LANDSCAPE)
        
        self.po = Gtk.PrintOperation()
        self.po.set_default_page_setup(setup)
        self.po.set_job_name("Listagem de Classes")
        self.po.set_show_progress(True)
        self.po.set_n_pages(1)
        self.po.connect("draw_page", self.draw_page)
        self.po.set_export_filename("Listagem de Classes.pdf")
        self.po.run(Gtk.PrintOperationAction.PRINT_DIALOG, None)

    def draw_page (self, operation, context, page_num):
        cr = context.get_cairo_context()
        self.header(cr)
        self.body(cr)
    
    def begin_print(self, context):
        self.po.set_n_pages(1)
        
    def body(self, cr):
        current_y = 70

        total_rows = self.read_total_itens()
        self.total_page = len(total_rows)/29
        
        if self.total_page % 29 > 1:
            self.total_page += 2

        rows = self.read_classes()
        
        self.footer(cr)
        
        for row in rows:
            current_x = 20
            self.fill_color(cr, current_y, current_x, 10)

            layout = PangoCairo.create_layout (cr)
            layout.set_width(530 * Pango.SCALE)

            desc = Pango.font_description_from_string ("Arial 10")
            layout.set_font_description( desc)

            layout.set_text(row[1])
            cr.move_to(20, current_y)
            PangoCairo.show_layout (cr, layout)

            layout.set_text(row[2].upper())
            cr.move_to(110, current_y)
            PangoCairo.show_layout (cr, layout)

            current_y += 15

            if current_y > 480:
                cr.show_page()
                self.page += 1
                self.header(cr)
                self.footer(cr)
                current_y = 70
                self.fill = 1

            itens = self.read_itens(row[0])

            for item in itens:
                layout.set_text(item[0])
                cr.move_to(20, current_y)
                PangoCairo.show_layout(cr, layout)

                layout.set_text(item[1])
                cr.move_to(110, current_y)
                PangoCairo.show_layout(cr, layout)

                layout.set_text(item[2])
                cr.move_to(200, current_y)
                PangoCairo.show_layout(cr, layout)

                extents = cr.text_extents('%.2f' % item[3])
                layout.set_text('%.2f' % item[3])
                cr.move_to(580 - extents.width, current_y)
                PangoCairo.show_layout(cr, layout)

                layout.set_text(item[4])
                cr.move_to(600, current_y)
                PangoCairo.show_layout(cr, layout)

                current_y += 15
                if current_y > 480:
                    cr.show_page()
                    self.page +=1
                    self.header(cr)
                    self.footer(cr)
                    current_y = 70
                
            cr.set_line_width(0.5)
            cr.move_to(20, current_y)
            cr.line_to(780, current_y)
            cr.stroke()

            current_y += 15
                
    def header(self, cr):
        layout = PangoCairo.create_layout (cr)
        layout.set_width(830 * Pango.SCALE)

        desc = Pango.font_description_from_string ("Arial 15")
        layout.set_font_description( desc)

        layout.set_text("Listagem de Classes")
        cr.move_to(20, 10)
        PangoCairo.show_layout (cr, layout)

        desc = Pango.font_description_from_string ("Arial 10")
        layout.set_font_description( desc)

        layout.set_text("Classe")
        cr.move_to(20, 40)
        PangoCairo.show_layout(cr, layout)

        layout.set_text("Descrição")
        cr.move_to(110, 40)
        PangoCairo.show_layout(cr, layout)
        
        cr.set_line_width(0.5)
        cr.move_to(20, 60)
        cr.line_to(780, 60)
        cr.stroke()

    def footer(self, cr):

        cr.set_line_width(0.5)
        cr.move_to(20, 510)
        cr.line_to(780, 510)
        cr.stroke()

        layout = PangoCairo.create_layout (cr)
        layout.set_width(830 * Pango.SCALE)

        desc = Pango.font_description_from_string ("Arial 8")
        layout.set_font_description( desc)

        layout.set_text("Gestão de Estoque")
        cr.move_to(20, 520)
        PangoCairo.show_layout (cr, layout)

        layout.set_text("Listagem de Classes")
        cr.move_to(280, 520)
        PangoCairo.show_layout (cr, layout)

        layout.set_text(self.now.strftime("%d/%m/%Y %H:%M:%S"))
        cr.move_to(560, 520)
        PangoCairo.show_layout (cr, layout)

        layout.set_text("Página %d de %d" % (self.page, self.total_page))
        cr.move_to(680, 520)
        PangoCairo.show_layout (cr, layout)

    def read_classes(self):
        sql = "SELECT idclasse, classe, descricao FROM classes ORDER BY descricao"

        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        con.close()

        return rows

    def read_itens(self, idclasse):
        sql = "SELECT codigo, nome, descricao, quantidade, un FROM itens WHERE classe = %s AND deleted = 0 ORDER BY codigo"  % idclasse
        
        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        con.close()
        
        return rows

    def read_total_itens(self):
        sql = "SELECT * FROM itens"

        con = lite.connect(self.path + '/estoque.db')
        cur = con.cursor()
        cur.execute(sql)

        rows = cur.fetchall()

        con.close()
        
        return rows

    def fill_color(self, cr, y, current_x, font_size):
        rectangleYPadding = 2
        
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(current_x, y + 2, 760, font_size + 2 * rectangleYPadding)
        cr.fill_preserve()

        if self.fill == 1:
            cr.set_source_rgb(0.9, 0.9, 0.9)

        else:
            cr.set_source_rgb(1, 1, 1)

        cr.fill()
        cr.set_source_rgb(0, 0, 0)
