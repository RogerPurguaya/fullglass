# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
import base64
import codecs
import os

class GlassPoolWizard(models.TransientModel):
	_name='glass.pool.wizard'

	line_order_ids=fields.Many2many('glass.order.line','glass_lines_wizard_rel','wizard_id','line_order_id')
	prod_resu_id = fields.One2many('glass.pool.wizard.line','wizard_id')
 	prod_detail_id = fields.One2many('glass.pool.wizard.line.detail','wizard_id')
	prod_detail_id_m = fields.Many2many('glass.pool.wizard.line.detail','glass_wizard_rel','wizard_id','detail_id')
	nextlotnumber = fields.Char('Lote')
	product_id = fields.Integer('productoid')
	qty_lines = fields.Integer('Cantidad',compute="getarealines")
	area_lines = fields.Float(u'Área M2',compute="getqtyarea",digits=(20,4))
	user_id=fields.Many2one('res.users','Responsable')




	@api.one
	def make_requisition(self):
		lines=[]
		umed = False
		for line in self.prod_resu_id:
			if line.selected:
				umed = line.uom_id.id
		orderact = False
		for line in self.line_order_ids:
			if orderact:
				if line.order_id.id !=orderact.id:
					raise UserError(u'Solo se admiten elementos de la misma orden de producción')
			else:
				orderact=line.order_id
			vals = {
				'product_id':line.product_id.id,
				'product_uom_id':umed,
				'product_qty':line.area,
				'description':"""Altura1: """+str(line.altura1)+
					""" Altura2: """+str(line.altura2)+
					""" Base1: """+str(line.base1)+
					""" Base2: """+str(line.base2)
			}
			lines.append((0,0,vals))
			line.is_used = True
			data = {
					'user_id':self.env.uid,
					'date':datetime.now(),
					'time':datetime.now().time(),
					'stage':'compra',
					'lot_line_id':line.lot_line_id.id,
					
				}
			stage_obj = self.env['glass.stage.record']
			stage_obj.create(data)
		compra = self.env['purchase.requisition'].create({
			'line_ids':lines,
			'sketch':orderact.sketch,
			'file_name':orderact.file_name,
			})

		return True
	
	@api.onchange('line_order_ids')
	def onchange_lines(self):
		areat=0.00
		for line in self.line_order_ids:
			areat=areat+line.area
		self.area_lines = areat
		self.qty_lines=len(self.line_order_ids)



		catidadsel = 0
		areasel = 0
		for line in self.line_order_ids:
			catidadsel=catidadsel+1
			areasel=areasel+line.area
		for line in self.prod_resu_id:
			if line.selected:
				line.cant_rest=line.qty-catidadsel
				line.area_rest=line.area-areasel



	@api.one
	def getqtyarea(self):
		areat=float(0.00)
		for line in self.line_order_ids:
			areat=areat+float(line.area)


		self.area_lines = areat

	@api.one
	def getarealines(self):
		self.qty_lines=len(self.line_order_ids)

	@api.multi
	def addlot(self):
		if len(self.line_order_ids)==0:
			return
		product_valid =False
		linesel = False
		for line in self.prod_resu_id:
			if line.selected:
				linesel=line
		if not linesel:
			return
		config_data = self.env['glass.order.config'].search([])[0]
		newname = config_data.seq_lot.next_by_id()
		
		vals = {
			'name':newname,
			'date':datetime.now(),
			'product_id':linesel.product_id.id,
			'state':'done',
			'user_id':self.user_id.id,
		}

		newlot = self.env['glass.lot'].create(vals)

		cad_optima = ""
		cad_optima =cad_optima +("Lote"+newlot.name.rjust(7,'0')).ljust(32,' ')
		fecha_s=str(newlot.date[8:10]).ljust(2,'0')+str(newlot.date[5:7]).ljust(2,'0')+str(newlot.date[:4])

		cad_optima =cad_optima +fecha_s
		cad_optima =cad_optima +''.ljust(8,' ')
		cad_optima =cad_optima +str(self.qty_lines).rjust(8,'0')
		cad_optima =cad_optima +'V7'+'\r\n'
		cad_optima =cad_optima +str(self.qty_lines).rjust(8,'0')+'\r\n'
		
		n=1
		for line in self.line_order_ids:
			if product_valid:
				if product_valid.id !=line.product_id.id:
					raise UserError('Solo se admiten elementos con el producto: '+line.product_id.name)
			search_code = str(int(line.order_id.name)).rjust(5,'0')
			search_code =search_code +str(line.crystal_number).rjust(4,'0')
			search_code =search_code +str(int(newname)).rjust(6,'0')
			vals = {
				'product_id':line.product_id.id,
				'nro_cristal':line.crystal_number,
				'base1':line.base1,
				'base2':line.base2,
				'altura1':line.altura1,
				'altura2':line.altura2,
				'descuadre':line.descuadre,
				'page_number':line.page_number,
				'lot_id':newlot.id,
				'order_line_id':line.id,
				'search_code':search_code,
				'calc_line_id':line.calc_line_id.id,
				'area':line.area,
			}
			newid = self.env['glass.lot.line'].create(vals) 
			line.is_used=True
			line.lot_line_id=newid.id
			line.order_id.state="process"
			product_valid=line.product_id

			data = {
					'user_id':self.env.uid,
					'date':datetime.now(),
					'time':datetime.now().time(),
					'stage':'optimizado',
					'lot_line_id':newid.id,
					
				}
			stage_obj = self.env['glass.stage.record']
			stage_obj.create(data)
			newid.optimizado=True
			line.order_id.state="process"



			
			desc='        '
			molval='000003.0'
			caddes=''
			data_desc = False # String con los datos de descuadre para optima
			if line.descuadre:
				desc='########'
				molval='000000.0'
				adesc=line.descuadre.split(',')
				caddes = caddes+'/'

				if adesc[0]=='1':
					caddes = caddes+str(line.base1)
				if adesc[0]=='2':
					caddes = caddes+str(line.base2)
				if adesc[0]=='3':
					caddes = caddes+str(line.altura1)
				if adesc[0]=='4':
					caddes = caddes+str(line.altura2)
				if len(adesc)>1: 
					if adesc[1]=='1':
						caddes = caddes+'x'+str(line.base1)
					if adesc[1]=='2':
						caddes = caddes+'x'+str(line.base2)
					if adesc[1]=='3':
						caddes = caddes+'x'+str(line.altura1)
					if adesc[1]=='4':
						caddes = caddes+'x'+str(line.altura2)
					data_desc = self.get_descuadre_2_3(line.order_id.name,line.product_id.product_tmpl_id.optima_trim,line.crystal_number,adesc,line.base1,line.base2,line.altura1,line.altura2)
				elif len(adesc) == 1:
					data_desc = self.get_descuadre_1(line.order_id.name,line.product_id.product_tmpl_id.optima_trim,line.crystal_number,adesc[0],line.base1,line.base2,line.altura1,line.altura2)

			x=line.base1
			if line.base2>x:
				x=line.base2
			ax = str(x).split('.')
			cadx=ax[0].rjust(4,'0')
			if len(ax)>1:
				cadx=cadx+'.'+ax[1].ljust(3,'0')
			else:
				cadx=cadx+'.000'

			y=line.altura1
			if line.altura2>y:
				y=line.altura2
			ay = str(y).split('.')
			cady=ay[0].rjust(4,'0')
			if len(ay)>1:
				cady=cady+'.'+ay[1].ljust(3,'0')
			else:
				cady=cady+'.000'
			cade1=''.rjust(32,' ')
			cade = '      '
			if line.entalle:
				cade='E     '
				cade1='E'.ljust(32,' ')

			#medidas
			cmedida=""
			if desc=='########':
				if line.base1!=line.base2:
					cmedida=cmedida+str(line.base1)+'/'+str(line.base2)
				else:
					cmedida=cmedida+str(line.base1)
				cmedida=cmedida+"x"
				if line.altura1!=line.altura2:
					cmedida=cmedida+str(line.altura1)+'/'+str(line.altura2)
				else:
					cmedida=cmedida+str(line.altura1)
			else:
				cmedida=str(line.base1)+"x"+str(line.altura1)

			fecha_prod_a=self.line_order_ids[0].order_id.date_production

			fecha_prod=(str(fecha_prod_a[:4]+'.'+str(fecha_prod_a[5:7])+'.'+fecha_prod_a[8:10])).ljust(32,' ')

			cad_optima =cad_optima+(line.product_id.type_materia_prod.ljust(64,' ') if line.product_id.type_materia_prod else ''.ljust(64,' ')) #codmaterial
			cad_optima =cad_optima+str(n).rjust(5,'0') # numpos
			cad_optima =cad_optima+line.partner_id.name[:12] #partner cliente
			cad_optima =cad_optima+line.order_id.name.ljust(12,' ') #ORDEN
			cad_optima =cad_optima+desc #si tine descuadre
			cad_optima =cad_optima+'    ' #extension
			cad_optima =cad_optima+molval #moliendavalor
			cad_optima =cad_optima+'000' #prioridadd de pezxas
			cad_optima =cad_optima+'Y' #si se rorta
			cad_optima =cad_optima+'00000001' # numero de corte
			cad_optima =cad_optima+'000000.0' # maquinadoblado
			cad_optima =cad_optima+cadx # tamaño x
			cad_optima =cad_optima+cady # tamaño y
			cad_optima =cad_optima+'        ' # espaciador
			cad_optima =cad_optima+(str(line.crystal_number)+'.0').ljust(32,' ') #notas adicionales
			cad_optima =cad_optima+''.ljust(5,'0') # nro etiuqetas
			cad_optima =cad_optima+''.ljust(5,'0') # piezas
			cad_optima =cad_optima+''.ljust(5,'0') # preferencia

			cad_optima =cad_optima+cade # entalle
			cad_optima =cad_optima+'        '# fenetrega
			cad_optima =cad_optima+'000' #cod hoyo
			cad_optima =cad_optima+'000000.0' #distancia borde cristal
			cad_optima =cad_optima+(str(line.crystal_number)+".0").ljust(32,' ') # texto add 1
			# aqui me voy a ver lo de qr de la alemana conuar desde aqui
			cad_optima =cad_optima+search_code.ljust(32,' ') # texto add 2
			cad_optima =cad_optima+line.product_id.name[:32].ljust(32,' ') # text add 3
			cad_optima =cad_optima+line.partner_id.name[:32].ljust(32,' ') # change: nombre completo del cliente recortado a 32 chars
			cad_optima =cad_optima+''.rjust(32,' ') # t a 5

			cad_optima =cad_optima+(line.pulido1.code.strip().ljust(32,' ') if line.pulido1.code else ''.ljust(32,' '))
			cad_optima =cad_optima+cade1
			cad_optima =cad_optima+''.ljust(32,' ') # t a 8
			cad_optima =cad_optima+''.ljust(32,' ') # t a 9
			cad_optima =cad_optima+''.ljust(32,' ') # t a 10
			cad_optima =cad_optima+''.ljust(8,' ') # second spavccer
			cad_optima =cad_optima+'000000.0'
			cad_optima =cad_optima+'000000.0'
			cad_optima =cad_optima+'000000.0'
			cad_optima =cad_optima+'000000.0'
			cad_optima =cad_optima+cmedida.ljust(32,' ')# medidas 
			cad_optima =cad_optima+''.ljust(32,' ') # roto?
			cad_optima =cad_optima+('D'.ljust(32,' ') if desc=='########' else ''.ljust(32,' ')) # descuadre?
			cad_optima =cad_optima+line.product_id.name[32:64].ljust(32,' ') # resto del nombre producto
			arenado = 'Arenado' if line.calc_line_id.arenado else ''
			cad_optima =cad_optima+arenado.ljust(32,' ') #

			cad_optima =cad_optima+fecha_prod+'\r\n'
			if data_desc:
				cad_optima =cad_optima+data_desc+'\r\n'
			n=n+1

		newlot.optimafile=base64.b64encode(cad_optima)
		if not config_data.optimization_path:
			raise UserError('No se ha configurado la ruta para los archivos de OPTIMA')
		if not config_data.optimization_ext:
			raise UserError('No se ha configurado la ruta para los archivos de OPTIMA')
		newname = newname.rjust(7,'0')
		filename=config_data.optimization_path+newname+"."+config_data.optimization_ext
		f=open(filename,"w+")
		cad_optima = cad_optima.replace('\r','')
		f.write(cad_optima)
		f.close()
		data={}
		form_view_ref = self.env.ref('glass_production_order.view_glass_lot_form', False)
		# tree_view_ref = self.env.ref('account.invoice_tree', False)

		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_lot_form' % module)
		data = {
			'name': _('Pool de pedidos'),
			'context': self._context,
			'view_type': 'tree,form',
			'view_mode': 'form',
			'res_model': 'glass.lot',
			'view_id': view.id,
			'res_id':newlot.id,
			'type': 'ir.actions.act_window',
		} 
		return data


	# Método para optener la data para los cristales con un descuadre:
	@api.multi
	def get_descuadre_1(self,op,trim,crystal,position,base1,base2,altura1,altura2):
		data = '060 3\r\n'
		base1,base2,altura1,altura2 = str(base1),str(base2),str(altura1),str(altura2)
		if position == '1':
			if base1 < base2:
				data+='W '+altura2+'\r\n'+'H '+base2+'\r\n'+'H1 '+base1+'\r\n'+'ELAB: OFF 1.50 ROT 90 MY 1'+'\r\n'
			else:
				data+='W '+altura2+'\r\n'+'H '+base1+'\r\n'+'H1 '+base2+'\r\n'+'ELAB: OFF 1.50 ROT 90'+'\r\n'
		elif position == '2':
			if altura2 > altura1:
				data+='W '+base1+'\r\n'+'H '+altura2+'\r\n'+'H1 '+altura1+'\r\n'+'ELAB: OFF 1.50 MY 1'+'\r\n'
			else:
				data+='W '+base1+'\r\n'+'H '+altura1+'\r\n'+'H1 '+altura2+'\r\n'+'ELAB: OFF 1.50'+'\r\n'
		elif position == '3':
			if base2 < base1:
				data+='W '+altura1+'\r\n'+'H '+base1+'\r\n'+'H1 '+base2+'\r\n'+'ELAB: OFF 1.50 ROT 270 MY 1'+'\r\n'
			else:
				data+='W '+altura1+'\r\n'+'H '+altura2+'\r\n'+'H1 '+altura1+'\r\n'+'ELAB: OFF 1.50 ROT 270'+'\r\n'
		elif position == '4':
			if altura2 > altura1:
				data+='W '+base2+'\r\n'+'H '+altura2+'\r\n'+'H1 '+altura1+'\r\n'+'ELAB: OFF 1.50 ROT MX 1 MY 1'+'\r\n'
			else:
				data+='W '+base2+'\r\n'+'H '+altura1+'\r\n'+'H1 '+altura2+'\r\n'+'ELAB: OFF 1.50 MX 1'+'\r\n'
		
		return data + str(op)+ '.0_' +str(crystal)+ '.0 0 0 '+str(trim)+' 0'


	# Metodo para optener la data para los cristales con un descuadre de 2 o 3, esta 
	# funcionalidad no esta 100% correcta ya que requieren
	# un trabajo mas especializado para generar el archivo adecuado.
	@api.multi
	def get_descuadre_2_3(self,op,trim,crystal,positions,base1,base2,altura1,altura2):
		data = ''
		#lado4,lado2,lado1,lado3 = str(base1),str(base2),str(altura1),str(altura2)
		W,W1,H,H1 = str(base1),str(base2),str(altura1),str(altura2)

		if positions == ['2','3']:
			condition = H > H1 and W1 > 0 and H1 > 0
			if W > W1 and condition:
				data+='071 4\r\n'+'W '+W+'\r\n'+'W1 '+W1+'\r\n'+'H '+H+'\r\n'+'H1 '+H1+'\r\n'+'ELAB: OFF 1.50'+'\r\n'
			if W < W1 and condition:
				data+='070 4\r\n'+'W '+W+'\r\n'+'W1 '+W1+'\r\n'+'H '+H+'\r\n'+'H1 '+H1+'\r\n'+'ELAB: OFF 1.50'+'\r\n'
		elif positions == ['1','2']:
			tmp = W
			W = W1
			W1 = tmp
			if W > W1 and H > H1 and W1 > 0 and H1 > 0:
				data+='073 4\r\n'+'W '+W+'\r\n'+'W1 '+W1+'\r\n'+'H '+H+'\r\n'+'H1 '+H1+'\r\n'+'ELAB: OFF 1.50'+'\r\n'
		if positions == ['1','2','3']:
			compl = 'W '+W+'\r\n'+'W2 '+W1+'\r\n'+'H '+H+'\r\n'+'H1 '+H1+'\r\n'+'ELAB: OFF 1.50'+'\r\n'
			if W1 < H1 and H1 > H:
				data+='075 4\r\n'+ compl
			if W1 > H and W1 > H1 and H > H1:
				data+='078 4\r\n'+ compl
			if H > W1 and H > H1 and W1 > H1:
				data+='079 4\r\n'+ compl
		
		return data + str(op)+ '.0_' +str(crystal)+ '.0 0 0 '+str(trim)+' 0'
		
	@api.onchange('prod_resu_id','product_id')
	def onchagelineprod(self):
		ntot=0
		linesel = False
		for line in self.prod_resu_id:
			#print line
			if line.selected:
				ntot = ntot +1
				linesel=line
		if ntot>1:
			raise UserError('Solo se admite un producto seleccionado')
		else:
			if linesel:
				domain ={
					'line_order_ids':[('product_id','=',linesel.product_id.id),('is_used','=',False)]
				}
				return {'domain':domain}

				

		

	@api.model
	def default_get(self, fields):
		lst = []
		res = super(GlassPoolWizard,self).default_get(fields)
		
		cadsql ="""select 
			sum(case when sale_calculadora_proforma_line.base1>sale_calculadora_proforma_line.base2 then
				case when sale_calculadora_proforma_line.altura1>sale_calculadora_proforma_line.altura2 then
					sale_calculadora_proforma_line.base1*sale_calculadora_proforma_line.altura1
				else
					sale_calculadora_proforma_line.base1*sale_calculadora_proforma_line.altura2
				end
			else
				case when sale_calculadora_proforma_line.altura1>sale_calculadora_proforma_line.altura2 then
					sale_calculadora_proforma_line.base2*sale_calculadora_proforma_line.altura1
				else
					sale_calculadora_proforma_line.base2*sale_calculadora_proforma_line.altura2
				end
			end)/1000000::float as area, 
			count(glass_order_line.*) as qty,
			glass_order_line.product_id,
			product_product.default_code,
			product_template.uom_id
			from glass_order_line 
			inner join glass_order on glass_order_line.order_id = glass_order.id
			inner join product_product on glass_order_line.product_id = product_product.id
			inner join product_template on product_product.product_tmpl_id= product_template.id
			inner join sale_calculadora_proforma_line on glass_order_line.calc_line_id = sale_calculadora_proforma_line.id
			where glass_order_line.state != 'delivered' 
				and (glass_order_line.is_used=false or glass_order_line.is_used is null)
			group by glass_order_line.product_id,
			product_product.default_code,
			product_template.uom_id"""
		data_sql = self.env.cr.execute(cadsql)
		filldata = self.env.cr.dictfetchall()
		for line in filldata:
			lst.append((0,0,{
				'product_id':line['product_id'],
				'area':line['area'] if line['area'] else 0.0,
				'qty':line['qty'],
				'uom_id':line['uom_id'],
				'default_code':line['default_code'],
				}))

		lst2=[]


		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]
		res.update( {
			'nextlotnumber':config_data.seq_lot.number_next_actual,
			'prod_resu_id':lst,
			'user_id':self.env.uid,
			# 'order_id':self._context['active_id']
		})
		return res


	@api.multi
	def showdetail(self):
		for line in self.prod_detail_id:
			line.unlink()
		prods=""
		for line in self.prod_resu_id:
			if line.selected==True:
				prods=prods+str(line.product_id.id)+","
		prods="("+prods[:-1]+")"

		cadsql="""select 
			glass_order.name,
			glass_order.date_production,
			glass_order_line.calc_line_id,
			glass_order_line.crystal_number,
			sale_calculadora_proforma_line.base1,
			sale_calculadora_proforma_line.base2,
			sale_calculadora_proforma_line.altura1,
			sale_calculadora_proforma_line.altura2,
			sale_calculadora_proforma_line.descuadre,
			sale_calculadora_proforma_line.page_number,
			glass_order_line.id,
			glass_order.obra,
			glass_order_line.product_id,
			product_product.id as product_id,
			product_product.default_code,
			glass_order.id as order_id
			from glass_order
			inner join glass_order_line on glass_order.id =glass_order_line.order_id
			inner join product_product on glass_order_line.product_id = product_product.id
			inner join product_template on product_product.product_tmpl_id= product_template.id
			inner join sale_calculadora_proforma_line on glass_order_line.calc_line_id = sale_calculadora_proforma_line.id
			where glass_order_line.state != 'delivered' 
				and (glass_order_line.is_used=false or glass_order_line.is_used is null)
				and glass_order_line.product_id in """+prods


		data_sql = self.env.cr.execute(cadsql)
		filldata = self.env.cr.dictfetchall()
		for line in filldata:


			vals={
				'order_line_id':line['id'],
				'default_code':line['default_code'],
				'product_id':line['product_id'],
				'crystal_number':line['crystal_number'],
				'base1':line['base1'],
				'base2':line['base2'],
				'altura1':line['altura1'],
				'altura2':line['altura2'],
				'descuadre':line['descuadre'],
				'page_number':line['page_number'],
				'wizard_id':self.id,
				'production_id':line['order_id'],
				# 'partner_id':line['page_number'],
				# 'date_production':line['page_number'],
				'obra':line['obra'],
				}
			self.env['glass.pool.wizard.line.detail'].create(vals)


		form_view_ref = self.env.ref('glass_production_order.view_glass_pool_wizard_form', False)
		# tree_view_ref = self.env.ref('account.invoice_tree', False)
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_pool_wizard_form' % module)
		data = {
			'name': _('Pool de pedidos'),
			'context': self._context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.pool.wizard',
			'view_id': view.id,
			'res_id':self.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 
		return data







class GlassPoolWizardLine(models.TransientModel):
	_name='glass.pool.wizard.line'

	order_line_id = fields.Many2one('glass.order.line')
	default_code = fields.Char(u'Código')
	product_id = fields.Many2one('product.product','Producto')
	uom_id = fields.Many2one('product.uom',string='Unidad de Medida')
	qty = fields.Float('Cantidad')
	area = fields.Float('M2',digits=(20,4))
	selected = fields.Boolean('Ver')
	area_rest = fields.Float(u'Área Restante M2',digits=(20,4))
	cant_rest = fields.Integer(u'Cantidad restante')
	wizard_id = fields.Many2one('glass.pool.wizard','header_id')

	




	@api.onchange('selected')
	def onchangeselec(self):
		#print 'bbbbbb'
		self.wizard_id.product_id = self.product_id

class GlassPoolWizardLineDetail(models.TransientModel):
	_name='glass.pool.wizard.line.detail'

	order_line_id = fields.Many2one('glass.order.line')
	default_code = fields.Char(u'Código')
	product_id = fields.Many2one('product.product','Producto')
	crystal_number = fields.Integer('Nro. Cristal')
	base1 = fields.Integer("Base1 (L 4)",readonly=True)
	base2 = fields.Integer("Base2 (L 2)",readonly=True)
	altura1 = fields.Integer("Altura1 (L 1)",readonly=True)
	altura2 = fields.Integer("Altura2 (L 3)",readonly=True)
	descuadre = fields.Char("Descuadre",size=7,readonly=True)
	page_number = fields.Char(u"Nro. Pág.",readonly=True)
	obra = fields.Char('Obra')
	production_id = fields.Many2one('glass.order',"order")
	partner_id = fields.Many2one('res.partner',related="production_id.partner_id",string='Cliente')
	date_production = fields.Date(related="production_id.date_production",string='F. Prod.')

	wizard_id = fields.Many2one('glass.pool.wizard','header_id')
	select_line = fields.Boolean('V',default=False)

