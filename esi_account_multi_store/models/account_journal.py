##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    # ESI correccion: este campo es la base de la integración contable por tienda.
    store_id = fields.Many2one(
        'res.store',
        string='Store',
        index=True,
        help=(
            'Store used for data analysis. Users working in another store '
            'should not select this journal for new operations.'
        ),
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False,
                access_rights_uid=None):
        """Restrict selectable journals without breaking registry searches.

        ESI correccion:
        - Never mutate the domain received from the caller.
        - Never add a domain for ``store_id`` if the field is not available in
          the current registry (important during upgrades / partial installs).
        - If the user has no current store, use the explicitly allowed stores.
        """
        args = list(args or [])
        user = self.env.user

        if not self.env.is_superuser() and 'store_id' in self._fields:
            if getattr(user, 'store_id', False):
                args += [
                    '|',
                    ('store_id', '=', False),
                    ('store_id', 'child_of', [user.store_id.id]),
                ]
            elif 'store_ids' in user._fields and user.store_ids:
                args += [
                    '|',
                    ('store_id', '=', False),
                    ('store_id', 'in', user.store_ids.ids),
                ]

        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
