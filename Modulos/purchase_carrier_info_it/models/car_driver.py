# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class PurchaseOrderForm(models.Model):
    _inherit= "purchase.order"

    transporter_street = fields.Char(u'Dirección',related="transporter_id.street")
    transporter_phone = fields.Char(u'Teléfono',related="transporter_id.phone")
    transporter_email = fields.Char(u'Dirección',related="transporter_id.email")

