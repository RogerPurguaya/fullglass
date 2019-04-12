from odoo import fields,models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import reduce

# Wizard para mostrar la preview de las guias de remision:
class Preview_Remission_Guide_Wizard(models.TransientModel):
	_name = 'preview.remission.guide.wizard'
	date = fields.Date(string='Fecha')
	reference = fields.Char('Documento')
	partner = fields.Char('Partner')
	nro_doc = fields.Char('Nro doc partner')
	direction = fields.Char(string='Direccion')
	phone = fields.Char('Telefono')
	transporter = fields.Char('Transportista')	
	start_point = fields.Char('Punto de partida')
	end_point = fields.Char('Punto de llegada')
	mode = fields.Selection([('internal','internal'),('out_to_customers','out_to_customers')])
	data = fields.Text('Detalle de lineas')
	ruc = fields.Char('RUC')