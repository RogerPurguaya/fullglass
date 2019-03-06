# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_category(models.Model):
	_inherit = 'product.category'
	able_code = fields.Boolean(u"Generar código", default=True, inverse ='serie' )
	
	@api.multi
	def serie(self):
		print "este es el valor de able_code   ",self.able_code
		if self.able_code:
			print "esta true"
			id_seq = self.env['ir.sequence'].search([('name','=','Categoria Producto Codigo')])
			if len(id_seq)>0:
				id_seq = id_seq[0]
			else:
				id_seq = self.env['ir.sequence'].create({'name':'Categoria Producto Codigo','implementation':'standard','active':True,'prefix':'','padding':3,'number_increment':1,'number_next_actual' :1})
			self.write({'codigo_categoria': id_seq.next_by_id()})
		else:
			print "esta false"
			self.write({'codigo_categoria': ""})

	
class product_atributo(models.Model):
	_name = 'product.atributo'

	name = fields.Char('Atributo')
	detalle_ids = fields.One2many('product.atributo.valores','atributo_id','Detalle')

class product_atributo_valores(models.Model):
	_name = 'product.atributo.valores'

	name = fields.Char('Valor')
	code = fields.Char('Codigo')
	atributo_id = fields.Many2one('product.atributo','Atributo')

	special = fields.Boolean('Atributo Especial')

	@api.model
	def create(self,vals):
		t = super(product_atributo_valores,self).create(vals)
		if t.special == False:
			id_seq = self.env['ir.sequence'].search([('name','=','Atributos Codigo')])
			if len(id_seq)>0:
				id_seq = id_seq[0]
			else:
				id_seq = self.env['ir.sequence'].create({'name':'Atributos Codigo','implementation':'standard','active':True,'prefix':'','padding':3,'number_increment':1,'number_next_actual' :1})

			t.code = id_seq.next_by_id()
		else:
			id_seq = self.env['ir.sequence'].search([('name','=','Atributos Codigo Especial')])
			if len(id_seq)>0:
				id_seq = id_seq[0]
			else:
				id_seq = self.env['ir.sequence'].create({'name':'Atributos Codigo Especial','implementation':'standard','active':True,'prefix':'','padding':3,'number_increment':1,'number_next_actual' :1})

			t.code = id_seq.next_by_id()
		return t

class product_selecionable(models.Model):
	_name = 'product.selecionable'

	atributo_id = fields.Many2one('product.atributo','Atributo')
	valor_id = fields.Many2one('product.atributo.valores','Valor')
	product_id = fields.Many2one('product.template','Producto')

class product_codigo_nativo(models.Model):
	_name = 'product.codigo.nativo'

	name = fields.Char('Producto Origen',required=True)
	code = fields.Char('Código Producto Fuente',readonly=True)
	vacio = fields.Boolean('Vacio',default=False)

	@api.model
	def create(self,vals):
		t = super(product_codigo_nativo,self).create(vals)

		if t.vacio:
			return t

		id_seq = self.env['ir.sequence'].search([('name','=','Producto Template Codigo')])
		if len(id_seq)>0:
			id_seq = id_seq[0]
		else:
			id_seq = self.env['ir.sequence'].create({'name':'Producto Template Codigo','implementation':'standard','active':True,'prefix':'','padding':3,'number_increment':1,'number_next_actual' :1})

		t.code = id_seq.next_by_id()
		return t

class product_template(models.Model):
	_inherit = 'product.template'

	codigo_inicial = fields.Many2one('product.codigo.nativo','Codigo del Producto')
	atributo_ids = fields.One2many('product.selecionable','product_id','Atributos')

	categ_id_ant = fields.Many2one('product.category','Categoria 2')
	categ_id_ant_ant = fields.Many2one('product.category','Categoria 1')



	@api.model
	def create(self,vals):
		t = super(product_template,self).create(vals)
		t.write({})
		return t

	@api.one
	def write(self,vals):	
		t = super(product_template,self).write(vals)
		self.refresh()
		print self.env.context
		if 'nomas' in self.env.context:
			pass
		else:			
			namet =  self.categ_id.codigo_categoria  if self.categ_id.codigo_categoria else '000'
			namet += '.' + ( self.codigo_inicial.code if self.codigo_inicial.id and self.codigo_inicial.code  else '000' )
			cont = 0

			not_specials = []
			for item in self.atributo_ids.sorted(key=lambda r: r.id):
				special = item.valor_id.special
				if special:
					pass
				else:
					not_specials.append(item)

			for i in not_specials:
				
				if cont <2:
					cont+= 1
					namet += '.' + ( i.valor_id.code if i.valor_id.code else '000' )

			for i in range(2-cont):
				namet += '.000'
			
			self.refresh()
			new_n = self.codigo_inicial.name + ' '

			for i in self.atributo_ids:
				new_n += i.valor_id.name + ','


			if self.codigo_inicial.vacio:
				namet = False

			self.with_context({'nomas':1,'lang': 'es_PE'}).write({'default_code': namet,'name':new_n[:-1],'categ_id_ant': self.categ_id.parent_id.id, 'categ_id_ant_ant':self.categ_id.parent_id.parent_id.id if self.categ_id.parent_id.id else False})
		return t
