
# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class AccountPrintCashSet(models.TransientModel):
    _inherit = "account.common.cash.report"
    _name = "account.print.cash"
    _description = "Account Print Cash"

    target_move = fields.Selection([('posted', 'Todos los asientos Publicados'),
                                    ('all', 'Todos los Asientos '),
                                    ], string='Target Moves', required=True, default='posted')

    sort_selection = fields.Selection([('date', 'Fecha'), ('move_name', 'Número de asiento'),], 'Asientos ordenados por', required=True, default='move_name')
    journal_ids = fields.Many2many('account.journal', string='Diarios', required=True, default=lambda self: self.env['account.journal'].search([('id', 'in', ['1'])]))

    account_id = fields.Many2many('account.account','table_account', string='Tipo de Cuenta', requiered=True,default=lambda self: self.env['account.account'].search([('id', 'in', ['31'])]))
    # serie_id = fields.Many2many('account.config.efective','table_serie', string='Tipo de Serie', requiered=True)
    serie_id = fields.Many2many('it.invoice.serie','table_serie', string='Tipo de Serie', requiered=True)
    def _print_report(self, data):
        data = self.pre_print_report(data)
        s_list = []
        a_list = []
        for s in self.serie_id:
            if (s.name == "Serie de facturas 0001"):
                s_list.append("0001-")
            else:
                s_list.append(s.name)
        for a in self.account_id:
            a_list.append(a.code)
        data['form'].update({'sort_selection': self.sort_selection})
        data['form'].update({'account_id':a_list})
        data['form'].update({'serie_id':s_list})
        return self.env['report'].with_context(landscape=True).get_action(self, 'report_cash.report_invoice', data=data)