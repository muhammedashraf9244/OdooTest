# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

# Ahmed Salama Code Start ---->


class PurchaseOrderInherit(models.Model):
	_inherit = 'purchase.order'
	
	multi_requisition = fields.Boolean("Multi Requests")
	request_id = fields.Many2one('purchase.request', 'Purchase Request', copy=False,
	                             domain=[('state', '=', 'done')],
	                             help="Choose Confirmed request and load it's lines on PO")
	request_ids = fields.Many2many(comodel_name='purchase.request',  copy=False)
	request_added = fields.Boolean()
	
	def load_pr_lines(self):
		for order in self:
			if order.multi_requisition:
				request_ids = order.request_ids
			else:
				request_ids = [order.request_id]
			if request_ids:
				order_products = order.order_line.mapped('product_id.id')
				for request_id in request_ids:
					# if request_id.purchase_order_id:
					# 	raise Warning(_("This Request %s Used Before in Order %s") % (request_id.name,
					# 																  request_id.purchase_order_id.name))
					for line in request_id.request_line.filtered(lambda l: l.state == 'done'):
						if line.product_id.id in order_products:
							order_line = order.order_line.filtered(lambda l:
							                                       l.product_id.id == line.product_id.id)
							request_line_ids = order_line[0].request_line_ids.ids
							request_line_ids.append(line.id)
							order_line[0].write({'product_qty': line.product_qty + order_line[0].product_qty,
							                     'request_line_ids': [(6, 0, request_line_ids)]})
						else:
							order.order_line.create({
								'order_id': order.id,
								'request_line_ids': [(6, 0, [line.id])],
								'product_qty': line.product_qty,
								'price_unit': 0.0,
								'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
								'product_id': line.product_id.id,
								'name': line.product_id.display_name,
								'product_uom': line.product_id.uom_po_id and line.product_id.uom_po_id.id or line.product_id.uom_id.id,
							})
							order_products.append(line.product_id.id)
					# 'state': 'locked',
					request_id.write({'purchase_order_id': order.id})
				order.request_added = True
			else:
				raise Warning(_("No Request To load"))
	
	def remove_pr_lines(self):
		for order in self:
			if order.multi_requisition:
				request_ids = order.request_ids
			else:
				request_ids = [order.request_id]
			if request_ids:
				for request_id in request_ids:
					for line in request_id.request_line:
						order_line = order.order_line.filtered(lambda l: line.id in l.request_line_ids.ids)
						if order_line:
							# IT's Only Line Created with pr Line qty
							if order_line[0].product_qty == line.product_qty:
								order_line[0].unlink()
							# IT's Order Line And will deduct pr line qty
							elif order_line[0].product_qty > line.product_qty:
								request_line_list = order_line[0].request_line_ids.ids
								request_line_ids = False
								if request_line_list:
									if len(request_line_list) > 1:
										request_line_list.remove(line.id)
										request_line_ids = [(6, 0, request_line_list)]
								
								order_line[0].write({'product_qty': order_line.product_qty - line.product_qty,
								                     'request_line_ids': request_line_ids})
							# THis line is edit and qty is bellow pr line qty (User miss using)
							else:
								raise Warning(_("User Changed Qty for this product [%s]\n"
								                " Please Make it's qty bigger than purchase request line qty:%s") %(
									              order_line[0].product_id.display_name, line.product_qty
								              ))
					request_id.write({'state': 'done', 'purchase_order_id': False})
				order.request_added = False
			else:
				raise Warning(_("No Request To remove"))
	
	def amount_to_text(self):
		amount_text = self.currency_id.with_context({'lang': self.env.user.lang}).amount_to_text(
			self.amount_total)
		if self.env.user.lang in ['ar', 'ar_SY', 'ar_001']:
			amount_in_words = "%s %s" % (amount_text, "فقط لا غير.")
			amount_in_words = str(amount_in_words).replace('Euros', 'يورو')
			amount_in_words = str(amount_in_words).replace('Dollars', 'دولارات')
			amount_in_words = str(amount_in_words).replace('Dollar', 'دولار')
			amount_in_words = str(amount_in_words).replace('Cents', 'سنتاً')
			amount_in_words = str(amount_in_words).replace('Cent', 'سنت')
			amount_in_words = str(amount_in_words).replace('Pound', 'جنيهاً')
			amount_in_words = str(amount_in_words).replace('Pounds', 'جنيهات')
			amount_in_words = str(amount_in_words).replace('Piastres', 'قرشاً')
		else:
			amount_in_words = "%s Only." % amount_text
		return amount_in_words
	
	def purchase_taxes(self):
		tax_obj = self.env['account.tax']
		for order in self:
			taxes_dict = []
			taxes = []
			# Group taxes
			for line in order.order_line:
				if line.taxes_id:
					for tax_id in line.taxes_id.ids:
						if tax_id not in taxes:
							taxes.append(tax_id)
			if taxes:
				for tax_id in taxes:
					tax = tax_obj.browse(tax_id)
					tax_amount = 0
					for line in order.order_line:
						if tax_id in line.taxes_id.ids:
							vals = line._prepare_compute_all_values()
							taxes = tax.compute_all(
								vals['price_unit'],
								vals['currency_id'],
								vals['product_qty'],
								vals['product'],
								vals['partner'])
							tax_amount += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
					taxes_dict.append({
						'tax_name': tax.name,
						'tax_amount': tax_amount,
					})
			return taxes_dict
	
	# TODO: ADD SECTOR FOR TAXES SUCH AS INVOICE
	amount_by_group = fields.Binary(string="Tax amount by group",
	                                compute='compute_purchase_taxes_by_group')
	
	@api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.taxes_id',
	             'amount_tax', 'partner_id', 'currency_id')
	def compute_purchase_taxes_by_group(self):
		''' Helper to get the taxes grouped according their account.tax.group.
        This method is only used when printing the invoice.
        '''
		for order in self:
			lang_env = order.with_context(lang=order.partner_id.lang).env
			tax_lines = order.order_line.filtered(lambda line: line.taxes_id.ids != [])
			res = {}
			# There are as many tax line as there are repartition lines
			done_taxes = set()
			for line in tax_lines:
				for tax_id in line.taxes_id:
					tax_dict = tax_id.compute_all(line.price_unit, line.currency_id,
					                              line.product_qty, line.product_id,
					                              order.partner_id).get('taxes', [])[0]
					print("tax_dict: ", tax_dict)
					if tax_dict:
						price_tax = tax_dict.get('amount')
						res.setdefault(tax_id.tax_group_id, {'base': 0.0, 'amount': 0.0})
						res[tax_id.tax_group_id]['amount'] += price_tax
						tax_key_add_base = tuple(order._get_tax_key_for_group_add_base(line))
						if tax_key_add_base not in done_taxes:
							if line.currency_id != self.company_id.currency_id:
								amount = self.company_id.currency_id._convert(price_tax, line.currency_id,
								                                              self.company_id, fields.Date.today())
							else:
								amount = price_tax
							res[tax_id.tax_group_id]['base'] += amount
							# The base should be added ONCE
							done_taxes.add(tax_key_add_base)
			res = sorted(res.items(), key=lambda l: l[0].sequence)
			order.amount_by_group = [(
				group.name, amounts['amount'],
				amounts['base'],
				formatLang(lang_env, amounts['amount'], currency_obj=order.currency_id),
				formatLang(lang_env, amounts['base'], currency_obj=order.currency_id),
				len(res),
				group.id
			) for group, amounts in res]
	
	@api.model
	def _get_tax_key_for_group_add_base(self, line):
		"""
        Useful for compute_purchase_taxes_by_group
        must be consistent with _get_tax_grouping_key_from_tax_line
         @return list
        """
		return line.taxes_id.ids
	
	@api.onchange('requisition_id')
	def _onchange_requisition_id(self):
		super(PurchaseOrderInherit, self)._onchange_requisition_id()
		self.request_id = self.requisition_id.request_id and self.requisition_id.request_id.id or False
		self.request_ids = self.requisition_id.request_ids and \
		                   [(6, 0, self.requisition_id.request_id.ids)] or False


