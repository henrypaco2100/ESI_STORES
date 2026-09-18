from odoo import api, fields, models


class AccountingReportBi(models.TransientModel):
    _inherit = 'accounting.report.bi'

    store_ids = fields.Many2many(
        'res.store',
        string='Sucursal'
,
    )

    @api.onchange('store_ids')
    def _set_journal_store(self):
        # ESI correccion: integración opcional, separada del núcleo contable.
        if self.store_ids and 'store_id' in self.env['account.journal']._fields:
            stores = self.store_ids | self.store_ids.mapped('child_ids')
            journals = self.env['account.journal'].search([
                ('store_id', 'in', stores.ids),
            ])
            self.journal_ids = [(6, 0, journals.ids)]
