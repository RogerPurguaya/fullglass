# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class carDriver(models.Model):
    _name = 'car.driver'
    partner_id = fields.Many2one('res.partner', string="Conductores")

class res_partner(models.Model):
    _inherit="res.partner"
    mi_campo = fields.Char("Mi campo")
    # libro_ids = fields.One2many("biblioteca.libros", "partner_id", "Lista de libros")

class SaleOrderForm(models.Model):
    _inherit= "purchase.order"

    transporter_id = fields.Many2one('res.partner', string="Transportista")
    importations = fields.Many2one('importations',string="Importaciones")

    @api.model
    def _prepare_picking(self):
        record = super(SaleOrderForm,self)._prepare_picking()
        if self.transporter_id:
            record['transporter_id']=self.transporter_id[0].id
        print("record",record)
        return record

class importaciones(models.Model):
    _name = 'importations'
    _rec_name = 'description'
    description = fields.Char('Descripcion de la Importacion')
    date_import = fields.Date(string='Fecha de Importacion')

class transportista(models.Model):
    _inherit = "stock.picking"

    transporter_id= fields.Many2one('res.partner',string='Transportista')
    transporter_name= fields.Char("Transportista",compute='get_id_transporter')
    transporter_ruc= fields.Char("RUC",compute='get_id_transporter',default="0000")
    
    @api.one
    def get_id_transporter(self):
        sql_query = """select ru.name, ru.nro_documento
        from stock_picking sp
        inner join purchase_order po
        on po.name='%s' and sp.group_id= po.group_id
        inner join res_partner ru
        on po.transporter_id = ru.id
        """ % self.origin
        self.env.cr.execute(sql_query)
        result = self.env.cr.dictfetchall()
        # print "----result ", result
        if (len(result)>0):
            self.transporter_ruc = result[0]['nro_documento']
            self.transporter_name = result[0]['name']
            self.ruc = self.transporter_ruc
        # else:
        #     self.transporter_ruc = "no"
        #     self.transporter_name = "no"
    @api.multi
    def write(self, vals):
        if (self.transporter_ruc):
            vals['ruc']= self.transporter_ruc
            # print "escribio" ,self.transporter_ruc
        res = super(transportista, self).write(vals)
        return res

