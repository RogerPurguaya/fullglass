# -*- coding: utf-8 -*-
from odoo import models, fields, api,exceptions,SUPERUSER_ID
from openerp.osv import osv
import datetime
import urlparse
import urllib


class modalmsg(models.Model):
	_name = 'modalmsg'
	
	msg=fields.Char('message')

	


