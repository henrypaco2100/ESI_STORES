##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    store_id = fields.Many2one(
        related='journal_id.store_id',
        string='Store',
        store=True,
        index=True,
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        # ESI correccion: dominio seguro para instalaciones/actualizaciones parciales.
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


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    store_id = fields.Many2one('res.store', string='Sucursal', readonly=True)

    def _select(self):
        # ESI correccion: mantener la tienda disponible en el análisis de facturas.
        return super()._select() + ', move.store_id as store_id'

    def _group_by(self):
        return super()._group_by() + ', move.store_id'
