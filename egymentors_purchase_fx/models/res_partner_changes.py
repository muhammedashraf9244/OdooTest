# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    sequence_id = fields.Many2one('ir.sequence', "Po Sequence")
    
    @api.constrains('ref')
    def ref_unique_constrain(self):
        for partner in self:
            if partner.ref and self.env['res.partner'].search_count([('ref', '=', partner.ref)]) > 1:
                raise Warning(_("Partner Ref violating unique constrain!!!"))

# Ahmed Salama Code End.
