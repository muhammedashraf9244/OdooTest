# -*- coding: utf-8 -*-
from odoo import models, fields, api


# Ahmed Salama Code Start ---->


class StockPickingInherit(models.Model):
	_inherit = 'stock.picking'
	
	generate_seq = fields.Boolean("Generate Sequence (Manual)",
	                              default=lambda self: self.env.company.generate_seq)
	
	def act_generate_seq(self):
		for picking in self:
			if picking.name == '/' and picking.picking_type_id:
				picking.write({'name': picking.picking_type_id.sequence_id.next_by_id(),
				               'generate_seq': False})
	
	@api.model
	def create(self, vals):
		# As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
		# As it is a create the format will be a list of (0, 0, dict)
		moves = vals.get('move_lines', []) + vals.get('move_ids_without_package', [])
		if moves and vals.get('location_id') and vals.get('location_dest_id'):
			for move in moves:
				if len(move) == 3 and move[0] == 0:
					move[2]['location_id'] = vals['location_id']
					move[2]['location_dest_id'] = vals['location_dest_id']
					# When creating a new picking, a move can have no `company_id` (create before
					# picking type was defined) or a different `company_id` (the picking type was
					# changed for an another company picking type after the move was created).
					# So, we define the `company_id` in one of these cases.
					picking_type = self.env['stock.picking.type'].browse(vals['picking_type_id'])
					if 'picking_type_id' not in move[2] or move[2]['picking_type_id'] != picking_type.id:
						move[2]['picking_type_id'] = picking_type.id
						move[2]['company_id'] = picking_type.company_id.id
		if 'generate_seq' in vals and not vals['generate_seq']:
			defaults = self.default_get(['name', 'picking_type_id'])
			picking_type = self.env['stock.picking.type'].browse(
				vals.get('picking_type_id', defaults.get('picking_type_id')))
			if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' \
					and vals.get('picking_type_id', defaults.get('picking_type_id')):
				vals['name'] = picking_type.sequence_id.next_by_id()
		res = super(models.Model, self).create(vals)
		res._autoconfirm_picking()
		# set partner as follower
		if vals.get('partner_id'):
			for picking in res.filtered(
					lambda p: p.location_id.usage == 'supplier' or p.location_dest_id.usage == 'customer'):
				picking.message_subscribe([vals.get('partner_id')])
		
		return res
	
	# @api.depends('state', 'is_locked')
	# def _compute_show_validate(self):
	# 	for picking in self:
	# 		if not (picking.immediate_transfer) and picking.state == 'draft' and picking.generate_seq:
	# 			picking.show_validate = False
	# 		elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned') or not picking.is_locked:
	# 			picking.show_validate = False
	# 		else:
	# 			picking.show_validate = True
	
	# def action_confirm(self):
	# 	"""
	# 	Add Sequence on Mark as to do action instead of create
	# 	:return:
	# 	"""
	# 	self.generate_seq()
	# 	return super(StockPickingInherit, self).action_confirm()
	

# Ahmed Salama Code End.
