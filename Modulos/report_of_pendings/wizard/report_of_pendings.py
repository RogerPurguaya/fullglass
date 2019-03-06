# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ReportOfPending(models.Model):
    _name = 'report.pending'
    _auto = False
    op = fields.Char('Numero de Op')
    #lote = fields.Char('Numero de Op')
    fec_produccion = fields.Char('Fecha de Produccion')
    fec_entrega = fields.Char('Fecha de Entrega')
    cliente = fields.Char('Cliente')
    obra = fields.Char('Obra')
    presentacion = fields.Char('Presentacion')
    producto = fields.Char('Producto')
    product_id = fields.Integer('Producto')
    sol_id = fields.Integer('Sale Order id')
    order_id = fields.Integer('Glass order id')
    total_area = fields.Char('Total M2 solicitados')
    total_vidrios = fields.Char('Total cristales solicitados')
    total_area_entalle = fields.Char('Tot. de m2 con entalle',compute='_get_entalle')
    total_vidrios_entalle = fields.Char('Tot. vidrios entalle',compute='_get_entalle')
    total_area_optimizado = fields.Char('Tot. de m2 optimizado',compute='_get_optimizado')
    total_vidrios_optimizado = fields.Char('Tot. vidrios entalle',compute='_get_optimizado')
    total_area_corte = fields.Char('Tot. de m2 con entalle',compute='_get_corte')
    total_vidrios_corte = fields.Char('Tot. vidrios entalle',compute='_get_corte')
    total_area_pulido = fields.Char('Tot. de m2 con entalle',compute='_get_pulido')
    total_vidrios_pulido = fields.Char('Tot. vidrios entalle',compute='_get_pulido')
    total_area_entalle_real = fields.Char('Tot. de m2 con entalle',compute='_get_entalle_real')
    total_vidrios_entalle_real = fields.Char('Tot. vidrios entalle',compute='_get_entalle_real')
    total_area_lavado = fields.Char('Tot. de m2 con entalle',compute='_get_lavado')
    total_vidrios_lavado = fields.Char('Tot. vidrios entalle',compute='_get_lavado')
    total_area_templado = fields.Char('Tot. de m2 con entalle',compute='_get_templado')
    total_vidrios_templado = fields.Char('Tot. vidrios entalle',compute='_get_templado')
    total_area_insulado = fields.Char('Tot. de m2 con entalle',compute='_get_insulado')
    total_vidrios_insulado = fields.Char('Tot. vidrios entalle',compute='_get_insulado')
    total_area_laminado = fields.Char('Tot. de m2 con entalle',compute='_get_laminado')
    total_vidrios_laminado = fields.Char('Tot. vidrios entalle',compute='_get_laminado')
    total_area_ingresado = fields.Char('Tot. de m2 con entalle',compute='_get_ingresado')
    total_vidrios_ingresado = fields.Char('Tot. vidrios entalle',compute='_get_ingresado')
    total_area_entregado = fields.Char('Tot. de m2 con entalle',compute='_get_entregado')
    total_vidrios_entregado = fields.Char('Tot. vidrios entalle',compute='_get_entregado')
    total_area_arenado = fields.Char('Tot. de m2 con entalle',compute='_get_arenado')
    total_vidrios_arenado = fields.Char('Tot. vidrios entalle',compute='_get_arenado')
    total_area_comprado = fields.Char('Tot. de m2 con entalle',compute='_get_comprado')
    total_vidrios_comprado = fields.Char('Tot. vidrios entalle',compute='_get_comprado')


    @api.depends('order_id','product_id')
    def _get_entalle(self):
        for record in self:
            order = self.env['glass.order'].search([('id','=',record.order_id)])
            for line in order.line_ids:
                line.calc_line_id.entalle
            record.total_area_entalle = 'yeah'

    @api.depends('order_id','product_id')
    def _get_pulido(self):
        for record in self:
            order = self.env['glass.order'].search([('id','=',record.order_id)])
            area = 0
            totales = 0
            for line in order.line_ids:
                if line.calc_line_id.pulido1:
                    area += line.calc_line_id.area
                    totales += 1
            record.total_area_pulido = area
            record.total_vidrios_pulido = totales

