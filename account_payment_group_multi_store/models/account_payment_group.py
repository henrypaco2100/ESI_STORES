from odoo import api, fields, models


class AccountPaymentGroup(models.Model):
    _inherit = 'account.payment.group'

    store_id = fields.Many2one(
        'res.store',
        string='Store',
        compute='_compute_store_id',
        readonly=False,
        store=True,
    )

    @api.depends_context('to_pay_move_line_ids')
    @api.depends('payment_ids.journal_id.store_id')
    def _compute_store_id(self):
        # ESI correccion: un Many2one nunca debe recibir un recordset con
        # múltiples tiendas; sólo asignamos cuando existe una única tienda.
        context_line_ids = self._context.get('to_pay_move_line_ids') or []
        context_stores = self.env['res.store']
        if context_line_ids:
            context_stores = self.env['account.move.line'].browse(
                context_line_ids
            ).mapped('journal_id.store_id')

        for rec in self:
            store = self.env['res.store']
            if len(context_stores) == 1:
                store = context_stores
            payment_stores = rec.payment_ids.mapped('journal_id.store_id')
            if len(payment_stores) == 1:
                store = payment_stores
            rec.store_id = store

    def _get_to_pay_move_lines_domain(self):
        res = list(super()._get_to_pay_move_lines_domain())
        store = self.store_id
        if store and store.only_allow_reonciliaton_of_this_store:
            res += [('store_id', '=', store.id)]
        elif store:
            res += [
                '|',
                ('store_id', '=', False),
                ('store_id.only_allow_reonciliaton_of_this_store', '=', False),
            ]
        return res

    @api.onchange('partner_id', 'partner_type', 'company_id', 'store_id')
    def _refresh_payments_and_move_lines(self):
        return super()._refresh_payments_and_move_lines()
