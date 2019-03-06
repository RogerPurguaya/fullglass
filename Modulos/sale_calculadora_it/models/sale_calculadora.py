# -*- coding: utf-8 -*-
from odoo.osv import osv
from odoo import fields, models,api, _
from odoo.exceptions import UserError
from decimal import *
from lxml import etree
import pprint
import json
from openerp.osv import osv

class SaleCalculatorType(models.Model):
	_name = 'sale.calculadora.type'

	codigo = fields.Char(u"Código")
	modelo = fields.Char(u"Modelo")
	descripcion = fields.Char(u"Descripcion")
	unidad_kardex = fields.Char(u"Unidad Kardex")
	precio = fields.Float(u"Precio")
	cantidad= fields.Char(u"Cantidad")
	dato = fields.Char(u"Datos Fijo")
	base = fields.Integer(u"Base")
	inc = fields.Integer(u"INC(B)")
	altura = fields.Integer(u"Altura")


class pulidoProforma(models.Model):
	_name="sale.pulido.proforma"

	name = fields.Char("Tipo Pulido")
	code = fields.Char(u"Código")


class SaleCalculatorProformaLine(models.Model):
	_name = 'sale.calculadora.proforma.line'


	@api.one
	@api.depends('base1','base2','altura1','altura2','cantidad')
	def _medidas1(self):
		prof= self

		t_area=0.0
		t_per =0.0
		if prof.base2==0:
			prof.base2=prof.base1
		if prof.altura2==0:
			prof.altura2=prof.altura1
		maxbase= prof.base2
		maxaltura = prof.altura2
		if prof.base1>prof.base2:
			maxbase= prof.base1
		if prof.altura1>prof.altura2:
			maxaltura = prof.altura1
	
		t_area = (Decimal(maxbase * maxaltura)*prof.cantidad)/(1000000)
		t_per = Decimal((prof.base1 + prof.altura1 + prof.base2 + prof.altura2)*prof.cantidad)/1000
		t_area1=t_area
		if 'id_main' in self._context:
			lineref = self.env['sale.order.line'].search([('id_type','=',self._context.get('id_main')),('id_type','!=',False)])
			if lineref:
				total_area = float(t_area)
				unidadventa = lineref.product_uom
				unidad = lineref.product_id.categ_id.uom_min_sale
				valor = unidad._compute_quantity(total_area,unidadventa)
				
				if lineref.product_id.categ_id.min_sale>valor:
					valor2 = unidad._compute_quantity(lineref.product_id.categ_id.min_sale,unidadventa)
					t_area1 = valor2*prof.cantidad
		
		prof.area=float(t_area)
		prof.perimetro=float(t_per)
		prof.area_vendida=float(t_area1)
			


	@api.onchange('base1','base2','altura1','altura2','cantidad')
	def _medidas(self):
		return False
		for prof in self:
			print 2222
			
			t_area=0.0
			t_per =0.0
			if prof.base2==0:
				prof.base2=prof.base1
			if prof.altura2==0:
				prof.altura2=prof.altura1
			maxbase= prof.base2
			maxaltura = prof.altura2
			if prof.base1>prof.base2:
				maxbase= prof.base1
			if prof.altura1>prof.altura2:
				maxaltura = prof.altura1
		
			t_area = (Decimal(maxbase * maxaltura)*prof.cantidad)/(1000000)
			t_per = Decimal((prof.base1 + prof.altura1 + prof.base2 + prof.altura2)*prof.cantidad)/1000
			t_area1=t_area
			if 'id_main' in self._context:
				lineref = self.env['sale.order.line'].search([('id_type','=',self._context.get('id_main')),('id_type','!=',False)])
				if lineref:
					total_area = float(t_area)
					unidadventa = lineref.product_uom
					unidad = lineref.product_id.categ_id.uom_min_sale
					valor = unidad._compute_quantity(total_area,unidadventa)
					
					if lineref.product_id.categ_id.min_sale>valor:
						valor2 = unidad._compute_quantity(lineref.product_id.categ_id.min_sale,unidadventa)
						t_area1 = valor2*prof.cantidad
			
			prof.area=float(t_area)
			prof.perimetro=float(t_area)
			prof.area_vendida=float(t_area)
			
		

	proforma_id = fields.Many2one('sale.calculadora.proforma',"Lineas")
	name = fields.Char(u'Cálculos')
	cantidad = fields.Integer(u"Cantidad")
	nro_cristal = fields.Char(u"Número de Cristal",readonly=False)
	base1 = fields.Integer("Base1 (L 4)")
	base2 = fields.Integer("Base2 (L 2)")
	altura1 = fields.Integer("Altura1 (L 1)")
	altura2 = fields.Integer("Altura2 (L 3)")
	descuadre = fields.Char("Descuadre",size=7,inverse="_grafico")
	perimetro = fields.Float(u"Perímetro (ML)", digits=(12,2), inverse="_grafico", compute='_medidas1', store=True)
	area = fields.Float(u"Área m2",digits=(12,4), inverse="_grafico", compute='_medidas1', store=True)
	area_vendida= fields.Float(u"Área Vendida",digits=(12,4), inverse="_grafico", compute='_medidas1', store=True)
	peso = fields.Float("Peso")
	min_vend = fields.Float(u"Mínimo Vendible")
	pulido1 = fields.Many2one("sale.pulido.proforma","Pulido")
	# pulido1 = fields.Selection([("cantoplano","01 Canto Plano"),("cantobrillante","02 Canto Brillante"),("aristasabatidas","03 Aristas abatidas")],"Pulido")
	entalle = fields.Integer("Entalle")
	biselado = fields.Boolean("Biselado")
	lavado = fields.Boolean("Lavado")
	perforaciones = fields.Boolean("Perforaciones")
	plantilla = fields.Boolean("Plantilla")
	embalado = fields.Boolean("Embalado")
	insulado = fields.Boolean("Insulado")
	arenado = fields.Boolean("Arenado")
	page_number = fields.Char(u"Nro. Pág.")
	image = fields.Binary("imagen")

	is_service = fields.Boolean('Es servicio')
	type_prod = fields.Char('tipoproducto')

	



	# _sql_constraints = [
	# 		('crystalnumber_uniq', 'unique(proforma_id,nro_cristal)', u'El número de cristal está repetido'),
	# 	]





	@api.model
	def create(self,vals):
		t = super(SaleCalculatorProformaLine,self).create(vals)
		return t

	@api.multi
	def showimage(self):
		print "showimage"
		self.ensure_one()
		self._grafico()
		self.proforma_id.image = self.image
		self.proforma_id.update(
			{
				'image':self.image
			})
	

		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_image_wizard_form' % module)
		ctx = self._context.copy()
		ctx.update({'id_calc':self.proforma_id.id})
		data = {
					
				'name':'Imagen',
				'view_type':'form',
				'view_mode':'form',
				'res_model':'sale.calculadora.proforma.line',
				'view_id':view.id,
				'type':'ir.actions.act_window',
				'res_id':self.id,
				'nodestroy':True,
				'target':'new',
				'context':ctx,

		}
		return data
	@api.multi
	def reshowcalc(self):
		print "reshowcalc"
		lineref = self.env['sale.order.line'].browse(self._context.get('active_id'))
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_calculadora_presupuesto_linea_wizard_form' % module)
		idact=False
		lineref = self.env['sale.order.line'].search([('id_type','=',self.proforma_id.id)])
		if lineref.product_id.type == 'service':
			view = self.env.ref('%s.view_calculadora_presupuesto_linea2_wizard_form' % module)
		idact = self.proforma_id.id
		data = {					
				'name':'Calculadora',
				'view_type':'form',
				'view_mode':'form',
				'res_model':'sale.calculadora.proforma',
				'view_id':view.id,
				'type':'ir.actions.act_window',
				'key2':"client_action_multi",
				'multi':"True",
				'res_id':idact,
				'nodestroy':True,
				'target':'new',
		}
		return data	

		
	
	@api.multi
	@api.onchange('nro_cristal','cantidad')
	def validate_crystal_number(self):
		print "validate_crystal_number"
		self.ensure_one()
		cadnro = self.nro_cristal
		ncant=0
		if cadnro:
			if ',' not in cadnro:
				acadnro = cadnro.split('-')
				if len(acadnro)>2:
					raise UserError(u"No se puede tener más de un rango en el número de cristales: "+cadnro)

				if len(acadnro)>1:
					if int(acadnro[0])>int(acadnro[1]):
						raise UserError(u"El número de cristales debe comenzar con un número menor al siguiente: "+cadnro)			
					
					nini = int(acadnro[0])			
					nend = int(acadnro[1])
					ncant=nend-nini+1
				else:
					ncant=1
				if ncant>0 and self.cantidad>0:
					if ncant != self.cantidad:
						raise UserError(u"El número de cristales debe corresponder a la cantidad indicada: "+cadnro)			
			else:
				acadnro = cadnro.split(',')
				existentes = []
				if len(acadnro)>0 and self.cantidad:
					for a in acadnro:
						if a in existentes:
							raise UserError(u"Un valor está duplicado:" + cadnro)			
						existentes.append(a)
					if len(acadnro) != self.cantidad:
						raise UserError(u"El número de cristales debe corresponder a la cantidad indicada: "+cadnro)			


			

	@api.onchange('descuadre')
	def desonchange(self):
		print "desonchange"
		self.ensure_one()
		if self.descuadre:
			self.lavado = True
		else:
			self.lavado = False

		prof = self
		if not prof.altura1:
			return
		if not prof.altura2:
			return
		if not prof.base1:
			return
		if not prof.base2:
			return
		
		# lineref = self.env['sale.order.line'].search([('id_type','=',self.proforma_id.id)])

		if self.proforma_id.type_line == 'service':
			return
		h1=prof.altura1
		h2=prof.altura2
		b1=prof.base1
		b2=prof.base2
		dcd=[]
		if prof.descuadre:
			dcd = [int(x) for x in prof.descuadre.split(',')]
		data_line = """ 
		Detalle de la linea: 
		Nro: """+prof.nro_cristal+"""
		Altura 1:"""+str(prof.altura1)+"""
		Altura 2:"""+str(prof.altura2)+"""
		Base 1:"""+str(prof.base1)+"""
		Base 2:"""+str(prof.base2)

		if 1 in dcd:
			if b2==b1:
				raise UserError(_(u"Descuadre: No existe descuadre en el lado 1"+data_line))
		if 3 in dcd:
			if b2==b1:
				raise UserError(_(u"Descuadre: No existe descuadre en el lado 3"+data_line))

		if 2 in dcd:
			if h2==h1:
				raise UserError(_(u"Descuadre: No existe descuadre en el lado 2"+data_line))
		if 4 in dcd:
			if h2==h1:
				raise UserError(_(u"Descuadre: No existe descuadre en el lado 4"+data_line))

		return False
	
	@api.depends('descuadre','area','altura1','altura2','base1','base2')
	def _grafico(self):
		import PIL.ImageDraw as ImageDraw
		import PIL.Image as Image
		from PIL import ImageFont
		print "_grafico"
		for prof in self:
			is_product = True
			if self.proforma_id.type_line == 'service':
				is_product=False

			w=1000
			h=1000
			image = Image.new("RGB", (w, h),color=(255,255,255))
			draw = ImageDraw.Draw(image)
			left= 300
			top=150
			h1=prof.altura1
			h2=prof.altura2
			b1=prof.base1
			b2=prof.base2

			dcd=[]
			if prof.descuadre:
				dcd = [int(x) for x in prof.descuadre.split(',')]

			l = [b1,b2,h1,h2]
			e_max = max(l)
			if e_max==0:
				return False
			size = [x*500 /e_max for x in l]

			size=[]
			size.append(b1*500 /e_max )
			size.append(b2*500 /e_max )
			size.append(h1*500 /e_max )
			size.append(h2*500 /e_max )

			p0 = (0.+left ,h/2+top)
			p1 = (0.+left, h/2-size[2]+top)
			p2 = (size[1]+left, h/2-size[3]+top)
			
			p3 = (size[0]+left, h/2-0.+top)
			p3_x = size[0]+left
			p3_y = h/2-0.+top

			data_line = """ 
			Detalle de la linea: 
			Nro: """+(prof.nro_cristal if prof.nro_cristal else '')+"""
			Altura 1:"""+(str(prof.altura1) if str(prof.altura1) else '')+"""
			Altura 2:"""+(str(prof.altura2) if str(prof.altura2) else '')+"""
			Base 1:"""+(str(prof.base1) if str(prof.base1) else '')+"""
			Base 2:"""+(str(prof.base2) if str(prof.base2) else '')


			if is_product:
				if 1 in dcd:
					if b2==b1:
						raise UserError(_(u"Descuadre: No existe descuadre en el lado 1"+data_line))
				if 3 in dcd:
					if b2==b1:
						raise UserError(_(u"Descuadre: No existe descuadre en el lado 3"+data_line))

				if 2 in dcd:
					if h2==h1:
						raise UserError(_(u"Descuadre: No existe descuadre en el lado 2"+data_line))
				if 4 in dcd:
					if h2==h1:
						raise UserError(_(u"Descuadre: No existe descuadre en el lado 4"+data_line))


			if 1 in dcd:				
				if b2>b1:
					p0 = ( p1[0]+(size[1]-size[0]),p0[1])
					p3_x = size[1]+left
				else:
					p1=(p1[0]+(size[0]-size[1]),p1[1])
					p2=(p3[0],p2[1])


				

			if 4 in dcd:
				if h2<h1:
					tmp=p1
					p1=(p0[0],p2[1])
					p3=(p3[0],p1[1]-(size[2]-size[3]))
					p3_y = p1[1]+(size[3]-(size[2]-size[3]))
				else:
					p2 = (size[1]+left, h/2-size[2]+top)
					p3_y = h/2-(size[2]-size[3])+top

			p3 = (p3_x,p3_y)
					



			points =(
				p0,
				p1,
				p2,
				p3,
				p0,)
			import os
			dirpath = os.environ.get('HOME') or os.getcwd()
			
			path = os.path.join(os.path.dirname(os.path.abspath(__file__)))+"/arial.ttf"
			font = ImageFont.truetype(path, 36)
			y=30
			# draw.text((20, size[2]/3+top), "LADO 1",font=font,fill=(255, 43, 0,128))
			# draw.text((20, size[2]/3+top+y), str(h1)+" mm",font=font,fill=(51, 123, 164))

			# draw.text((size[0]+250, size[2]/3+top), "LADO 3",font=font,fill=(255, 43, 0,128))
			# draw.text((size[0]+250, size[2]/3+top+y), str(h2)+" mm",font=font,fill=(51, 123, 164))

			# draw.text((size[0]/3+left,20), "LADO 2",font=font,fill=(255, 43, 0,128))
			# draw.text((size[0]/3+left,20+y), str(b2)+" mm",font=font,fill=(51, 123, 164))

			# draw.text((size[0]/3+left,size[3]+200), "LADO 4",font=font,fill=(255, 43, 0,128))
			# draw.text((size[0]/3+left,size[3]+200+y), str(b1)+" mm",font=font,fill=(51, 123, 164))

			# h1=prof.altura1
			# h2=prof.altura2
			# b1=prof.base1
			# b2=prof.base2


			# size.append(b1*500 /e_max )
			# size.append(b2*500 /e_max )
			# size.append(h1*500 /e_max )
			# size.append(h2*500 /e_max )

			maxheight=size[2]
			if p0[1]<p3[1]:
				maxheight = size[3]

			maxwidth=size[0]
			if size[0]<size[1]:
				maxwidth=size[1]

			moreleft = p1[0]
			if p0[0]<p1[0]:
				moreleft = p0[0]

			moreright = p2[0]
			if p2[0]<p3[0]:
				moreright = p3[0]

			moretop=p1[1]
			if p1[1]>p2[1]:
				moretop=p2[1]

			moreboot=p0[1]
			if p0[1]<p3[1]:
				moreboot=p3[1]



			draw.text((moreleft-300,(moreboot-(maxheight/2))), "LADO 1",font=font,fill=(255, 43, 0,128))
			draw.text((moreleft-300,((moreboot-(maxheight/2))+30)), str(h1)+" mm",font=font,fill=(51, 123, 164))

			draw.text((moreleft+((maxwidth/2)-120),moretop-80), "LADO 2",font=font,fill=(255, 43, 0,128))
			draw.text((moreleft+((maxwidth/2)-120),moretop-50), str(b2)+" mm",font=font,fill=(51, 123, 164))

			draw.text((moreright+20,(moreboot-(maxheight/2))), "LADO 3",font=font,fill=(255, 43, 0,128))
			draw.text((moreright+20,(moreboot-(maxheight/2))+30), str(h2)+" mm",font=font,fill=(51, 123, 164))

			

			draw.text((moreleft+((maxwidth/2)-120),moreboot+30), "LADO 4",font=font,fill=(255, 43, 0,128))
			draw.text((moreleft+((maxwidth/2)-120),moreboot+60), str(b1)+" mm",font=font,fill=(51, 123, 164))

			draw.polygon((points), fill=(105,238,113))


			# draw.text((0.+left ,h/2+top),"a",fill=(51, 123, 164))
			# draw.text((0.+left, h/2-size[2]+top),"b",fill=(51, 123, 164))
			# draw.text((size[1]+left, h/2-size[3]+top),"c",fill=(51, 123, 164))
			# draw.text((size[0]+left, h/2-0.+top),"d",fill=(51, 123, 164))

			for d in dcd:
				if d not in [1,2,3,4]:
					raise UserError(_(u"Descuadre: Sólo válido número de lados: 1,2,3,4"))
				else:
					color = 'Red'
					if not is_product:
						color = 'Gold'
					draw.line((points[d-1][0],points[d-1][1],points[d][0],points[d][1]),fill=color,width=15)

			import os
			direccion=self.env['main.parameter'].search([])[0].dir_create_file

			image.save(direccion+'vidrio.png')
			prof.update({
				'image':open(str(direccion)+"vidrio.png", "rb").read().encode("base64"),

			})

