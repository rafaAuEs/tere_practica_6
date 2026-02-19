# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Empleado(models.Model):
    _name = 'reparto.empleado'
    _description = 'Empleado de Reparto'
    _rec_name = 'nombre' # Por defecto busca el campo name, aquí usamos nombre

    dni = fields.Char(string='DNI', required=True)
    nombre = fields.Char(string='Nombre', required=True)
    apellidos = fields.Char(string='Apellidos', required=True)
    telefono = fields.Char(string='Teléfono')
    foto = fields.Binary(string='Fotografía')
    
    # Carnets (Booleanos para check boxes)
    carnet_ciclomotor = fields.Boolean(string='Carnet de Ciclomotor')
    carnet_furgoneta = fields.Boolean(string='Carnet de Furgoneta')

    # Relación: Un empleado -> Muchos repartos
    reparto_ids = fields.One2many('reparto.pedido', 'repartidor_id', string='Historial de Repartos')

    # Campo computado para nombre completo (Opcional pero recomendado para buena presentación)
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.nombre} {record.apellidos}"
            result.append((record.id, name))
        return result


class Vehiculo(models.Model):
    _name = 'reparto.vehiculo'
    _description = 'Vehículo de Reparto'
    _rec_name = 'matricula'

    tipo = fields.Selection([
        ('bicicleta', 'Bicicleta'),
        ('furgoneta', 'Furgoneta')
    ], string='Tipo de Vehículo', required=True, default='furgoneta')
    
    matricula = fields.Char(string='Matrícula')
    foto = fields.Binary(string='Fotografía')
    descripcion = fields.Text(string='Descripción')
    estado = fields.Selection([
        ('disponible', 'Disponible'),
        ('reparto', 'En Reparto')
    ], string='Estado', default='disponible')


class Cliente(models.Model):
    _name = 'reparto.cliente'
    _description = 'Cliente'
    _rec_name = 'nombre'

    dni = fields.Char(string='DNI', required=True)
    nombre = fields.Char(string='Nombre', required=True)
    apellidos = fields.Char(string='Apellidos', required=True)
    telefono = fields.Char(string='Teléfono')

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.nombre} {record.apellidos}"
            result.append((record.id, name))
        return result


class Pedido(models.Model):
    _name = 'reparto.pedido'
    _description = 'Pedido de Reparto'
    # Requisito: Ordenar por fecha recepción y urgencia
    _order = 'fecha_recepcion desc, urgencia desc' 

    name = fields.Char(string='Código Referencia', required=True, copy=False, readonly=True, default='Nuevo')
    
    fecha_inicio = fields.Datetime(string='Fecha Salida')
    fecha_retorno = fields.Datetime(string='Fecha Retorno')
    fecha_recepcion = fields.Datetime(string='Fecha Recepción', default=fields.Datetime.now, required=True)
    
    # Relaciones
    repartidor_id = fields.Many2one('reparto.empleado', string='Repartidor Asignado')
    vehiculo_id = fields.Many2one('reparto.vehiculo', string='Vehículo Asignado')
    cliente_id = fields.Many2one('reparto.cliente', string='Cliente Emisor', required=True)
    
    # Datos del paquete
    receptor_datos = fields.Text(string='Datos del Receptor (Dirección/Nombre)', required=True)
    kilometros = fields.Float(string='Distancia (Km)', required=True)
    peso = fields.Float(string='Peso (Kg)')
    volumen = fields.Float(string='Volumen (m3)')
    observaciones = fields.Text(string='Observaciones')
    
    estado = fields.Selection([
        ('no_salido', 'No ha salido'),
        ('camino', 'En camino'),
        ('entregado', 'Entregado')
    ], string='Estado', default='no_salido', required=True)
    
    urgencia = fields.Selection([
        ('0_baja', 'Baja prioridad'),
        ('1_alta', 'Alta prioridad'),
        ('2_alimentos', 'Alimentos'),
        ('3_refrigerados', 'Alimentos refrigerados'),
        ('4_organos', 'Órganos humanos')
    ], string='Urgencia', default='0_baja', required=True)

    @api.constrains('repartidor_id', 'vehiculo_id', 'kilometros')
    def _check_reglas_reparto(self):
        for record in self:
            # 1. Regla de Carnets
            if record.vehiculo_id.tipo == 'furgoneta' and not record.repartidor_id.carnet_furgoneta:
                raise ValidationError("¡Error! El repartidor %s no tiene carnet de furgoneta." % record.repartidor_id.nombre)
            
            if record.vehiculo_id.tipo == 'bicicleta' and not record.repartidor_id.carnet_ciclomotor:
                # Nota: El enunciado pide carnet de ciclomotor, aunque sea una bici, seguimos la regla.
                raise ValidationError("¡Error! El repartidor %s no tiene carnet para conducir este vehículo." % record.repartidor_id.nombre)

            # 2. Regla de Distancias
            if record.vehiculo_id.tipo == 'bicicleta' and record.kilometros > 10:
                raise ValidationError("No se pueden realizar repartos de más de 10 Km en bicicleta.")
            
            if record.vehiculo_id.tipo == 'furgoneta' and record.kilometros < 1:
                raise ValidationError("Los repartos de menos de 1 Km deben hacerse en bicicleta, no en furgoneta.")

    @api.constrains('repartidor_id', 'vehiculo_id', 'estado')
    def _check_disponibilidad(self):
        for record in self:
            if record.estado == 'camino':
                # Buscar si el empleado ya está en otro reparto 'en camino'
                repartos_empleado = self.search([
                    ('repartidor_id', '=', record.repartidor_id.id),
                    ('estado', '=', 'camino'),
                    ('id', '!=', record.id)
                ])
                if repartos_empleado:
                    raise ValidationError("El empleado %s ya está en un reparto activo." % record.repartidor_id.nombre)

                # Buscar si el vehículo ya está en otro reparto 'en camino'
                repartos_vehiculo = self.search([
                    ('vehiculo_id', '=', record.vehiculo_id.id),
                    ('estado', '=', 'camino'),
                    ('id', '!=', record.id)
                ])
                if repartos_vehiculo:
                    raise ValidationError("El vehículo ya está asignado a otro reparto activo.")
                
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            # Llamamos a la secuencia que definimos en el XML
            vals['name'] = self.env['ir.sequence'].next_by_code('reparto.pedido') or 'Nuevo'
        return super(Pedido, self).create(vals)