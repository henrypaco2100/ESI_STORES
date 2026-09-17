# -*- coding: utf-8 -*-
# ESI correccion 2026: actualizar la regla histórica aunque el XML-ID haya
# sido creado originalmente con noupdate=1.


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_rule r
           SET domain_force = %s,
               perm_read = TRUE,
               perm_write = TRUE,
               perm_create = TRUE,
               perm_unlink = TRUE
          FROM ir_model_data d
         WHERE d.model = 'ir.rule'
           AND d.module = 'sale_multi_store'
           AND d.name = 'sale_order_store_rule'
           AND r.id = d.res_id
    """, ["['|', ('store_id', '=', False), ('store_id', 'child_of', ([user.store_id.id] if user.store_id else user.store_ids.ids))]"])
    cr.execute("""
        UPDATE ir_model_data
           SET noupdate = FALSE
         WHERE module = 'sale_multi_store'
           AND name = 'sale_order_store_rule'
           AND model = 'ir.rule'
    """)
