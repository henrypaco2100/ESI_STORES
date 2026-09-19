# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AutomatedPurchaseStore(models.Model):
    _inherit = 'automated.purchase'

    store_id = fields.Many2one(
        'res.store', string='Sucursal',
        default=lambda self: self.env.user.store_id if self.env.user.store_id else False,
    )

    @api.onchange('company_id')
    def _onchange_company_id_store_esi(self):
        for rec in self:
            if rec.store_id and rec.store_id.company_id and rec.store_id.company_id != rec.company_id:
                rec.store_id = False

    @api.onchange('store_id')
    def _onchange_store_id_esi(self):
        for rec in self:
            if rec.st_almacen and rec.st_almacen.store_id != rec.store_id:
                rec.st_almacen = False
                rec.st_entregar_a = False
            if rec.purchase_journal and rec.purchase_journal.store_id and rec.purchase_journal.store_id != rec.store_id:
                rec.purchase_journal = False
            if rec.payment_journal and rec.payment_journal.store_id and rec.payment_journal.store_id != rec.store_id:
                rec.payment_journal = False
            if rec.store_id and not rec.st_almacen:
                warehouses = self.env['stock.warehouse'].search([
                    ('company_id', '=', rec.company_id.id),
                    ('store_id', '=', rec.store_id.id),
                ], limit=2)
                if len(warehouses) == 1:
                    rec.st_almacen = warehouses
                    rec.st_entregar_a = warehouses.in_type_id

    @api.constrains('store_id', 'company_id', 'st_almacen', 'purchase_journal', 'payment_journal')
    def _check_store_configuration_esi(self):
        for rec in self:
            if rec.store_id and rec.store_id.company_id and rec.store_id.company_id != rec.company_id:
                raise ValidationError(_('La sucursal no pertenece a la compañía seleccionada.'))
            if rec.st_almacen and rec.st_almacen.store_id != rec.store_id:
                raise ValidationError(_('El almacén no pertenece a la sucursal seleccionada.'))
            for journal in (rec.purchase_journal, rec.payment_journal):
                if journal and journal.store_id and journal.store_id != rec.store_id:
                    raise ValidationError(_('El diario %s no pertenece a la sucursal seleccionada.') % journal.display_name)


class PurchaseOrderStore(models.Model):
    _inherit = 'purchase.order'

    work_process_order_id = fields.Many2one(
        'automated.purchase', string='Tipo de Compra', copy=True,
        domain=lambda self: self._esi_store_purchase_type_domain(),
    )

    @api.model
    def _esi_store_purchase_type_domain(self):
        domain = ['&', ('active', '=', True), '|',
                  ('company_id', '=', False), ('company_id', '=', self.env.user.company_id.id)]
        user = self.env.user
        if user.store_id:
            domain += ['|', ('store_id', '=', False), ('store_id', 'child_of', [user.store_id.id])]
        elif user.store_ids:
            domain += ['|', ('store_id', '=', False), ('store_id', 'in', user.store_ids.ids)]
        return domain

    @api.model
    def _esi_purchase_type_vals(self, purchase_type):
        vals = super()._esi_purchase_type_vals(purchase_type)
        vals['store_id'] = purchase_type.store_id.id or False
        return vals

    @api.onchange('work_process_order_id')
    def _onchange_work_process_order_id_store_esi(self):
        res = super()._onchange_work_process_order_id_esi()
        for order in self:
            order.store_id = order.work_process_order_id.store_id if order.work_process_order_id else False
        return res

    def write(self, vals):
        vals = dict(vals)
        if 'work_process_order_id' in vals and not vals.get('work_process_order_id'):
            vals['store_id'] = False
        return super().write(vals)

    def _esi_validate_purchase_type(self):
        res = super()._esi_validate_purchase_type()
        for order in self:
            purchase_type = order.work_process_order_id
            if purchase_type.store_id and purchase_type.st_almacen and purchase_type.st_almacen.store_id != purchase_type.store_id:
                raise UserError(_('El almacén del Tipo de Compra no corresponde a su Sucursal.'))
            if purchase_type.store_id:
                for journal in (purchase_type.purchase_journal, purchase_type.payment_journal):
                    if journal and journal.store_id and journal.store_id != purchase_type.store_id:
                        raise UserError(_('Los diarios del Tipo de Compra deben corresponder a la misma sucursal.'))
        return res