class SaleCalculatorProforma(models.Model):
	_name = 'sale.calculadora.proforma'
	#id_line = fields.Many2many('sale.calculadora.proforma.line')
	id_line = fields.One2many('sale.calculadora.proforma.line','proforma_id','lista de items')
	total_perimetro = fields.Float(u"Perímetro Total (ML)",compute='_totales',track_visibility='always', digits=(12,2),store=False)
	total_area = fields.Float(u"Área Total (M2)",compute='_totales',track_visibility='always', digits=(12,4),store=False)
	total_area_cobrada = fields.Float(u"Área Cobrada (M2)",compute='_totales',track_visibility='always', digits=(12,4),store=False)
	qty = fields.Integer('Cantidad de Vidrios',compute='_totales',track_visibility='always', digits=(12,4),store=False)
	tipo= fields.Char("nro_cristal")
	image = fields.Binary("imagen")
	type_line = fields.Char('Tipo Producto')
	nlineas = fields.Integer('numlineas')
	total_items=fields.Integer('Cantidad de Vidrios',compute='_totales',track_visibility='always', digits=(12,4),store=False)
	iseditable = fields.Boolean('se edita',default=True)
	invoice_prev = fields.Boolean('factura previa',default=False)
	invoiced = fields.Boolean('Facturado',default=False)

	qty_invoiced=fields.Float('Cantidad Facturada',calculate='_totales',store=False)
	qty_invoiced_rest=fields.Float('Saldo por atender',calculate='_totales',store=False)
	#new code

	sale_order_ids = fields.One2many('sale.order.line','id_type','Products')
	
	# Producto a mostrar en la calculadora
	def _get_default_product(self):
		if self._context['product']:
			return self.env['product.product'].browse(self._context['product']).name

	show_product = fields.Char(string='Producto',compute='_get_name_product',default=_get_default_product)

	@api.depends('sale_order_ids')
	def _get_name_product(self):
		for record in self:
			if len(record.sale_order_ids) > 0:
				record.show_product = record.sale_order_ids[0].product_id.name
				
	
	@api.one
	def savecal(self):
		return True


	@api.model
	def default_get(self, default_fields):
		#print "default_get"
		b=""
		if self._context['is_service']:
			a = 'service'
		else:
			a='product'
		#print a
		contextual_self = self.with_context(default_type_line=a)
		return super(SaleCalculatorProforma, contextual_self).default_get(default_fields)

	@api.model
	def create(self,vals):
		prev_vals=[]
		#print "create"
		if 'id_line' in vals:
			for line_v in vals['id_line']:
				if line_v[0] in [0,1]:
					
					line = line_v[2]
					data_line = """ 
					Detalle de la linea: 
					Nro: """+line['nro_cristal']+"""
					Altura 1:"""+str(line['altura1'])+"""
					Altura 2:"""+str(line['altura2'])+"""
					Base 1:"""+str(line['base1'])+"""
					Base 2:"""+str(line['base2'])

					cadnro = line['nro_cristal']
					ncant=0
					if cadnro:
						if ',' not in cadnro:
							acadnro = cadnro.split('-')
							if len(acadnro)>1:					
								nini = int(acadnro[0])			
								nend = int(acadnro[1])+1
								for a in range(nini,nend):
									if str(a) in prev_vals:
										raise UserError(u"El número de cristal repetido "+str(a)+data_line)			
									else:
										prev_vals.append(str(a))
							else:
								if str(acadnro[0]) in prev_vals:
									raise UserError(u"El número de cristal repetido: "+str(acadnro[0])+data_line)			
								else:	
									prev_vals.append(str(acadnro[0]))
						else:
							acadnro = cadnro.split(',')
							if len(acadnro)>0 and self.cantidad:
								for a in acadnro:
									if str(a) in prev_vals:
										raise UserError(u"El número de cristal repetido: "+str(a)+data_line)			
									else:	
										prev_vals.append(str(a))


					



		t = super(SaleCalculatorProforma,self).create(vals)
		total_area=0
		lineref=self.env['sale.order.line'].browse(self._context['active_id'])
		total_area=t.total_area_cobrada
		vals1 ={'id_type':t.id,}
		eseditable=False
		tienefactura = False

		if lineref.order_id.state=='draft':
			eseditable=True
		if lineref.order_id.invoice_count>0:
			tienefactura=True
			
		tieneoc =False
		for line in lineref.order_id.order_line:
			for l2 in line.id_type.id_line:
				if l2.production_id:
					tieneoc=True
					break
			if tieneoc:
				break
		if tieneoc:
			if lineref.order_id.before_invoice:
				eseditable=True
			else:
				eseditable=False
		else:
			eseditable=True
		if eseditable:
			if tienefactura:
				if lineref.product_uom_qty<total_area:
					raise UserError(u"La suma de las áreas ingresadas supera a la facturada")	
				
			else:
				if lineref.order_id.state!='draft':
					if lineref.product_uom_qty<total_area:
						raise UserError(u"La suma de las áreas ingresadas supera a la facturada")	
					else:
						if not lineref.order_id.before_invoice:
							vals1.update({'product_uom_qty':total_area,})
				else:
					if lineref.order_id.before_invoice:
						if lineref.product_uom_qty<total_area:
							raise UserError(u"La suma de las áreas ingresadas supera a la facturada")		
					else:
						vals1.update({'product_uom_qty':total_area,})
		lineref.write(vals1)
		
		return t

	@api.one
	def getprevals(self,vals):
		prev_vals = []
		ids_changes = []

		if 'id_line' in vals:
			for line in vals['id_line']:
				if line[0] in [1]:
					ids_changes.append(line[1])

		actuales=self
		for line in actuales.id_line:
			if line.id in ids_changes:
				continue
			cadnro = line.nro_cristal
			ncant=0
			if cadnro:
				if ',' not in cadnro:
					acadnro = cadnro.split('-')
					if len(acadnro)>1:					
						nini = int(acadnro[0])			
						nend = int(acadnro[1])+1
						for a in range(nini,nend):
							prev_vals.append(str(a))
					else:
						prev_vals.append(str(acadnro[0]))
				else:
					acadnro = cadnro.split(',')
					if len(acadnro)>0 and self.cantidad:
						for a in acadnro:
							prev_vals.append(str(a))

		return prev_vals

	@api.one
	def validate_write(self,vals):
		prev_vals=self.getprevals(vals)[0]
		#print 'prev_vals',prev_vals
		if 'id_line' in vals:
			new_vals=[]
			for line_v in vals['id_line']:
				if line_v[0] in [0,1]:
					
					line = line_v[2]
					if 'nro_cristal' not in line:
						continue
					if line_v[0]==1:
						ant = self.env['sale.calculadora.proforma.line'].browse(line_v[1])
					data_line = """ 
					Detalle de la linea: 
					Nro: """+(line['nro_cristal'] if 'nro_cristal' in line else ant.nro_cristal)+ """
					Altura 1:"""+(str(line['altura1'])  if 'altura1' in line else str(ant.altura1))+"""
					Altura 2:"""+(str(line['altura2']) if 'altura2' in line else str(ant.altura2))+"""
					Base 1:"""+(str(line['base1']) if 'base1' in line else str(ant.base1))+"""
					Base 2:"""+(str(line['base2']) if 'base2' in line else str(ant.base2))

					
					cadnro = line['nro_cristal']
					ncant=0
					if cadnro:
						if ',' not in cadnro:
							#print 'sin ,,'
							acadnro = cadnro.split('-')
							#print 'acadnro',acadnro
							if len(acadnro)>1:					
								nini = int(acadnro[0])			
								nend = int(acadnro[1])+1
								for a in range(nini,nend):
									if str(a) in prev_vals:
										#print 1
										raise UserError(u"El número de cristal repetido : "+str(a)+data_line)			
									else:
										prev_vals.append(str(a))
							else:
								if str(acadnro[0]) in prev_vals:
									#print 12
									raise UserError(u"El número de cristal repetido: "+str(acadnro[0])+data_line)			
								else:	
									prev_vals.append(str(acadnro[0]))
						else:
							acadnro = cadnro.split(',')
							if len(acadnro)>0 and self.cantidad:
								for a in acadnro:
									if str(a) in prev_vals:
										#print 13
										raise UserError(u"El número de cristal repetido: "+str(a)+data_line)			
									else:	
										prev_vals.append(str(a))
			

				

	@api.one
	def write(self,vals):
		#print "write"
		if self.iseditable==False:
			return super(SaleCalculatorProforma,self).write(vals)
		self.validate_write(vals)
		t = super(SaleCalculatorProforma,self).write(vals)
		lineref=False

		if self._context.get('active_model',False):
			if self._context.get('active_model')=='sale.order.line':
				if self._context.get('active_id',False):
					lineref = self.env['sale.order.line'].browse(self._context.get('active_id'))
			else:
				if self._context.get('active_model')=='sale.calculadora.proforma.line':
					if self._context.get('id_calc',False):
						lineref = self.env['sale.order.line'].search([('id_type','=',self._context.get('id_calc',False))])
		
		if lineref:
			
			eseditable=False
			tienefactura = False

			if lineref.order_id.state=='draft':
				eseditable=True
			if lineref.order_id.invoice_count>0:
				tienefactura=True
				
			tieneoc =False
			for line in lineref.order_id.order_line:

				for l2 in line.id_type.id_line:
					if l2.production_id:
						#print 111111
						tieneoc=True
						break
				if tieneoc:
					break
			if tieneoc:
				if lineref.order_id.before_invoice:
					eseditable=True
				else:
					eseditable=False
			else:
				eseditable=True

			newvals = {
				'iseditable':eseditable,
				'invoice_prev':lineref.order_id.before_invoice,
				'invoiced':tienefactura,
			}
			t = super(SaleCalculatorProforma,self).write(newvals)

			
			total_area=self.total_area_cobrada

			vals1={}
			if eseditable:
				if tienefactura:
					if lineref.product_uom_qty<total_area:
						raise UserError(u"La suma de las áreas ingresadas supera a la facturada")	
				else:
					# if lineref.order_id.state!='draft':
					# 	if lineref.product_uom_qty<total_area:
					# 		raise UserError(u"La suma de las áreas ingresadas supera a la facturada")	
					# else:
					if lineref.order_id.before_invoice:
						if lineref.product_uom_qty<total_area:
							raise UserError(u"La suma de las áreas ingresadas supera a la facturada")		
					else:
						vals1.update({'product_uom_qty':total_area,})
						lineref.write(vals1)
		return t		

	@api.multi
	def cantidad(self):
		print "cantidad"
		ini = 1
		fin = 0
		for prof in self:
			for line in prof.id_line:
				line.write({})
				# ini = ini
				# fin = ini+line.cantidad-1
				# line.write({
				# 	'nro_cristal': str(ini)+" - " +str(fin),
				# })
				# ini = fin+1
		
		# self.tipo = str(ini)

	@api.one
	@api.depends('id_line.cantidad','id_line.area','id_line.perimetro','id_line.area_vendida',)
	def _totales(self):
		import pprint
		print "_totales"
		# pprint.pprint(self._context)
		prof = self
		t_area=0.0
		t_area_vendida=0.0
		t_per =0.0
		t_qty=0.0
		nitems=0
		newtotal = 0.0000
		lineref=False
		if self._context.get('active_model',False):
			if self._context.get('active_model')=='sale.order.line':
				if self._context.get('active_id',False):
					lineref = self.env['sale.order.line'].browse(self._context.get('active_id'))
			else:
				if self._context.get('active_model')=='sale.calculadora.proforma.line':
					if self._context.get('id_calc',False):
						lineref = self.env['sale.order.line'].search([('id_type','=',self._context.get('id_calc',False))])

		if lineref:
			
			for line in prof.id_line:
				t_area += line.area
				t_per += line.perimetro
				t_qty+=line.cantidad
				nitems=nitems+line.cantidad
				total_area = float(line.area)
				unidadventa = lineref.product_uom
				unidad = lineref.product_id.categ_id.uom_min_sale
				valor = unidad._compute_quantity(total_area/line.cantidad,unidadventa,round=False)
				#print valor,total_area,lineref.product_id.categ_id.min_sale
				if lineref.product_id.categ_id.min_sale>valor:
					valor2 = unidad._compute_quantity(lineref.product_id.categ_id.min_sale,unidadventa,round=False)
					t_area_vendida += (valor2*line.cantidad)
				else:
					t_area_vendida+=(valor*line.cantidad)
				newtotal = newtotal + (t_area_vendida*lineref.price_subtotal)
			self.total_area=t_area
			self.total_perimetro=t_per
			self.total_area_cobrada=t_area_vendida
			self.qty=t_qty
			self.total_items=t_qty
			self.qty_invoiced=lineref.product_uom_qty
			self.qty_invoiced_rest=lineref.product_uom_qty-t_area_vendida
			#self.show_product = lineref.product_id.name

		

		# data = {
		# 	'total_area':t_area,
		# 	'total_perimetro':t_per,
		# 	'total_area_cobrada':t_area_vendida,
		# 	'qty':t_qty,
		# 	'total_items':t_qty,
		# }
		# prof.update(data)

