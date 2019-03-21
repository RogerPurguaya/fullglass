# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountCommonCashReport(models.TransientModel):
    _name = 'account.common.cash.report'
    _description = 'Account Common Cash Report'
    _inherit = "account.common.report"

    amount_currency = fields.Boolean('Con Moneda', help="Print Report with the currency column if the currency differs from the company currency.")

    @api.multi
    def pre_print_report(self, data):
        data['form'].update({'amount_currency': self.amount_currency})
        return data
