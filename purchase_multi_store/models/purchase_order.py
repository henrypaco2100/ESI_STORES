##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # ESI correccion 2026: campo propio de sucursal. La asignación se realiza
    # desde el Tipo de Compra. Un borrador sin tipo queda sin sucursal y es
    # visible para todos los usuarios autorizados.
    store_id = fields.Many2one(
        'res.store',
        string='Sucursal',
        index=True,
        copy=True,
    )
