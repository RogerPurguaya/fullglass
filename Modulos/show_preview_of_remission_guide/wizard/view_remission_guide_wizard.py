from odoo import fields,models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import reduce

# Wizard contenedor para ver los cristales de los stock_moves a retornar:
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

#	
#  Contenedor para lineas de cristles a devolver desde APT
# class Detail_Crystals_Entered_Wizard_Lines(models.TransientModel):
# 	_name = 'detail.crystals.entered.wizard.line'
	
# 	check = fields.Boolean(string='Seleccion')
# 	wizard_id = fields.Many2one('detail.crystals.entered.wizard')
# 	origen = fields.Char(string='Origen')
# 	lote= fields.Char(string='Lote') 
# 	cantidad = fields.Float('Cantidad' ,digits=(12,4))
# 	picking_id = fields.Integer('Picking')
# 	venta = fields.Char(string='Venta')
# 	base1 = fields.Integer(string='Base 1')
# 	base2 = fields.Integer(string='Base 2')
# 	altura1 = fields.Integer(string='Altura 1')
# 	altura2 = fields.Integer(string='Altura 1')
# 	numero_cristal = fields.Integer(string='Numero Cristal')
# 	product_id = fields.Integer(string='Producto ID')
# 	cristal_area = fields.Float(string='Cristal Area' ,digits=(12,4))
# 	templado = fields.Boolean(string='Templado')
# 	ingresado = fields.Boolean(string='Ingresado')
# 	entregado = fields.Boolean(string='Entregado') 
# 	requisicion = fields.Char(string='Requisicion')
# 	gol_id = fields.Integer('Glass order line id')
# 	gll_id = fields.Integer('Glass Lote Line id')
# 	sm_id  =  fields.Integer('Move ID')
# 	mode = fields.Char('Modo')
# 	#campo para motivo de rotura:
# 	motive = fields.Selection([
# 		('Vidrio roto','Vidrio roto'), 
# 		('Error entalle','Error entalle'), 
# 		('Error medidas','Error medidas'), 
# 		('Vidrio rayado','Vidrio rayado'), 
# 		('Planimetria','Planimetria'), 
# 		('Error ventas','Error ventas'), 
# 		('Materia prima','Materia prima')])