class PurchaseOrderLineInherit(models.Model):
	_inherit = 'purchase.order.line'
	
	request_line_ids = fields.Many2many('purchase.request.line', string="Request Lines")
	requisition_line_id = fields.Many2one('purchase.requisition.line', 'Requisition Line')
	accepted = fields.Boolean("Accepted")
	
	def unlink(self):
		for line in self:
			if not line.request_line_ids and line.order_id.state in ['purchase', 'done']:
				raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.state,))
		return super(models.Model, self).unlink()
	
	@api.constrains('requisition_line_id', 'accepted')
	def _accepted_lines_constrain(self):
		obj = self.env['purchase.order.line']
		for line in obj:
			if line.accepted:
				other_lines = obj.search([('accepted', '=', True),
				                          ('id', '!=', line.id),
				                          ('requisition_line_id', '=', line.requisition_line_id.id)])
				for l in other_lines:
					raise Warning(_("You Can't accept this line: %s\nIt's already accepted on "
					                "Quotation[%s] from vendor: %s." %
					                (l.product_id.display_name, l.order_id.name, l.partner_id.name)))
	
	@api.model
	def create(self, vals):
		line = super(PurchaseOrderLineInherit, self).create(vals)
		print("VALS: ", vals.get('accepted'), line.request_line_ids)
		if 'accepted' in vals and line.request_line_ids:
			for request_line in line.request_line_ids:
				print("REQUEST LINE: ", request_line)
				if vals.get('accepted'):
					state = 'locked'
				else:
					continue
				request_line.write({'state': state})
				request_id = request_line.request_id
				if all(state == 'locked' for state in request_id.request_line.mapped('state')):
					request_id.write({'state': 'locked'})
				elif any(state == 'done' for state in request_id.request_line.mapped('state')) \
						and request_id.state == 'locked':
					request_id.write({'state': 'done'})
		return line
	
	def write(self, vals):
		super(PurchaseOrderLineInherit, self).write(vals)
		if 'accepted' in vals and self.request_line_ids:
			for request_line in self.request_line_ids:
				print("REQUEST LINE: ", request_line)
				if vals.get('accepted'):
					state = 'locked'
				else:
					state = 'done'
				request_line.write({'state': state})
				request_id = request_line.request_id
				if all(state == 'locked' for state in request_id.request_line.mapped('state')):
					request_id.write({'state': 'locked'})
				elif any(state == 'done' for state in request_id.request_line.mapped('state')) \
						and request_id.state == 'locked':
					request_id.write({'state': 'done'})
		return True


# Ahmed Salama Code End.
