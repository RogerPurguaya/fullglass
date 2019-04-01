from odoo import api,models,fields

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			domain = [('number', operator, name)]
		invoices = self.search(domain + args, limit=limit)
		return invoices.name_get()
	
