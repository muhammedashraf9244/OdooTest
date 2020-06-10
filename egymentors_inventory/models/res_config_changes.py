# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class InventoryConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    
    stock_generate_seq = fields.Boolean("Picking Manual Sequence", default=False)
    
    @api.model
    def get_values(self):
        res = super(InventoryConfigSetting, self).get_values()
        res['stock_generate_seq'] = bool(self.env['ir.config_parameter'].get_param('egymentors_inventory.stock_generate_seq'))
        print("------ RES: ", res['stock_generate_seq'], type(res['stock_generate_seq']))
        return res

    def set_values(self):
        super(InventoryConfigSetting, self).set_values()
        self.stock_generate_seq and self.env['ir.config_parameter']. \
            set_param('egymentors_inventory.stock_generate_seq', self.stock_generate_seq)
        print("----- SET: ", self.stock_generate_seq, type(self.stock_generate_seq))
        

class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    generate_seq = fields.Boolean("Generate Sequence (Manual)",)
