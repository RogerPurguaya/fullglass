from odoo import api, fields, models, exceptions
from datetime import datetime, timedelta

class PostponeOpWizard(models.TransientModel):
    _name = 'postpone.op.wizard'
    date_production = fields.Date(string='Nueva Fecha de Produccion')
    
    @api.multi
    def set_values_dates_op(self):
        order = self.env['glass.order'].search([('id','=',self._context['active_id'])])

        if self.date_production <= order.date_production:
            raise exceptions.Warning('La nueva fecha ('+str(self.date_production)+') no puede ser anterior o igual a la fecha original ('+str(order.date_production)+') de la OP')
        
        dateprod = datetime.strptime(self.date_production.replace('-',''),'%Y%m%d').date()
        if dateprod.weekday()==6:
            dateprod = dateprod+timedelta(days=1)

        config=self.env['glass.order.config'].search([])
        if len(config)==0:
            raise exceptions.Warning(u'No se encontraron los valores de configuracion de produccion')
        config=self.env['glass.order.config'].search([])[0]
        limite = False
        for linec in config.limit_ids:
            if linec.motive_limit=='templado':
                limite = linec
        if not limite:
            raise exceptions.Warning(u"No se ha encontra la configuracion de plazos de produccion")

        dias_send = 0
        aux = False
        if order.destinity_order=='local':
            dias_send = dias_send+limite.local_send
            aux = True
        
        if order.destinity_order=='external':
            dias_send = dias_send+limite.external_send	
        datesend = dateprod+timedelta(days=dias_send)

        if order.send2partner:
            dias_send = dias_send+limite.send2partner

        datedeli = None
        if aux: # si la entrega es en la ciudad, delivery_date es igual a la send_date
            datedeli = datesend
        else:
            datedeli = datesend+timedelta(days=dias_send)

        old_date = order.date_production
        order.write({
            'date_production': dateprod,
            'date_send': datesend,
            'date_delivery': datedeli,
        })

        data = {
            'subject': 'Reprogramacion de OP: ' + str(order.name),
            'message': 'Se ha reprogramado la fecha de produccion de la OP '+str(order.name)+' del '+str(old_date)+' al ' + str(dateprod) + '.'
        }

        sender = self.env['send.email.event'].create(data)
        res = sender.send_emails(motive='reprograming_op') 
        return res