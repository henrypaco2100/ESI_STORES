from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def get_journals_domain(self):
        # ESI correccion: esi_account_multi_store es ahora dependencia explícita,
        # por lo que store_id existe antes de construir este dominio.
        domain = list(super().get_journals_domain())
        store = self.payment_group_id.store_id
        if store and store.only_allow_reonciliaton_of_this_store:
            domain += [('store_id', '=', store.id)]
        elif store:
            domain += [
                '|',
                ('store_id', '=', False),
                ('store_id.only_allow_reonciliaton_of_this_store', '=', False),
            ]
        return domain
