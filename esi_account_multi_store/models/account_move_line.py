##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    store_id = fields.Many2one(
        related='move_id.store_id',
        string='Store',
        store=True,
        index=True,
    )

    def _check_reconcile_validity(self):
        res = super()._check_reconcile_validity()
        if not self:
            return res

        # ESI correccion: comparar tiendas de forma segura, incluso si alguna
        # línea no tiene tienda asignada.
        first_store = self[0].store_id
        for line in self[1:]:
            restricted_store = line.store_id if (
                line.store_id and
                line.store_id.only_allow_reonciliaton_of_this_store
            ) else first_store if (
                first_store and
                first_store.only_allow_reonciliaton_of_this_store
            ) else False

            if restricted_store and line.store_id != first_store:
                raise UserError(_(
                    'For store "%s" you can only reconcile lines of the same store.'
                ) % restricted_store.display_name)
        return res

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        # ESI correccion: no modificar el dominio original y validar el campo.
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
