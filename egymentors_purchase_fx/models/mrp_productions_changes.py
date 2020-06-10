# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class MrpProductionInherit(models.Model):
	_inherit = 'mrp.production'
	
	sale_line_id = fields.Many2one('sale.order.line', "Sale Line")
	
	@api.model
	def create(self, values):
		if values.get('origin'):
			so_name = '/' in values.get('origin') and values.get('origin').split('/')[0] or values.get('origin')
			order_id = self.env['sale.order'].search([('name', '=', so_name)])
			if order_id:
				line_id = order_id.order_line.\
					filtered(lambda l: l.product_id.id == values.get('product_id')
				                      and l.product_uom_qty == values.get('product_qty'))
				values['sale_line_id'] = line_id and line_id[0].id or False
		production = super(MrpProductionInherit, self).create(values)
		return production
	
	def _action_cancel(self):
		res = super(MrpProductionInherit, self)._action_cancel()
		if self.sale_line_id:
			self.sale_line_id.write({'line_status': 'closed'})
		return res

# Ahmed Salama Code End.
