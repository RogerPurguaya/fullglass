# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError



class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = "sale.advance.payment.inv"



	@api.depends('procurement_group_id_compute_ids','albaranes')
	@api.onchange('albaranes','procurement_group_id_compute')
	def onchange_albaranes_compute(self):
		orders = self.env['sale.order'].browse(self._context.get('active_ids',[False]))
		cont = [-1,-1,-1]
		for i in orders:
			if i.procurement_group_id.id:
				if i.procurement_group_id.id not in cont:
					cont.append(i.procurement_group_id.id)	
			# for line in i.order_line:
				# if line.procurement_group_id.id:
					# if line.procurement_group_id.id not in cont:
						# cont.append(line.procurement_group_id.id)
		res = {'domain':{'albaranes': [('group_id','in',cont),('invoice_id','=',False)] } }
		return res