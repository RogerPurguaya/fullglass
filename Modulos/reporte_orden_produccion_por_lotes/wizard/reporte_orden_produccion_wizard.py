# -*- coding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api, exceptions
import codecs, pprint, pytz
from datetime import datetime, timedelta
from openerp import tools
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit,ImageReader
from cgi import escape
from reportlab.lib.units import inch, cm
import decimal
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128
from functools import reduce
import StringIO

class ReporteOrdenProduccionAlmacen(models.TransientModel):
	_name='reporte.orden.produccion.wizard'
	order_id = fields.Many2one('glass.order',string="OP")

	@api.multi
	def print_report_op(self):
		import sys
		reload(sys)		
		self.reporteador_lotes()
		sys.setdefaultencoding('iso-8859-1')
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		import os
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		vals = {
			'output_name': 'ordenproduccion_lotes.pdf',
			'output_file': open(direccion + "ordenproduccion_lotes.pdf", "rb").read().encode("base64"),	
		}
		sfs_id = self.env['export.file.save'].create(vals)
		return {
			"type": "ir.actions.act_window",
			"res_model": "export.file.save",
			"views": [[False, "form"]],
			"res_id": sfs_id.id,
			"target": "new",
		}

	@api.multi
	def reporteador_lotes(self):
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
		pdfmetrics.registerFont(TTFont('Calibri-Bold', 'CalibriBold.ttf'))
		width ,height  = A4  # 595 , 842
		wReal = width- 30
		hReal = height - 40
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		c = canvas.Canvas( direccion + "ordenproduccion_lotes.pdf", pagesize= A4)
		pos_inicial = hReal-140
		start_pos_left = 20
		size_widths = [25,160,75,30,40,40,40,40,90]
		total_width_size = reduce(lambda x,y: x+y,size_widths)
		totals = [0,0,0,0]
		aux_array = [0,0,0,0,0] # para almacenar auxiliares
		qty_cristales = 0
		pagina = 1
		textPos = 0
		
		self.cabezera_lotes(c,wReal,hReal,start_pos_left,size_widths)
		glass_order_lines = self.order_id.line_ids
		
		pagina, pos_inicial = self.verify_linea_lotes(c,wReal,hReal,pos_inicial,12,pagina,start_pos_left,size_widths)

		for line in glass_order_lines:
			c.setFont("Calibri", 8)
			pagina, pos_inicial = self.verify_linea_lotes(c,wReal,hReal,pos_inicial,12,pagina,start_pos_left,size_widths)

			tmp_pos = start_pos_left
			c.drawRightString(tmp_pos+size_widths[0]-10,pos_inicial,str(line.crystal_number) if line.crystal_number else '')
			tmp_pos += size_widths[0]

			c.drawString(tmp_pos+2,pos_inicial,line.product_id.name[:160] if line.product_id.name else '')
			tmp_pos += size_widths[1]

			measure = self._process_measures_item(line.base1,line.base2,line.altura1, line.altura2)
			c.drawString(tmp_pos+2, pos_inicial, measure)
			tmp_pos += size_widths[2]

			c.drawString(tmp_pos+2, pos_inicial,line.lot_line_id.lot_id.name if line.lot_line_id.lot_id.name else '')
			tmp_pos += size_widths[3]
			
			c.drawString(tmp_pos+2, pos_inicial, 'EM' if line.embalado else '')
			tmp_pos += size_widths[4]
			
			state= dict(self.order_id._fields['state'].selection).get(line.order_id.state)
			c.drawString(tmp_pos+2,pos_inicial,state)
			aux_array[0] = tmp_pos+2
			tmp_pos += size_widths[5]

			area = line.area if line.area else 0
			c.drawRightString(tmp_pos+size_widths[6]-2,pos_inicial,'{:,.4f}'.format(decimal.Decimal ("%0.4f" % area)))
			aux_array[1] = tmp_pos+size_widths[6]-2
			totals[0] += area
			tmp_pos += size_widths[6]

			peso = line.peso if line.peso else 0
			c.drawRightString(tmp_pos+size_widths[7]-2,pos_inicial,'{:,.2f}'.format(decimal.Decimal ("%0.2f" % peso)))
			totals[1] += peso
			aux_array[2] = tmp_pos+size_widths[7]-2
			tmp_pos += size_widths[7]
			location = line.order_id.warehouse_id.name if line.order_id.warehouse_id and line.lot_line_id.ingresado else ''
			c.drawString(tmp_pos+10,pos_inicial,location)
			
		c.line(start_pos_left,pos_inicial-2,start_pos_left+total_width_size,pos_inicial-2)
		c.drawString(start_pos_left, pos_inicial-12,'Nro Pzs.'+str(len(glass_order_lines)))
		c.drawRightString(aux_array[0], pos_inicial-12,'Totales:')
		c.drawRightString(aux_array[1], pos_inicial-12, '{:,.4f}'.format(decimal.Decimal ("%0.4f" % totals[0])))
		c.drawRightString(aux_array[2], pos_inicial-12, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % totals[1])))

		now = datetime.now() - timedelta(hours=5)
		c.drawString(start_pos_left+10, pos_inicial-48, 'Usuario: '+str(self.env.user.partner_id.name) +' '+ str(now)[:19])
		c.save()

	# cabezera_lotes para el segundo reporte
	@api.multi
	def cabezera_lotes(self,c,wReal,hReal,start_pos_left,size_widths=None):
		
		company = self.env['res.company'].search([])[0]
		if len(company) == 0:
			raise exceptions.Warning(u"No se creado compañía alguna.\n Configure los datos de su compañía para poder mostrarlos en este reporte.")
		
		if company.logo:
			file = base64.b64decode(company.logo)
			c.drawImage(ImageReader(StringIO.StringIO(file)),start_pos_left,792,width=75,height=40,mask=None)
		else:
			c.setFont("Calibri", 12)
			c.drawString(start_pos_left,800,company.name if company.name else 'Company')

		## Codigo temporal:
		invoice = ''
		if len(self.order_id.invoice_ids) > 0:
			invoice = self.order_id.invoice_ids[0].reference if self.order_id.invoice_ids[0].reference else ''

		# Datos de Conpañía para la cabecera
		c.setFont("Calibri", 6)
		c.drawString(start_pos_left,784,company.street if company.street else u'Address')
		c.drawString(start_pos_left,778,(u'Teféfono: '+str(company.phone)) if company.phone else 'no disponible')
		c.drawString(start_pos_left+70,778,(u'Fax: '+str(company.fax))if company.fax else 'no disponible')
		c.drawString(start_pos_left,770,company.website if company.website else 'website')
		c.drawString(start_pos_left+100,770,company.email if company.email else 'email')
		ruc = company.partner_id.nro_documento if company.partner_id.nro_documento else ''
		c.drawString(start_pos_left,762,'RUC: '+str(ruc))		
		
		pos_inicial = hReal-83
		posicion_indice = 1
		c.line(375,800,580,800)
		c.line(375,750,580,750)
		c.line(375,800,375,750)
		c.line(580,800,580,750)
		c.setFont("Calibri", 13)
		c.drawString( 410 , 785,'ORDEN DE PRODUCCION')
		c.drawString( 470 , 765, self.order_id.name)
		for i in range(0,2):
			c.line(start_pos_left,750-i,365,750-i)
		c.line(start_pos_left,745,365,745)
		c.setFont("Calibri", 8) 
		c.drawString(start_pos_left,730,'Documento:')
		c.drawString(start_pos_left+70,730,str(invoice))
		c.drawString(start_pos_left,722,'Cliente:')
		c.drawString(start_pos_left+70,722,self.order_id.partner_id.name)
		c.drawString(start_pos_left,714,'Obra:')
		c.drawString(start_pos_left+70,714, self.order_id.obra if self.order_id.obra else '')
		c.drawString(start_pos_left,706,'Direccion:')
		c.drawString(start_pos_left+70,706,self.order_id.partner_id.street if self.order_id.partner_id.street else '')
		c.drawString(start_pos_left,698,'Pto.Llegada:')
		llegada = self.order_id.sale_order_id.partner_shipping_id.street if self.order_id.sale_order_id.partner_shipping_id.street else ''
		c.drawString(start_pos_left+70,698,llegada)	
		c.drawString( 380 ,730,'Fecha Emision:')
		c.drawString( 460 ,730,self.order_id.date_sale_order)
		c.drawString( 380 ,722,'Fecha Produccion:')
		c.drawString( 460 ,722,self.order_id.date_production)
		c.drawString( 380 ,714,'Fecha Despacho:')
		c.drawString( 460 ,714,self.order_id.date_send)
		c.drawString( 380 ,706,'Fecha Entrega:')
		c.drawString( 460 ,706,self.order_id.date_delivery)
		c.drawString( 380 ,698,'Vendedor:')
		c.drawString( 460 ,698,self.order_id.seller_id.partner_id.name)
		c.line(start_pos_left,690,580,690)
		
		total_width = reduce(lambda x,y: x+y,size_widths) + start_pos_left
		c.line(start_pos_left,680,total_width,680)
		c.line(start_pos_left,660,total_width,660)
		c.line(start_pos_left,680,start_pos_left,660)
		c.line(total_width,680,total_width,660)
		headers = ['Cristal','Detalle','Medida','Lote','Embalado','Estado','M2','Peso','Ubicacion']
		if len(headers) != len(size_widths):
			print('El numero de headers y de anchos deben ser iguales :)')
			return
		pos = start_pos_left
		for i,item in enumerate(headers):
			c.drawCentredString(pos +int(size_widths[i]/2),667,item)
			pos += size_widths[i]

	@api.multi
	def verify_linea_lotes(self,c,wReal,hReal,posactual,valor,pagina,start_pos_left,size_widths):
		if posactual <40:
			c.showPage()
			self.cabezera_lotes(c,wReal,hReal,start_pos_left,size_widths)

			c.setFont("Calibri-Bold", 8)
			#c.drawCentredString(300,25,'Pág. ' + str(pagina+1))
			return pagina+1,hReal-160
		else:
			return pagina,posactual-valor

	# obtener las medidas a mostrar
	@api.multi
	def _process_measures_item(self,base1,base2,height1,height2):
		label = ''
		base1,base2,height1,height2 = str(base1),str(base2),str(height1),str(height2)
		if base1 == base2:
			label += base1
		else:
			label += base1 + '/' + base2
		label += ' x '
		if height1 == height2:
			label += height1
		else:
			label += height1 + '/' + height2
		return label
