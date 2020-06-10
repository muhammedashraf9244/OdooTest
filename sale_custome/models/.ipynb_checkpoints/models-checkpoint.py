# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sales_custome(models.Model):
     _inherit = 'sale.order'
     customer_order=fields.Char(string="Customer’s order")
    
class delivery_custome(models.Model):
     _inherit = 'sale.order'
     customer_order=fields.Many2one(string="Customer’s order")
    
