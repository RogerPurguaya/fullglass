# -*- encoding: utf-8 -*-

from openerp.osv import osv
import base64,codecs,pprint
from openerp import models, fields, api
from datetime import datetime,timedelta
from functools import reduce

class ReportRequisitionsOrdersWizard(osv.TransientModel):
	_name='report.requisition.orders.wizard'

	search_param = fields.Selection([('requisition','Orden de Requisicion'),('dates','Fechas')],string='Paramatro de busqueda')
	start_date = fields.Date(string='Fecha Inicio',default=fields.Date.today)
	end_date = fields.Date(string='Fecha Fin',default=fields.Date.today)
	requisition = fields.Many2one('glass.requisition',string='Order de Requisicion')

	@api.model_cr
	def init(self):
		self.env.cr.execute(""" 
			drop view if exists vst_rq_drt;
			create or replace view vst_rq_drt as (
			select gr.id as requisition_id,sm.product_id,sum(
				round(sm.product_uom_qty*(1/pu.factor),4)) as rt_m2
			from glass_requisition gr
			join glass_requisition_picking_drt_rel mpr on gr.id = mpr.requisition_id
			join stock_picking sp on mpr.picking_id = sp.id
			join stock_move sm on sp.id = sm.picking_id
			join product_uom pu on sm.product_uom = pu.id
			join product_product pp on sm.product_id = pp.id
			join product_template pt on pp.product_tmpl_id = pt.id
			where sp.state ='done'
			group by 1,2
			);

			drop view if exists vst_rq_rt;
			create or replace view vst_rq_rt as (
			select gr.id as requisition_id,sm.product_id,sum(
			round(sm.product_uom_qty*(1/pu.factor),4)) as rt_m2
			from glass_requisition gr
			join glass_requisition_picking_rt_rel mpr on gr.id = mpr.requisition_id
			join stock_picking sp on mpr.picking_id = sp.id
			join stock_move sm on sp.id = sm.picking_id
			join product_uom pu on sm.product_uom = pu.id
			join product_product pp on sm.product_id = pp.id
			join product_template pt on pp.product_tmpl_id = pt.id
			where sp.state ='done'
			group by 1,2
			);

			drop view if exists vst_rq_corte;
			create or replace view vst_rq_corte as (
			select gr.id as requisition_id,gr.date_order as fecha,sum(gll.area) as corte
			from glass_requisition gr
			join glass_requisition_line_lot grll on gr.id = grll.requisition_id
			join glass_lot_line gll on grll.lot_id = gll.lot_id
			group by 1,2
			);

			drop view if exists vst_rq_mp;
			create or replace view vst_rq_mp as (
			select gr.id as requisition_id,sm.product_id,pt.name as prod,pu.name as present,puk.name as umed,
			round(sm.product_uom_qty*(1/pu.factor),4) as mp_m2,
			pp.default_code as codigo
			from glass_requisition gr
			join glass_requisition_picking_mp_rel mpr on gr.id = mpr.requisition_id
			join stock_picking sp on mpr.picking_id = sp.id
			join stock_move sm on sp.id = sm.picking_id
			join product_uom pu on sm.product_uom = pu.id
			join product_product pp on sm.product_id = pp.id
			join product_template pt on pp.product_tmpl_id = pt.id
			left join product_uom puk on pt.unidad_kardex = puk.id
			where sp.state ='done'
			);

			""")

	@api.multi
	def do_rebuild(self):
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'reporte_ordenes_de_requisicion.xlsx')
		worksheet = workbook.add_worksheet("Seguimiento de Produccion")
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
		numberfour = workbook.add_format({'num_format':'0.0000'})
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_text_wrap()
		numberdos.set_border(style=1)
		numberfour.set_border(style=1)
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

		worksheet.merge_range(1,2,0,6, u"Reporte Ordenes de Requisicion",title)
		worksheet.write(2,1, u"FECHA INICIO:",bold)
		worksheet.write(2,2, str(self.start_date),bold)
		worksheet.write(3,1 , u"FECHA FIN",bold)
		worksheet.write(3,2, str(self.end_date),bold)
		
		worksheet.write(7,1, u"CODIGO",boldbord)
		worksheet.write(7,2, u"PRODUCTO",boldbord)
		worksheet.write(7,3, u"MEDIDA",boldbord)
		worksheet.write(7,4, u"UNIDAD MED. KARDEX",boldbord)
		worksheet.write(7,5, u"MATERIA PRIMA",boldbord)
		worksheet.write(7,6, u"CORTE",boldbord)
		worksheet.write(7,7, u"DEVUELTOS",boldbord)
		worksheet.write(7,8, u"DESPERDICIO",boldbord)
		worksheet.write(7,9, u"CONSUMO",boldbord)		
		# worksheet.write(7,10, u"TOTAL M2 SOLICITADOS CON ENTALLE",boldbord)
		# worksheet.write(7,11, u"TOTAL VIDRIOS CON ENTALLE",boldbord)
		
		valores_dia= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
		valores_total= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]

		condition = ' WHERE '
		if self.requisition and self.search_param=='requisition':
			condition += " co.requisition_id ='"+str(self.requisition.id)+"'"
		elif self.start_date and self.end_date and self.search_param=='dates':
			condition += " co.fecha >= '"+self.start_date+"' and co.fecha <= '"+self.end_date+"'"
		print('cond: ', condition)
		self.env.cr.execute("""		
		select co.requisition_id,
		mp.codigo as codigo,
		mp.prod as producto,
		mp.present as presentacion,
		mp.umed unidad_kardex,
		mp.mp_m2+rt.rt_m2 as mp_m2,
		co.corte as corte,
		drt.rt_m2 as dev_m2,
		(mp.mp_m2+rt.rt_m2)-co.corte-drt.rt_m2 as desper,
		(mp.mp_m2+rt.rt_m2)-drt.rt_m2 as consum
		from vst_rq_corte co
		join vst_rq_mp mp on co.requisition_id = mp.requisition_id
		join vst_rq_rt rt on mp.requisition_id = rt.requisition_id and mp.product_id = rt.product_id
		join vst_rq_drt drt on mp.requisition_id = drt.requisition_id and mp.product_id = drt.product_id
		"""+condition+""" 
		""")

		results = self.env.cr.dictfetchall()

		print('res: ', results)

		for line in results:
			#cont = 0
			worksheet.write(x,1,line['codigo'] if line['codigo'] else '',bord)
			worksheet.write(x,2,line['producto'] if line['producto'] else '',bord)
			worksheet.write(x,3,line['presentacion'] if line['presentacion'] else '',bord)
			worksheet.write(x,4,line['unidad_kardex'] if line['unidad_kardex'] else '',bord)

			mp_m2 = line['mp_m2'] if line['mp_m2'] else 0
			worksheet.write(x,5,mp_m2,bord)
			valores_total[0] += mp_m2

			corte = line['corte'] if line['corte'] else 0
			worksheet.write(x,6,corte,bord)
			valores_total[1] += corte

			dev_m2 = line['dev_m2'] if line['dev_m2'] else 0
			worksheet.write(x,7,dev_m2,bord)
			valores_total[2] += dev_m2

			desper = line['desper'] if line['desper'] else 0
			worksheet.write(x,8,desper,bord)
			valores_total[3] += desper

			consum = line['consum'] if line['consum'] else 0
			worksheet.write(x,9,consum,bord)
			valores_total[4] += consum

			x=x+1
		# if fecha_actual != None:
		# 	worksheet.merge_range(x,1,x,8, "Total "+ fecha_actual, bold)
		# 	worksheet.write(x,9,valores_dia[0] if valores_dia[0]  else 0,numberdos)
		# 	worksheet.write(x,10,valores_dia[1] if valores_dia[1]  else 0,numberdos)
		# 	worksheet.write(x,11,valores_dia[2] if valores_dia[2]  else 0,numberdos)
		# 	worksheet.write(x,12,valores_dia[3] if valores_dia[3]  else 0,numberdos)
		# 	x=x+1

		worksheet.merge_range(x,1,x,4, "Total General", bold)
		worksheet.write(x,5,valores_total[0] if valores_total[0]  else 0,numberfour)
		worksheet.write(x,6,valores_total[1] if valores_total[1]  else 0,numberfour)
		worksheet.write(x,7,valores_total[2] if valores_total[2]  else 0,numberfour)
		worksheet.write(x,8,valores_total[3] if valores_total[3]  else 0,numberfour)
		worksheet.write(x,9,valores_total[4] if valores_total[4]  else 0,numberfour)
		
		tam_col = [13,18,35,18,12,12,12,12,12,12,12,12,12]

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
		worksheet.set_column('L:L', tam_col[10])
		worksheet.set_column('M:M', tam_col[10])
		worksheet.set_column('N:N', tam_col[10])
		workbook.close()
		
		f = open(direccion + 'reporte_ordenes_de_requisicion.xlsx', 'rb')
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'reporte_ordenes_de_requisicion.xlsx',
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