class SaleLineCalculadora(models.Model):
	_inherit = 'sale.order.line'
	id_type = fields.Many2one('sale.calculadora.proforma',string="Calculadora")
	id_type_line = fields.One2many(related='id_type.id_line')
	#id_type_line = fields.Many2many(related='id_type.id_line')
	product_uom_qty = fields.Float(string='Quantity',required=True, default=1.0,digits=(12,4))

	# @api.onchange('id_type')
	# def _get_q(self):
	# 	for line in self:
	# 		line.update({
	# 		'product_uom_qty': line.id_type.total_area_cobrada,
	# 		})


	@api.multi
	def showcalc(self):
		print "showcalc"
		self.ensure_one()
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_calculadora_presupuesto_linea_wizard_form' % module)
		idact=False
		ctx = self._context.copy()
		ctx.update({'is_service':False,'product':self.product_id.id})		
		if self.product_id.type == 'service':
			view = self.env.ref('%s.view_calculadora_presupuesto_linea2_wizard_form' % module)
			ctx.update({'is_service':True})
		if self.id_type:
			idact = self.id_type.id

		data = {
					
				'name':'Calculadora',
				'view_type':'form',
				'view_mode':'form',
				# 'views' : [(view_image_wizard_form,'form')],
				'res_model':'sale.calculadora.proforma',
				'view_id':view.id,
				'type':'ir.actions.act_window',
				# 'key2':"client_action_multi",
				# 'multi':"True",
				'res_id':idact,
				# 'nodestroy':True,
				'target':'new',
				'context':ctx,
		}
		return data		