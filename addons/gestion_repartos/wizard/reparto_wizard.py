# -*- coding: utf-8 -*-

from odoo import models, fields, api

class RepartoWizard(models.TransientModel):
    _name = 'reparto.wizard'
    _description = 'Asistente de Creación Rápida de Repartos'

    # Campos simplificados para el wizard
    cliente_id = fields.Many2one('reparto.cliente', string="Cliente", required=True)
    repartidor_id = fields.Many2one('reparto.empleado', string="Repartidor")
    vehiculo_id = fields.Many2one('reparto.vehiculo', string="Vehículo")
    kilometros = fields.Float(string="Kms")
    receptor_datos = fields.Text(string="Datos Receptor", required=True)
    urgencia = fields.Selection([
        ('0_baja', 'Baja'),
        ('1_alta', 'Alta'),
        ('2_alimentos', 'Alimentos'),
        ('4_organos', 'Órganos')
    ], string='Urgencia', default='1_alta')

    def crear_reparto(self):
        # Este método se ejecuta al pulsar el botón "Crear"
        vals = {
            'cliente_id': self.cliente_id.id,
            'repartidor_id': self.repartidor_id.id,
            'vehiculo_id': self.vehiculo_id.id,
            'kilometros': self.kilometros,
            'receptor_datos': self.receptor_datos,
            'urgencia': self.urgencia,
            'estado': 'no_salido', # Estado inicial por defecto
            'fecha_recepcion': fields.Datetime.now()
        }
        
        # Crear el registro en el modelo principal
        nuevo_reparto = self.env['reparto.pedido'].create(vals)
        
        # Acción para abrir el reparto recién creado (Opcional, pero queda muy pro)
        return {
            'name': 'Reparto Creado',
            'type': 'ir.actions.act_window',
            'res_model': 'reparto.pedido',
            'res_id': nuevo_reparto.id,
            'view_mode': 'form',
            'target': 'current',
        }