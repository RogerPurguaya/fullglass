# -*- coding: utf-8 -*-
from openerp.osv import osv
import base64
from openerp import models, fields, api, exceptions
import codecs
import pprint

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
from reportlab.lib.utils import simpleSplit
from cgi import escape
from reportlab.lib.units import inch, cm
import decimal



from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.units import mm

from reportlab.graphics.barcode import code128



class GlassFurnaceOut(models.Model):
	_inherit='glass.furnace.out'

			
	@api.multi
	def impresion_etiquetas(self):
		self.reporteador()
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		import os

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		vals = {
			'output_name': 'etiquetasproductos.pdf',
			'output_file': open(direccion + "etiquetasproductos.pdf", "rb").read().encode("base64"),	
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
	def x_aument(self,a):
		a[0] = a[0]+1

	@api.multi
	def reporteador(self):

		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
		pdfmetrics.registerFont(TTFont('Calibri-Bold', 'CalibriBold.ttf'))

		width ,height  = ( 7.62 * cm , 5.08 * cm) #216 144
		print ( 7.62 * cm , 5.08 * cm)
		wReal = width- 3
		hReal = height - 4

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		c = canvas.Canvas( direccion + "etiquetasproductos.pdf", pagesize=( 7.62 * cm , 5.08 * cm))
		inicio = 0
		pos_inicial = hReal-40
		libro = None
		voucher = None
		
		pagina = 1
		textPos = 0
		
		#self.cabezera(c,wReal,hReal)

		pos_inicial = pos_inicial-43
		posicion_indice = 1

		c.setFont("Calibri", 8)
		pagina, pos_inicial = self.verify_linea(c,wReal,hReal,pos_inicial,12,pagina)
		
		lines = self.line_ids.filtered(lambda x: not x.lot_line_id.is_break) # filter list		
		if len(lines) == 0:
			raise exceptions.Warning('No hay cristales aptos para etiquetar')
		for line in lines:
			c.setFont("Calibri", 12)
			c.drawString(15,100,'O/P: '+line.lot_line_id.order_prod_id.name if line.lot_line_id.order_prod_id else '')
			c.setFont("Calibri-Bold", 9)
			c.drawRightString(200,100,self._process_measures_item(line.base1,line.base2,line.altura1,line.altura2))
			c.setFont("Calibri", 10)
			nro_crystal = line.crystal_number + '/' + str(len(line.lot_line_id.order_prod_id.line_ids))
			c.drawString( 15 ,90,'Cristal Nro. '+nro_crystal)
			c.setFont("Calibri", 7)
			c.drawString( 15 ,84,self.particionar_text(  line.lot_id.product_id.name if line.lot_id.product_id.name else '',180) )
			c.setFont("Calibri-Bold", 10)
			c.drawString( 15 ,76,self.particionar_text( line.partner_id.name if line.partner_id.name else '',0) )
			c.setFont("Calibri", 10)
			c.drawString( 15 ,68,self.particionar_text( line.partner_id.street if line.partner_id.street else '',0) )

			c.line(15,65,195,65)
			c.line(15,55,195,55)
			#las lineas verticales
			c.line(15,65,15,55)
			c.line(45,65,45,55)
			c.line(75,65,75,55)
			c.line(105,65,105,55)
			c.line(135,65,135,55)
			c.line(165,65,165,55)
			c.line(195,65,195,55)
			c.setFont("Calibri", 9)

			c.drawString( 30 ,58,self.particionar_text( self.name if self.name else '',0) )
			c.drawString( 80 ,46,self.particionar_text( line.lot_line_id.search_code if line.lot_line_id.search_code else '',10) )

			c.drawString( 55 ,58,self.particionar_text( line.lot_line_id.calc_line_id.pulido1.code  if line.lot_line_id.calc_line_id.pulido1.code else '',10) )
			
			if line.lot_line_id.calc_line_id.entalle != 0:
				c.drawString( 88 ,58,self.particionar_text( 'E' ,10) )
			else:
				pass

			if line.lot_line_id.calc_line_id.plantilla == True:
				c.drawString( 121 ,58,self.particionar_text( 'PL' ,10) )
			else:
				pass

			if line.lot_line_id.calc_line_id.embalado == True:
				c.drawString( 190 ,58,self.particionar_text( 'EM' ,10) )
			else:
				pass
			string = line.lot_line_id.search_code
			st = code128.Code128(string,barHeight=.3*inch,barWidth=1.2)
			st.drawOn(c,10,15)
			line.etiqueta = True
			c.showPage()
		c.save()


	@api.multi
	def particionar_text(self,c,tam):
		tet = ""
		for i in range(len(c)):
			tet += c[i]
			lines = simpleSplit(tet,'Calibri',8,tam)
			if len(lines)>1:
				return tet[:-1]
		return tet

	@api.multi
	def verify_linea(self,c,wReal,hReal,posactual,valor,pagina):
		if posactual <40:
			c.showPage()
			#self.cabezera(c,wReal,hReal)

			c.setFont("Calibri-Bold", 8)
			#c.drawCentredString(300,25,'Pág. ' + str(pagina+1))
			return pagina+1,hReal-95
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
		label += 'X'
		if height1 == height2:
			label += height1
		else:
			label += height1 + '/' + height2
		return label




