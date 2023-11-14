# Todos

## Tolerancia a fallas

- Monitoring
  - Healthcheck
  - Heartbeats
  El "médico" se puede caer
  - Hay un lider -> algoritmo de selección de lider
    - Bully
  - Se ocupa de levantar nodos caidos
  - No se puede usar rabbit para esto, communicación sync

### AED: Medic implementation

Tiene 3 partes:

- monitoreo de nodos (protocolo TCP)
- Mecanismo de levantar nodos caidos
- Mecanismo de selección de lider


## Alta disponibilidad


- Replicacion para todas las partes (mismo al tp anterior)
- Filtro de duplicados, filtros sencillos (sin estado)
- Ventana de importancia de datos (descartar antiguos)


## Simulación de caida

Caos Engineering
- Programar algún sistema/algoritmo
  - Tirar un dado en cada instrucción
- para la demo hay que programar un sistema de simulación de fallas que tire aleatoriamente las instancias.
  

## Requerimientos

**! No hay reentrega**

### Clientes en paralelo/secuenciales

- Ningún dato es compartido entre clientes (incluso aeropouertos)


## Hipótesis

- Rabbitmq no se cae
- Los clientes no se caen

## Tareas

- Estado de los workers
