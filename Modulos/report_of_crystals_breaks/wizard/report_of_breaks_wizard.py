# -*- encoding: utf-8 -*-

from openerp.osv import osv
import base64,codecs,pprint
from openerp import models, fields, api, exceptions
from datetime import datetime,timedelta
from functools import reduce
from time import time

class report_crystal_breaks_wizard(osv.TransientModel):
	_name='report.crystal.breaks.wizard'

	def _get_start_date(self):
		now = datetime.now().date()
		start_date = now - timedelta(days=30,hours=5)
		return start_date

	start_date = fields.Date(string='Fecha Inicio',default=_get_start_date)
	end_date = fields.Date(string='Fecha Fin',default=fields.Date.today)
	search_param = fields.Selection([('glass_order','Orden de Produccion'),('product','Producto')],string='Busqueda por')
	glass_order_id = fields.Many2one('glass.order','Nro de Orden de Produccion')
	product_id = fields.Many2one('product.product','Nombre de producto')
	customer_id = fields.Many2one('res.partner','Cliente')
	all_items = fields.Boolean('Todos')

	@api.multi
	def do_rebuild(self):
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'reporte_de_pendientes.xlsx')
		worksheet = workbook.add_worksheet("Pendientes")
		#Print Format
		worksheet.set_landscape() #Horizontal
		worksheet.set_paper(9) #A-4
		worksheet.set_margins(left=0.75, right=0.75, top=1, bottom=1)
		worksheet.fit_to_pages(1, 0)  # Ajustar por Columna	
		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_text_wrap()
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)	
		title = workbook.add_format({'bold': True})
		title.set_align('center')
		title.set_align('vcenter')
		title.set_text_wrap()
		title.set_font_size(20)
		worksheet.set_row(0, 30)
		boldborda = workbook.add_format({'bold': True})
		boldborda.set_border(style=2)
		boldborda.set_align('center')
		boldborda.set_align('vcenter')
		boldborda.set_text_wrap()
		boldborda.set_font_size(9)
		boldborda.set_bg_color('#ffff40')

		x= 9 # caminador de iteraciones para cada linea			
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')
		# display values for selection fields:
		search= dict(self._fields['search_param'].selection).get(self.search_param)
		label = ''
		param = ''
		if search == 'Producto' and not self.all_items:
			label = "PRODUCTO:"
			param = self.product_id.name
		elif search == 'Orden de Produccion' and not self.all_items:
			label = "OP:"
			param = self.glass_order_id.name
		worksheet.merge_range(1,1,0,7, u"REPORTE DE PENDIENTES EN PRODUCCION",title)
		worksheet.write(2,1, u"FECHA DEL:",bold)
		worksheet.write(3,1, u"BUSQUEDA:",bold)
		worksheet.write(4,1, label,bold)
		worksheet.write(2,2, str(self.start_date),bold)
		worksheet.write(2,3, u"AL",bold)
		worksheet.write(2,4, str(self.end_date),bold)
		worksheet.write(3,2, search if not self.all_items else 'TODOS',bold)
		worksheet.merge_range(4,2,4,3,param,bold)

		worksheet.merge_range(7,1,8,1, u"ORDEN DE PRODUCCION",boldbord)
		worksheet.merge_range(7,2,8,2, u"LOTES",boldbord)
		worksheet.merge_range(7,3,8,3, u"FECHA PRODUCCION",boldbord)
		worksheet.merge_range(7,4,8,4, u"FECHA DE ENTREGA",boldbord)
		worksheet.merge_range(7,5,8,5, u"NOMBRE CLIENTE",boldbord)
		worksheet.merge_range(7,6,8,6, u"OBRA",boldbord)
		worksheet.merge_range(7,7,8,7, u"COD PRESENTACION",boldbord)
		worksheet.merge_range(7,8,8,8, u"DSCRIPCION DE PRODUCTO",boldbord)
		worksheet.merge_range(7,9,8,9, u"TOTAL M2 SOLICITADOS",boldbord)
		worksheet.merge_range(7,10,8,10, u"TOTAL VIDRIOS SOLICITADOS",boldbord)		
		
		worksheet.merge_range(7,11,7,12, u"PENDIENTE DE OPTIMIZADO",boldbord)
		worksheet.merge_range(7,13,7,14, u"PENDIENTE DE CORTE",boldbord)
		worksheet.merge_range(7,15,7,16, u"PENDIENTE DE PULIDO",boldbord)
		worksheet.merge_range(7,17,7,18, u"PENDIENTE DE ENTALLE",boldbord)
		worksheet.merge_range(7,19,7,20, u"PENDIENTE DE LAVADO",boldbord)
		worksheet.merge_range(7,21,7,22, u"PENDIENTE DE HORNO",boldbord)
		worksheet.merge_range(7,23,7,24, u"PENDIENTE DE ARENADO",boldbord)
		
		for i in range(11,24,2):
			worksheet.write(8,i, u"Area (M2)",boldbord)
			worksheet.write(8,i+1, u"Numero de cristales",boldbord)
		
		#valores_dia= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
		#total_values= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		data = []
		#test = []
		if self.product_id and self.search_param == 'product' and not self.all_items:
			domain = []
			if self.start_date and self.end_date:
				domain = [('date_production','>=',self.start_date),('date_production','<=',self.end_date)]
			orders = self.env['glass.order'].search(domain)
			if self.customer_id:
				orders=orders.filtered(lambda x: x.partner_id.id == self.customer_id.id)
			# for item in range(0,1500):
			# 	test.append(orders[0])

			# print('start...', len(test))
			# start_time = time()
			sale_lines = []
			for order in orders:
				for item in order.sale_lines:
					if item.product_id.id == self.product_id.id:
						sale_lines.append({'sale_line':item,'order':order})
			data = self.get_data(sale_lines)
			
		elif self.glass_order_id and self.search_param == 'glass_order' and not self.all_items:
			if self.start_date and self.end_date:
				start = self._str2date(self.start_date)
				end = self._str2date(self.end_date)
				date_order = self._str2date(self.glass_order_id.date_production)
				if start<=date_order<=end:
					data = self.get_data(self.glass_order_id.sale_lines,self.glass_order_id)
				else:
					raise exceptions.Warning('No se encontraron registros.\nLa fecha de produccion de la OP esta fuera del rango de fechas: '+ self.start_date +' - '+ self.end_date)
			else:
				data = self.get_data(self.glass_order_id.sale_lines,self.glass_order_id)

		elif self.all_items:
			domain = []
			if self.start_date and self.end_date:
				domain = [('date_production','>=',self.start_date),('date_production','<=',self.end_date)]
			orders = self.env['glass.order'].search(domain)
			sale_lines = []
			for order in orders:
				for item in order.sale_lines:
					sale_lines.append({'sale_line':item,'order':order})
			data = self.get_data(sorted(sale_lines, key=lambda x: x['sale_line'].product_id.id))

		for line in data:
			worksheet.write(x,1,line['op'],bord)
			worksheet.write(x,2,line['lot_names'],bord)
			worksheet.write(x,3,line['fec_produccion'].replace('-','/'),bord )
			worksheet.write(x,4,line['fec_entrega'].replace('-','/'),bord)
			worksheet.write(x,5,line['cliente'],bord)
			worksheet.write(x,6,line['obra'],bord)
			worksheet.write(x,7,line['presentacion'],bord)
			worksheet.write(x,8,line['producto'],bord)
			worksheet.write(x,9,line['total_area'],bord)
			worksheet.write(x,10,line['total_vidrios'],bord )
			worksheet.write(x,11,line['area_optimizado'],bord)
			worksheet.write(x,12,line['vidrios_optimizado'],bord)
			worksheet.write(x,13,line['area_corte'],bord)
			worksheet.write(x,14,line['vidrios_corte'],bord)
			worksheet.write(x,15,line['area_pulido'],bord)
			worksheet.write(x,16,line['vidrios_pulido'],bord)
			worksheet.write(x,17,line['area_entalle_real'],bord)
			worksheet.write(x,18,line['vidrios_entalle_real'],bord)
			worksheet.write(x,19,line['area_lavado'],bord)
			worksheet.write(x,20,line['vidrios_lavado'],bord)
			worksheet.write(x,21,line['area_horno'],bord)
			worksheet.write(x,22,line['vidrios_horno'],bord)
			worksheet.write(x,23,line['area_arenado'],bord)
			worksheet.write(x,24,line['vidrios_arenado'],bord)
			x=x+1
		# if fecha_actual != None:
		# 	worksheet.merge_range(x,1,x,8, "Total "+ fecha_actual, bold)
		# 	worksheet.write(x,9,valores_dia[0] if valores_dia[0]  else 0,numberdos)
		# 	worksheet.write(x,10,valores_dia[1] if valores_dia[1]  else 0,numberdos)
		# 	worksheet.write(x,11,valores_dia[2] if valores_dia[2]  else 0,numberdos)
		# 	worksheet.write(x,12,valores_dia[3] if valores_dia[3]  else 0,numberdos)
		# 	x=x+1


		# worksheet.merge_range(x,1,x,8, "Total General", bold)
		# worksheet.write(x,9,valores_total[0] if valores_total[0]  else 0,numberdos)
		# worksheet.write(x,10,valores_total[1] if valores_total[1]  else 0,numberdos)
		# worksheet.write(x,11,valores_total[2] if valores_total[2]  else 0,numberdos)
		# worksheet.write(x,12,valores_total[3] if valores_total[3]  else 0,numberdos)
		
		tam_col = [13,10,10,12,12,24,20,12,30,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12]

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
		worksheet.set_column('T:T', tam_col[19])
		worksheet.set_column('V:V', tam_col[20])
		worksheet.set_column('W:W', tam_col[21])
		worksheet.set_column('X:X', tam_col[22])
		worksheet.set_column('Y:Y', tam_col[23])
		worksheet.set_column('Z:Z', tam_col[24])
		workbook.close()
		#elapsset = time() - start_time
		
		#print('finish: ',elapsset)
		f = open(direccion + 'reporte_de_pendientes.xlsx', 'rb')
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'reporte_de_pendientes.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
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
	def get_data(self,sale_lines,order_param=None):
		results = []
		for item in sale_lines:
			order = order_param if order_param else item['order']
			item = item['sale_line'] if order_param == None else item
			area_optimizado,vidrios_optimizado = 0,0
			area_corte,vidrios_corte = 0,0
			area_entalle_real,vidrios_entalle_real = 0,0
			area_lavado,vidrios_lavado = 0,0
			area_horno,vidrios_horno = 0,0
			area_pulido,vidrios_pulido = 0,0
			area_arenado,vidrios_arenado = 0,0
			aux = ''
			order_lines = self.env['glass.order.line'].search([('calc_line_id','in',item.id_type_line.ids),('canceled','=',False)])

			without_lot = order_lines.filtered(lambda x: not x.lot_line_id)
			if len(without_lot) > 0:
				area = reduce(lambda x,y: x+y,without_lot.mapped('area'))
				size = len(without_lot)
				area_optimizado += area
				vidrios_optimizado += size
				area_corte += area
				vidrios_corte  += size
				area_lavado += area
				vidrios_lavado  += size
				area_horno += area
				vidrios_horno  += size
				entalle_required = without_lot.filtered(lambda x: x.entalle > 0)
				pulido_required = without_lot.filtered(lambda x: x.pulido1)
				
				if len(entalle_required) > 0:
					area_entalle_real += reduce(lambda x,y: x+y,entalle_required.mapped('area'))
					vidrios_entalle_real += len(entalle_required)
				if len(pulido_required) > 0:
					area_pulido += reduce(lambda x,y: x+y,pulido_required.mapped('area'))
					vidrios_pulido += len(pulido_required)

			atributo = list(filter(lambda x: x.atributo_id.id==4,item.product_id.product_tmpl_id.atributo_ids))
			if len(atributo) == 0:
				atributo = 'not found'
			else:
				atributo = atributo[0].valor_id.name
			total_vidrios = map(lambda n:n.cantidad,item.id_type_line)
			if len(total_vidrios) > 0:
				total_vidrios=reduce(lambda x,y:x+y,map(lambda n:n.cantidad,item.id_type_line))
			else:
				total_vidrios = 0

			vals = {
				'cliente':item.order_id.partner_id.name,
				'presentacion': atributo,
				'producto': item.product_id.name,
				'total_area': item.product_uom_qty,
				'total_vidrios':total_vidrios,
				'area_arenado':'-', # pendiente de gestion
				'vidrios_arenado':'-', # pendiente de gestion
			}
			if len(without_lot) < len(order_lines):
				lot_lines = order_lines.filtered(lambda x: x.lot_line_id).mapped('lot_line_id')
				## empezamos a sacar totales optimizado
				filtered = filter(lambda x: not x.optimizado,lot_lines)
				if len(filtered) > 0:
					area_optimizado+=reduce(lambda z,r:z+r,map(lambda y:y.area,filtered))
					vidrios_optimizado+=len(filtered)
				## empezamos a sacar totales corte
				filtered = filter(lambda x: not x.corte,lot_lines)
				if len(filtered) > 0:
					area_corte+=reduce(lambda z,r:z+r,map(lambda y:y.area,filtered))
					vidrios_corte+=len(filtered)
				## empezamos a sacar totales entalle real
				filtered = filter(lambda x: not x.entalle and x.order_line_id.entalle > 0,lot_lines)
				if len(filtered) > 0:
					area_entalle_real+=reduce(lambda z,r:z+r,map(lambda y:y.area,filtered))
					vidrios_entalle_real+=len(filtered)
				## empezamos a sacar totales lavado
				filtered = filter(lambda x: not x.lavado,lot_lines)
				if len(filtered) > 0:
					area_lavado+=reduce(lambda z,r:z+r,map(lambda y:y.area,filtered))
					vidrios_lavado+=len(filtered)
				## empezamos a sacar totales horno
				filtered = filter(lambda x: not x.horno,lot_lines)
				if len(filtered) > 0:
					area_horno+=reduce(lambda z,r:z+r,map(lambda y:y.area,filtered))
					vidrios_horno+=len(filtered)

				## empezamos a sacar totales pulido
				filtered = filter(lambda x: not x.pulido and x.order_line_id.pulido1,lot_lines)
				if len(filtered) > 0:
					area_pulido+=reduce(lambda z,r:z+r,map(lambda y:y.area,filtered))
					vidrios_pulido+=len(filtered)
				lot_names = set(map(lambda x: x.lot_id.name ,lot_lines))
				for i in lot_names:
					aux += 'L-'+str(i)+' '
			vals['op'] = order.name
			vals['lot_names'] = aux
			vals['fec_produccion'] = order.date_production
			vals['fec_entrega'] = order.date_delivery
			vals['obra'] = order.obra if order.obra else ''
			vals['area_optimizado'] = area_optimizado
			vals['vidrios_optimizado'] = vidrios_optimizado
			vals['area_corte'] = area_corte
			vals['vidrios_corte'] = vidrios_corte
			vals['area_entalle_real'] = area_entalle_real
			vals['vidrios_entalle_real'] = vidrios_entalle_real
			vals['area_lavado'] = area_lavado
			vals['vidrios_lavado'] = vidrios_lavado
			vals['area_pulido']=area_pulido
			vals['vidrios_pulido']=vidrios_pulido
			vals['area_horno']=area_horno
			vals['vidrios_horno']=vidrios_horno
			results.append(vals)

		return results

	def _str2date(self,string):
		return datetime.strptime(string.replace('-',''),"%Y%m%d").date()


	