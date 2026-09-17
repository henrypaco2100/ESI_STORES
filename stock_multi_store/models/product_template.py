from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    store_ids = fields.Many2many('res.store', string="Tienda")