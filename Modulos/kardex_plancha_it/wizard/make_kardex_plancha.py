# -*- coding: utf-8 -*-
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import time
import odoo.addons.decimal_precision as dp
from openerp.osv import osv
import base64
from odoo import models, fields, api
import codecs
values = {}

class make_kardex_plancha(models.TransientModel):
	_name = "make.kardex.plancha"
	period_id = fields.Many2one('account.period','Periodo')
	fini= fields.Date('Fecha inicial',required=True)
	ffin= fields.Date('Fecha final',required=True)
	products_ids=fields.Many2many('product.product','rel_wiz_kardex_plancha','product_id','kardex_id')
	location_ids=fields.Many2many('stock.location','rel_kardex_location_plancha','location_id','kardex_id','Ubicacion',required=True)
	allproducts=fields.Boolean('Todos los productos',default=True)
	destino = fields.Selection([('csv','CSV'),('crt','Pantalla')],'Destino')
	check_fecha = fields.Boolean('Editar Fecha')
	alllocations = fields.Boolean('Todos los almacenes',default=True)

	fecha_ini_mod = fields.Date('Fecha Inicial')
	fecha_fin_mod = fields.Date('Fecha Final')
	analizador = fields.Boolean('Analizador',compute="get_analizador")

	@api.multi
	def get_analizador(self):
		print "contexto",self.env.context
		if 'tipo' in self.env.context:
			if self.env.context['tipo'] == 'valorado':
				self.analizador = True
			else:
				self.analizador = False				
		else:
			self.analizador = False

	_defaults={
		'destino':'crt',
		'check_fecha': False,
		'allproducts': True,
		'alllocations': True,
	}
	
	@api.onchange('fecha_ini_mod')
	def onchange_fecha_ini_mod(self):
		self.fini = self.fecha_ini_mod


	@api.onchange('fecha_fin_mod')
	def onchange_fecha_fin_mod(self):
		self.ffin = self.fecha_fin_mod

	@api.model
	def default_get(self, fields):
		res = super(make_kardex_plancha, self).default_get(fields)
		import datetime
		fecha_hoy = str(datetime.datetime.now())[:10]
		fecha_inicial = fecha_hoy[:4] + '-01-01' 
		res.update({'fecha_ini_mod':fecha_inicial})
		res.update({'fecha_fin_mod':fecha_hoy})
		res.update({'fini':fecha_inicial})
		res.update({'ffin':fecha_hoy})

		#locat_ids = self.pool.get('stock.location').search(cr, uid, [('usage','in',('internal','inventory','transit','procurement','production'))])
		locat_ids = self.env['stock.location'].search([('usage','in',('internal','inventory','transit','procurement','production'))])
		locat_ids = [elemt.id for elemt in locat_ids]
		res.update({'location_ids':[(6,0,locat_ids)]})
		return res

	@api.onchange('alllocations')
	def onchange_alllocations(self):
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
			self.location_ids = [(6,0,locat_ids.ids)]
		else:
			self.location_ids = [(6,0,[])]

	@api.onchange('period_id')
	def onchange_period_id(self):
		self.fini = self.period_id.date_start
		self.ffin = self.period_id.date_stop

	

	
	@api.multi
	def do_csvtoexcel(self):
		cad = ""

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		if self.alllocations == True:
			locat_ids = self.env['stock.location'].search( [('usage','in',('internal','inventory','transit','procurement','production'))] )
			lst_locations = locat_ids.ids
		else:
			lst_locations = self.location_ids.ids
		lst_products  = self.products_ids.ids
		productos='{'
		almacenes='{'
		date_ini=self.fini
		date_fin=self.ffin
		if self.allproducts:
			lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids
			print lst_products

		else:
			lst_products = self.products_ids.ids

		if len(lst_products) == 0:
			raise osv.except_osv('Alerta','No existen productos seleccionados')

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'
		# raise osv.except_osv('Alertafis',[almacenes,productos])


		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'kardex_producto.xlsx')
		worksheet = workbook.add_worksheet("Kardex")
		bold = workbook.add_format({'bold': True})
		bold.set_font_size(8)
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(8)
		boldbord.set_bg_color('#DCE6F1')

		especial1 = workbook.add_format({'bold': True})
		especial1.set_align('center')
		especial1.set_align('vcenter')
		especial1.set_text_wrap()
		especial1.set_font_size(15)
		
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberseis = workbook.add_format({'num_format':'0.000000'})
		numberseis.set_font_size(8)
		numberocho = workbook.add_format({'num_format':'0.00000000'})
		numberocho.set_font_size(8)
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_font_size(8)
		numberdos.set_border(style=1)
		numberdos.set_font_size(8)
		numbertres.set_border(style=1)			
		numberseis.set_border(style=1)			
		numberocho.set_border(style=1)		
		numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})	
		numberdosbold.set_font_size(8)
		x= 10				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		worksheet.merge_range(1,5,1,10, "KARDEX FISICO", especial1)
		worksheet.write(2,0,'FECHA INICIO:',bold)
		worksheet.write(3,0,'FECHA FIN:',bold)

		worksheet.write(2,1,self.fini)
		worksheet.write(3,1,self.ffin)			
		import datetime		

		worksheet.merge_range(8,0,9,0, u"Ubicación Origen",boldbord)
		worksheet.merge_range(8,1,9,1, u"Ubicación Destino",boldbord)
		worksheet.merge_range(8,2,9,2, u"Almacún",boldbord)
		worksheet.merge_range(8,3,9,3, u"Tipo de Operación",boldbord)
		worksheet.merge_range(8,4,9,4, u"Categoría",boldbord)
		worksheet.merge_range(8,5,9,5, u"Producto",boldbord)
		worksheet.merge_range(8,6,9,6, u"Código P.",boldbord)
		worksheet.merge_range(8,7,9,7, u"Fecha",boldbord)
		worksheet.merge_range(8,8,9,8, u"Doc. Almacén",boldbord)				

		worksheet.merge_range(8,9,9,9, u"UM COMPRA",boldbord)
		worksheet.write(8,10, u"Ingreso",boldbord)
		worksheet.write(9,10, u"Físico",boldbord)
		worksheet.write(8,11, u"Salida",boldbord)
		worksheet.write(9,11, u"Física",boldbord)
		worksheet.write(8,12, u"Saldo",boldbord)
		worksheet.write(9,12, u"Físico",boldbord)



		worksheet.merge_range(8,13,9,13, u"Unidad",boldbord)
		worksheet.write(8,14, "Ingreso",boldbord)
		worksheet.write(9,14, "Cantidad",boldbord)
		worksheet.write(8,15, "Salida",boldbord)
		worksheet.write(9,15, "Cantidad",boldbord)
		worksheet.write(8,16, "Saldo",boldbord)
		worksheet.write(9,16, "Cantidad",boldbord)

		cadsql = """ 
			 
		select 
		origen.complete_name AS "Ubicación Origen", 
		destino.complete_name AS "Ubicación Destino", 
		almacen.complete_name AS "Almacén",
		vstf.motivo_guia AS "Tipo de operación",
		pc.name as "Categoria",
		product_name.name as "Producto",
		pp.default_code as "Codigo P.",
		pu.name as "unidad",
		vstf.fecha as "Fecha",
		sp.name as "Doc. Almacén", 
		vstf.entrada as "Entrada", 
		vstf.salida as "Salida",
		pu_plan.name as uoncompra,
		vstf.entrada_plancha,
		vstf.salida_plancha,
		round(vstf.factor,4) as factor

		from 
		(
		select date::date as fecha,location_id as origen, location_dest_id as destino, location_dest_id as almacen, product_qty as entrada, 
		0 as salida,id as stock_move,guia as motivo_guia,product_id,estado,qtycompra AS entrada_plancha, 0 as salida_plancha,uoncompra,factor from vst_kardex_fisico_plancha
		union all
		select date::date as fecha,location_id as origen, location_dest_id as destino, location_id as almacen, 0 as entrada, 
		product_qty as salida,id as stock_move ,guia as motivo_guia ,product_id ,estado,0 as entrada_plancha, qtycompra as salida_plancha,uoncompra,factor from vst_kardex_fisico_plancha
		) as vstf
		inner join stock_location origen on origen.id = vstf.origen
		inner join stock_location destino on destino.id = vstf.destino
		inner join stock_location almacen on almacen.id = vstf.almacen
		inner join product_product pp on pp.id = vstf.product_id
		INNER JOIN ( SELECT pp.id, 
		pt.name::text || COALESCE((' ('::text || string_agg(pav.name::text, ', '::text)) || ')'::text, ''::text) AS name
		FROM product_product pp
		JOIN product_template pt ON pt.id = pp.product_tmpl_id
		LEFT JOIN product_attribute_value_product_product_rel pavpp ON pavpp.product_product_id = pp.id
		LEFT JOIN product_attribute_value pav ON pav.id = pavpp.product_attribute_value_id
		GROUP BY pp.id, pt.name) product_name ON product_name.id = pp.id

		inner join product_template pt on pt.id = pp.product_tmpl_id
		inner join product_category pc on pc.id = pt.categ_id
		inner join product_uom pu on pu.id = (CASE WHEN pt.unidad_kardex IS NOT NULL THEN pt.unidad_kardex else pt.uom_id end )
		inner join stock_move sm on sm.id = vstf.stock_move
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_uom pu_plan on vstf.uoncompra = pu_plan.id
		left join purchase_order po on po.id = sp.po_id
		where vstf.fecha >='""" +str(date_ini)+ """' and vstf.fecha <='""" +str(date_fin)+ """'
		and vstf.product_id in """ +str(tuple(s_prod))+ """
		and vstf.almacen in """ +str(tuple(s_loca))+ """
		and vstf.estado = 'done'
		and almacen.usage = 'internal'
		order by 
		almacen.id,pp.id,pu_plan.id,vstf.fecha,vstf.entrada desc 
		"""
		
		self.env.cr.execute(cadsql)

		ingreso1= 0
		ingreso2= 0
		salida1= 0
		salida2= 0

		saldo = 0
		saldo_plancha = 0
		almacen = None
		producto = None
		for line in self.env.cr.fetchall():
			if almacen == None:
				almacen = (line[2] if line[2] else '')
				producto = (line[5]+line[12] if line[5]+line[12] else '')
				saldo = line[10] - line[11]
				saldo_plancha = line[13] - line[14]
			elif almacen != (line[2] if line[2] else '') or producto != (line[5]+line[12] if line[5]+line[12] else ''):					
				almacen = (line[2] if line[2] else '')
				producto = (line[5]+line[12] if line[5]+line[12] else '')
				saldo = line[10] - line[11]
				saldo_plancha = line[13] - line[14]
			else:
				saldo = saldo + line[10] - line[11]
				saldo_plancha = saldo_plancha+ line[13] - line[14]

			worksheet.write(x,0,line[0] if line[0] else '' ,bord )
			worksheet.write(x,1,line[1] if line[1] else '' ,bord )
			worksheet.write(x,2,line[2] if line[2] else '' ,bord )
			worksheet.write(x,3,line[3] if line[3] else '' ,bord )
			worksheet.write(x,4,line[4] if line[4] else '' ,bord )
			worksheet.write(x,5,line[5] if line[5] else '' ,bord )
			worksheet.write(x,6,line[6] if line[6] else '' ,bord )
			worksheet.write(x,7,line[8] if line[8] else '' ,bord )
			worksheet.write(x,8,line[9] if line[9] else '' ,bord )
			worksheet.write(x,9,line[12] if line[12] else '' ,bord )
			worksheet.write(x,10,line[13] if line[13] else '' ,bord )
			worksheet.write(x,11,line[14] if line[14] else '' ,bord )
			worksheet.write(x,12,saldo_plancha ,numberdos )
			worksheet.write(x,13,line[7] if line[7] else '' ,bord )
			worksheet.write(x,14,line[10] if line[10] else 0 ,numberdos )				
			worksheet.write(x,15,line[11] if line[11] else 0 ,numberdos )
			worksheet.write(x,16,saldo ,numberdos )
			
			x = x +1

		tam_col = [11,11,5,5,7,5,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]


		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:Z', tam_col[19])

		workbook.close()

		
		f = open(direccion + 'kardex_producto.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'Kardex.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		sfs_id = self.env['export.file.save'].create(vals)

		#import os
		#os.system('c:\\eSpeak2\\command_line\\espeak.exe -ves-f1 -s 170 -p 100 "Se Realizo La exportación exitosamente Y A EDWARD NO LE GUSTA XDXDXDXDDDDDDDDDDDD" ')

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}

	@api.multi
	def do_csv(self):
		data = self.read()
		cad=""
		if data[0]['products_ids']==[]:
			if data[0]['allproducts']:
				if data[0]['allproducts']==False:
					raise osv.except_osv('Alerta','No existen productos seleccionados')
					return
				else:
					#prods= self.pool.get('product.product').search(cr,uid,[])
					lst_products  = self.env['product.product'].search([]).ids
			else:
				raise osv.except_osv('Alerta','No existen productos seleccionados')
				return
		else:
			lst_products  = data[0]['products_ids']

		s_prod = [-1,-1,-1]
		s_loca = [-1,-1,-1]
		
		lst_locations = data[0]['location_ids']
		productos='{0,'
		almacenes='{0,'
		date_ini=data[0]['fini']
		date_fin=data[0]['ffin']
		if 'allproducts' in data[0]:
			if data[0]['allproducts']:
				#lst_products  = self.pool.get('product.product').search(cr,uid,[])
				lst_products = self.env['product.product'].with_context(active_test=False).search([]).ids
			else:
				lst_products  = data[0]['products_ids']
		else:
			lst_products  = data[0]['products_ids']

		if 'alllocations' in data[0]:
			lst_locations = self.env['stock.location'].search([]).ids

		for producto in lst_products:
			productos=productos+str(producto)+','
			s_prod.append(producto)
		productos=productos[:-1]+'}'
		for location in lst_locations:
			almacenes=almacenes+str(location)+','
			s_loca.append(location)
		almacenes=almacenes[:-1]+'}'
		# raise osv.except_osv('Alertafis',[almacenes,productos])
		#print 'tipo',context['tipo']
		#direccionid = self.pool.get('main.parameter').search(cr,uid,[])[0]
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		#direccion=self.pool.get('main.parameter').browse(cr,uid,direccionid,context).dir_create_file

		if self._context['tipo']=='fisico':
			cadf=u"""
			copy (select 
		origen.complete_name AS "Ubicación Origen", 
		destino.complete_name AS "Ubicación Destino", 
		almacen.complete_name AS "Almacén",
		vstf.motivo_guia AS "Tipo de operación",
		pc.name as "Categoria",
		product_name.name as "Producto",
		pp.default_code as "Codigo P.",
		
		vstf.fecha as "Fecha",
		sp.name as "Doc. Almacén", 
		pu_plan.name as uoncompra,
		vstf.entrada_plancha,
		vstf.salida_plancha,
		round(vstf.factor,4) as factor,
		pu.name as "unidad",
		vstf.entrada as "Entrada", 
		vstf.salida as "Salida"
		

		from 
		(
		select date::date as fecha,location_id as origen, location_dest_id as destino, location_dest_id as almacen, product_qty as entrada, 
		0 as salida,id as stock_move,guia as motivo_guia,product_id,estado,qtycompra AS entrada_plancha, 0 as salida_plancha,uoncompra,factor from vst_kardex_fisico_plancha
		union all
		select date::date as fecha,location_id as origen, location_dest_id as destino, location_id as almacen, 0 as entrada, 
		product_qty as salida,id as stock_move ,guia as motivo_guia ,product_id ,estado,0 as entrada_plancha, qtycompra as salida_plancha,uoncompra,factor from vst_kardex_fisico_plancha
		) as vstf
		inner join stock_location origen on origen.id = vstf.origen
		inner join stock_location destino on destino.id = vstf.destino
		inner join stock_location almacen on almacen.id = vstf.almacen
		inner join product_product pp on pp.id = vstf.product_id
		INNER JOIN ( SELECT pp.id, 
		pt.name::text || COALESCE((' ('::text || string_agg(pav.name::text, ', '::text)) || ')'::text, ''::text) AS name
		FROM product_product pp
		JOIN product_template pt ON pt.id = pp.product_tmpl_id
		LEFT JOIN product_attribute_value_product_product_rel pavpp ON pavpp.product_product_id = pp.id
		LEFT JOIN product_attribute_value pav ON pav.id = pavpp.product_attribute_value_id
		GROUP BY pp.id, pt.name) product_name ON product_name.id = pp.id

		inner join product_template pt on pt.id = pp.product_tmpl_id
		inner join product_category pc on pc.id = pt.categ_id
		inner join product_uom pu on pu.id = (CASE WHEN pt.unidad_kardex IS NOT NULL THEN pt.unidad_kardex else pt.uom_id end )
		inner join stock_move sm on sm.id = vstf.stock_move
		inner join stock_picking sp on sp.id = sm.picking_id
		inner join product_uom pu_plan on vstf.uoncompra = pu_plan.id
		left join purchase_order po on po.id = sp.po_id
				where vstf.fecha >='""" +str(date_ini)+ u"""' and vstf.fecha <='""" +str(date_fin)+ u"""'
				and vstf.product_id in """ +str(tuple(s_prod))+ u"""
				and vstf.almacen in """ +str(tuple(s_loca))+ u"""
				and vstf.estado = 'done'
				and almacen.usage = 'internal'
				order by 
				almacen.id,pp.id,pu_plan.id,vstf.fecha,vstf.entrada desc 


				) to '"""+direccion+u"""kardex.csv'  WITH DELIMITER ',' CSV HEADER 
			"""
		else:
			cadf="select * from get_kardex_fis_sumi("+date_ini.replace("-","") + "," + date_fin.replace("-","") + ",'" + productos + "'::INT[], '" + almacenes + "'::INT[]) order by location_id,product_id,fecha,esingreso,nro"							
	# raise osv.except_osv('Alertafis',cadf)

		self.env.cr.execute(cadf)
		import gzip
		import shutil
		# E:\REPORTES/
		# with open(direccion+'kardex.csv', 'rb') as f_in, gzip.open(direccion+'kardex.csv.gz', 'wb') as f_out:
		#	shutil.copyfileobj(f_in, f_out)		

		f = open(direccion+'kardex.csv', 'rb')
			
			
		#sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		#sfs_obj = self.env['repcontab_base.sunat_file_save']
		vals = {
			'output_name': 'kardex.csv',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		mod_obj = self.env['ir.model.data']
		act_obj = self.env['ir.actions.act_window']
		#sfs_id = self.pool.get('export.file.save').create(cr,uid,vals)
		sfs_id = self.env['export.file.save'].create(vals)


		# result = {}
		# view_ref = mod_obj.get_object_reference('account_contable_book_it', 'export_file_save_action')
		# view_id = view_ref and view_ref[1] or False
		# result = act_obj.read([view_id])
		# print sfs_id.id

		

		#import os
		#os.system('c:\\eSpeak2\\command_line\\espeak.exe -ves-f1 -s 170 -p 100 "Se Realizo La exportación exitosamente Y A EDWARD NO LE GUSTA XDXDXDXDDDDDDDDDDDD" ')

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}