# -*- coding: utf-8 -*-
from odoo import models, fields, _


# Ahmed Salama Code Start ---->


class StockInventoryInherit(models.Model):
	_inherit = 'stock.inventory'
	
	ref = fields.Char("Code")
	
	def action_validate(self):
		self.ref = self.env['ir.sequence'].sudo().next_by_code('stock.inventory.code') or _('New')
		return super(StockInventoryInherit, self).action_validate()

# Ahmed Salama Code End.
