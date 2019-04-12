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
import StringIO

class GlassOrder(models.Model):
	_inherit='glass.order'

	@api.multi
	def ordenprod_buttom(self):
		self.reporteador_op()
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		import os
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		vals = {
			'output_name': 'ordenproduccion.pdf',
			'output_file': open(direccion + "ordenproduccion.pdf", "rb").read().encode("base64"),	
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
	def reporteador_op(self):
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
		pdfmetrics.registerFont(TTFont('Calibri-Bold', 'CalibriBold.ttf'))
		width ,height  =A4  # 595 , 842
		wReal = width- 30
		hReal = height - 40
		check = 'X'
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		c = canvas.Canvas( direccion + "ordenproduccion.pdf", pagesize= A4)
		pos_inicial = hReal-165
		start_pos_left = 20
		#size_widths = [70,104,78,78,70,70]
		size_widths = [70,104,78,16,16,16,16,16,70,70]
		totals = [0,0,0,0]
		aux_array = [0,0,0,0,0] # para almacenar auxiliares
		qty_cristales = 0
		pagina = 1
		textPos = 0
		self.cabezera_op(c,wReal,hReal,start_pos_left)
		glass_order_lines = self.sale_lines
		
		pagina, pos_inicial = self.verify_linea_op(c,wReal,hReal,pos_inicial,12,pagina,start_pos_left)

		for item in glass_order_lines:
			#weight = self.env['product.product'].search([('id','=',item.product_id[0].id)])
			c.setFont("Calibri-Bold", 8)
			pagina, pos_inicial = self.verify_linea_op(c,wReal,hReal,pos_inicial,40,pagina,start_pos_left)
			weight_pro = item.product_id.weight if item.product_id.weight else 0
			c.drawString(start_pos_left, pos_inicial, item.name if item.name else '')
			c.line(start_pos_left,pos_inicial-2,552,pos_inicial-2)
			
			for line in item.id_type_line:
				c.setFont("Calibri", 8)
				pagina, pos_inicial = self.verify_linea_op(c,wReal,hReal,pos_inicial,12,pagina,start_pos_left)

				tmp_pos = start_pos_left + 60 #para que sea mas a la derecha
				c.drawString(tmp_pos+2, pos_inicial, line.nro_cristal if line.nro_cristal else '')
				tmp_pos += size_widths[0]

				label = self._process_measures_item(line.base1,line.base2,line.altura1,line.altura2)
				c.drawString(tmp_pos+2, pos_inicial, label)
				tmp_pos += size_widths[1]
				c.drawString(tmp_pos+27, pos_inicial, line.descuadre if line.descuadre else '')
				tmp_pos += size_widths[2]
				c.drawString(tmp_pos-28, pos_inicial, line.page_number if line.page_number else '')
				c.drawString(tmp_pos+6, pos_inicial, check if line.pulido1 else '')

				tmp_pos += size_widths[3]
				c.drawString(tmp_pos+6, pos_inicial, str(line.entalle) if line.entalle else '')
				tmp_pos += size_widths[4]
				c.drawString(tmp_pos+6, pos_inicial, check if line.plantilla else '')
				tmp_pos += size_widths[5]
				c.drawString(tmp_pos+6, pos_inicial, check if line.arenado else '')
				tmp_pos += size_widths[6]
				c.drawString(tmp_pos+6, pos_inicial, check if line.embalado else '')
				tmp_pos += size_widths[7] + size_widths[8]
				
				area = line.area if line.area else 0
				c.drawRightString(tmp_pos-2, pos_inicial, '{:,.4f}'.format(decimal.Decimal ("%0.4f" % area)))
				aux_array[0] = tmp_pos-2
				tmp_pos += size_widths[9]
				totals[0] += area

				weight = weight_pro * area
				c.drawRightString(tmp_pos-2, pos_inicial, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % weight)))
				aux_array[1] = tmp_pos-2
				totals[1] += weight

				qty_cristales += line.cantidad

				#print vertical lines:
				aux = start_pos_left+60
				for x in size_widths:
					c.line(aux,pos_inicial+10,aux,pos_inicial-2)
					aux += x
				c.line(aux,pos_inicial+10,aux,pos_inicial-2)
			
			c.line(start_pos_left+60,pos_inicial-2,552,pos_inicial-2)
			c.drawString(start_pos_left+60, pos_inicial-12, 'Nro. de Piezas: '+str(qty_cristales))
			c.drawRightString(aux_array[0], pos_inicial-12, '{:,.4f}'.format(decimal.Decimal ("%0.4f" % totals[0])))
			c.drawRightString(aux_array[1], pos_inicial-12, '{:,.2f}'.format(decimal.Decimal ("%0.2f" % totals[1])))
			totals = [0,0,0,0]
			qty_cristales = 0

		now = datetime.now() - timedelta(hours=5)
		c.drawString(start_pos_left+10, pos_inicial-48, 'Usuario: '+str(self.env.user.partner_id.name) +' '+ str(now)[:19])
		c.save()

	# cabezera_op para el segundo reporte
	@api.multi
	def cabezera_op(self,c,wReal,hReal,start_pos_left,size_widths=None):
		
		company = self.env['res.company'].search([])[0]
		if len(company) == 0:
			raise exceptions.Warning(u"No se creado compañía alguna.\n Configure los datos de su compañía para poder mostrarlos en este reporte.")
		

		if company.logo:
			file = base64.b64decode(company.logo)
			c.drawImage(ImageReader(StringIO.StringIO(file)),start_pos_left,792,width=75,height=40,mask=None)
		else:
			c.setFont("Calibri", 12)
			c.drawString(start_pos_left,800,company.name if company.name else 'Company')

		invoice = ''
		if len(self.invoice_ids) > 0:
			invoice = self.invoice_ids[0].reference if self.invoice_ids[0].reference else ''

		# Datos de Conpañía para la cabecera
		c.setFont("Calibri", 6)
		c.drawString(start_pos_left,784,company.street if company.street else u'Address')
		c.drawString(start_pos_left,778,(u'Teféfono: '+str(company.phone)) if company.phone else 'no disponible')
		c.drawString(start_pos_left+70,778,(u'Fax: '+str(company.fax))if company.fax else 'no disponible')
		c.drawString(start_pos_left,770,company.website if company.website else 'Fax')
		c.drawString(start_pos_left+100,770,company.email if company.email else 'Fax')
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
		c.drawString( 470 , 765, self.name)
		for i in range(0,2):
			c.line(start_pos_left,750-i,365,750-i)
		c.line(start_pos_left,745,365,745)
		c.setFont("Calibri", 8) 
		c.drawString(start_pos_left,730,'Documento:')
		c.drawString(start_pos_left+70,730,str(invoice))
		c.drawString(start_pos_left,722,'Cliente:')
		c.drawString(start_pos_left+70,722,self.partner_id.name)
		c.drawString(start_pos_left,714,'Obra:')
		c.drawString(start_pos_left+70,714, self.obra if self.obra else '')
		c.drawString(start_pos_left,706,'Direccion:')
		c.drawString(start_pos_left+70,706,self.partner_id.street if self.partner_id.street else '')
		c.drawString(start_pos_left,698,'Pto.Llegada:')
		llegada = self.sale_order_id.partner_shipping_id.street if self.sale_order_id.partner_shipping_id.street else ''
		c.drawString(start_pos_left+70,698,llegada)	
		c.drawString( 380 ,722,'Fecha Emision:')
		c.drawString( 450 ,722, str(self.sale_order_id.date_order))
		c.drawString( 380 ,714,'Fecha Entrega:')
		c.drawString( 450 ,714,str(self.date_delivery))
		c.drawString( 380 ,706,'Vendedor:')
		c.drawString( 450 ,706, self.seller_id.partner_id.name)
		c.line(start_pos_left,690,580,690)
		
		c.line(80,680,550,680)
		c.line(80,600,550,600)

		c.line(80,680,80,600)
		c.line(150,680,150,600)
		c.line(254,680,254,600)
		c.line(332,680,332,600)
		c.line(410,680,410,600)
		c.line(480,680,480,600)
		c.line(550,680,550,600)
		c.drawString( 90 ,640,'Nro. Cristal')
		c.drawString( 175 ,640,'Medidas (mm)')
		c.drawString( 300 ,640,'Nro.')
		c.drawString( 300 ,630,'Pag.')
		c.drawString( 430 ,640,'Metros')
		c.drawString( 427 ,630,'Cuadrados')
		c.drawString( 495 ,640,'Peso (Kg.)')
		c.rotate(90)
   		c.drawString(22*cm, -10*cm, "Descuadre")
   		c.drawString(22*cm, -12.3*cm, "Pulido")
   		c.drawString(22*cm, -12.8*cm, "Entalle")
   		c.drawString(22*cm, -13.3*cm, "Plantilla")
   		c.drawString(22*cm, -13.8*cm, "Arenado")
   		c.drawString(22*cm, -14.3*cm, "Embalado")
		c.rotate(-90)

	@api.multi
	def verify_linea_op(self,c,wReal,hReal,posactual,valor,pagina,start_pos_left):
		if posactual <40:
			c.showPage()
			self.cabezera_op(c,wReal,hReal,start_pos_left)

			c.setFont("Calibri-Bold", 8)
			#c.drawCentredString(300,25,'Pág. ' + str(pagina+1))
			return pagina+1,hReal-205
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
		