##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ESI correccion 2026: la sucursal de la venta ya no se deduce del
    # almacén. Se deja como campo propio para que otros módulos (por ejemplo
    # Tipo de Ventas) decidan cuándo asignarla. Esto permite que una
    # cotización borrador sin tipo de venta permanezca visible para todas las
    # sucursales, tal como se requiere.
    store_id = fields.Many2one(
        'res.store',
        string='Sucursal',
        index=True,
        copy=True,
    )
