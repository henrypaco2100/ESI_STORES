##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    store_id = fields.Many2one(
        related='warehouse_id.store_id',
        string='Store',
        store=True,
        index=True,
    )

    def write(self, vals):
        if 'active' in vals and self.mapped('store_id'):
            self = self.with_context(active_test=False)
        return super().write(vals)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        # ESI correccion: dominio robusto y sin modificar args del llamador.
        args = list(args or [])
        user = self.env.user
        if not self.env.is_superuser() and 'store_id' in self._fields:
            if getattr(user, 'store_id', False):
                args += ['|', ('store_id', '=', False),
                         ('store_id', 'child_of', [user.store_id.id])]
            elif 'store_ids' in user._fields and user.store_ids:
                args += ['|', ('store_id', '=', False),
                         ('store_id', 'in', user.store_ids.ids)]
        return super()._search(
            args, offset=offset, limit=limit, order=order, count=count,
            access_rights_uid=access_rights_uid)
