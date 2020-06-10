# -*- coding: utf-8 -*-
# from odoo import http


# class EgymentorsPurchaseFx(http.Controller):
#     @http.route('/egymentors_purchase_fx/egymentors_purchase_fx/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/egymentors_purchase_fx/egymentors_purchase_fx/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('egymentors_purchase_fx.listing', {
#             'root': '/egymentors_purchase_fx/egymentors_purchase_fx',
#             'objects': http.request.env['egymentors_purchase_fx.egymentors_purchase_fx'].search([]),
#         })

#     @http.route('/egymentors_purchase_fx/egymentors_purchase_fx/objects/<model("egymentors_purchase_fx.egymentors_purchase_fx"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('egymentors_purchase_fx.object', {
#             'object': obj
#         })
