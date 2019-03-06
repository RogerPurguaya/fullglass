
CREATE OR REPLACE VIEW public.vst_kardex_fisico_plancha AS 
 SELECT stock_move.product_uom,
    stock_move.move_dest_id,
        CASE
            WHEN sl.usage::text = 'supplier'::text THEN 0::double precision
            ELSE
            CASE
                WHEN original.id <> uomt.id THEN round((stock_move.price_unit * original.factor::double precision / uomt.factor::double precision)::numeric, 6)::double precision
                ELSE stock_move.price_unit
            END
        END AS price_unit,
        CASE
            WHEN product_uom.id <> uomt.id THEN round((stock_move.product_uom_qty::double precision * uomt.factor::double precision / product_uom.factor::double precision)::numeric, 6)
            ELSE stock_move.product_uom_qty
        END AS product_qty,
    stock_move.location_id,
    stock_move.location_dest_id,
    stock_move.picking_type_id,
    stock_move.product_id,
    stock_move.picking_id,
    COALESCE(stock_picking.invoice_id, 0) AS invoice_id,
        CASE
            WHEN stock_picking.es_fecha_kardex THEN stock_picking.fecha_kardex::timestamp without time zone
            ELSE
            CASE
                WHEN ai.date_invoice IS NULL THEN stock_picking.fecha_kardex::timestamp without time zone
                ELSE ai.date_invoice::timestamp without time zone
            END
        END AS date,
    stock_picking.name,
    stock_picking.partner_id,
    einvoice_catalog_12.code AS guia,
    stock_move.analitic_id,
    stock_move.id,
    product_product.default_code,
    stock_move.state AS estado,
    stock_move.product_uom_qty::double precision AS qtycompra,
    stock_move.product_uom AS uoncompra,
    1::numeric / product_uom.factor AS factor
   FROM stock_move
     JOIN product_uom ON stock_move.product_uom = product_uom.id
     JOIN stock_picking ON stock_move.picking_id = stock_picking.id
     JOIN stock_picking_type ON stock_picking.picking_type_id = stock_picking_type.id
     JOIN stock_location sl ON sl.id = stock_move.location_dest_id
     JOIN product_product ON stock_move.product_id = product_product.id
     JOIN product_template ON product_product.product_tmpl_id = product_template.id
     LEFT JOIN einvoice_catalog_12 ON stock_picking.einvoice_12 = einvoice_catalog_12.id
     JOIN product_uom uomt ON uomt.id =
        CASE
            WHEN product_template.unidad_kardex IS NOT NULL THEN product_template.unidad_kardex
            ELSE product_template.uom_id
        END
     JOIN product_uom original ON original.id = product_template.uom_id
     LEFT JOIN account_invoice ai ON ai.id = stock_picking.invoice_id
  WHERE (stock_move.state::text = ANY (ARRAY['done'::text, 'assigned'::text])) AND product_template.type::text = 'product'::text AND stock_move.picking_id IS NOT NULL;

ALTER TABLE public.vst_kardex_fisico_plancha
  OWNER TO postgres;
