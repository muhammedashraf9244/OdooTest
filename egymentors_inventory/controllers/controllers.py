# -*- coding: utf-8 -*-
# from odoo import http


# class EgymentorsInventory(http.Controller):
#     @http.route('/egymentors_inventory/egymentors_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/egymentors_inventory/egymentors_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('egymentors_inventory.listing', {
#             'root': '/egymentors_inventory/egymentors_inventory',
#             'objects': http.request.env['egymentors_inventory.egymentors_inventory'].search([]),
#         })

#     @http.route('/egymentors_inventory/egymentors_inventory/objects/<model("egymentors_inventory.egymentors_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('egymentors_inventory.object', {
#             'object': obj
#         })
