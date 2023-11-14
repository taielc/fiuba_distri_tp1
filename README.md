# TP1 de Sistemas Distribuidos I

Integrantes:

| Nombre y Apellido | Padron |
|:-----|:---:|
| Taiel Colavecchia | 102510 |
| Lucia Kasman | 97112 |

# Indice

Indice:
- [TP1 de Sistemas Distribuidos I](#tp1-de-sistemas-distribuidos-i)
- [Indice](#indice)
- [Documentación técnica](#documentación-técnica)
  - [Uso](#uso)
    - [Cliente](#cliente)
  - [Introducción](#introducción)
  - [Desarrollo](#desarrollo)
  - [DAG de la solución](#dag-de-la-solución)
  - [Cómo correr el proyecto](#cómo-correr-el-proyecto)
    - [Cliente](#cliente-1)
  - [Vistas](#vistas)
    - [Escenarios](#escenarios)
    - [Física](#física)
      - [Despliegue](#despliegue)
      - [Robustez](#robustez)
    - [Procesos](#procesos)
      - [Actividad](#actividad)
      - [Secuencia](#secuencia)
    - [Desarrollo](#desarrollo-1)
      - [Paquetes](#paquetes)
  - [Video demostración](#video-demostración)

# Documentación técnica

## Uso

- Instalación del paquete `tp`
    ```bash
    pip install -e .
    ```
    Testear la instalación con:
    ```bash
    tp --help
    ```

- Configuración del sistema (valores por defecto en [workers](cli/utils/workers.py))
    ```bash
    tp configure
    ```
    (Se puede verificar qué configuración aplicar con `tp configure --help`)

- Ejecución del sistema
    ```bash
    tp run --build
    ```
    (Se puede verificar qué imagen construir con `tp build --help`)

### Cliente

- Ejecución del cliente
    ```bash
    tp client --build
    ```

## Introducción

En este proyecto se busca crear un sistema distribuido que analice 6 meses de registros de precios de  vuelos de avión p/proponer mejoras en la oferta a clientes.

Los registros poseen trayectos (aeropuertos origen-destino), tarifa total,  distancia total, duración, cada segmento con escalas y aerolíneas.

Utilizando una arquitectura cliente-servidor, los registros se deben leer en el cliente, recibir en el servidor y procesar en diversos workers de manera que los mismos se puedan replicar y el sistema sea escalable. Además, se deben utilizar los middleware correspondientes para minimizar la pérdida de datos.

Se busca procesar las siguientes queries:

* ID, trayecto, precio y escalas de vuelos de 3 escalas o más.
* ID, trayecto y distancia total de vuelos cuya distancia total sea mayor a 
cuatro veces la distancia directa entre puntos origen-destino.
* ID, trayecto, escalas y duración de los 2 vuelos más rápidos para cada 
trayecto entre todos los vuelos de 3 escalas o más.
* El precio avg y max por trayecto de los vuelos con precio mayor a la 
media general de precios.

## Desarrollo

El proyecto posee un cliente, un servidor y ocho workers con capacidad de replicación. Estos se comunican a través de un Middleware, que puede utilizarse para el envío de mensajes con colas de la forma Producer-Subscriber (PS) o Producer-Consumer (PC).

Se utilizó el software RabbitMQ, creando Exchanges para los de tipo PS y Working Queues para los de tipo PC.

Además se implementó un cliente de ejemplo que se conecta al sistema a través del protocolo TCP, con un protocolo de mensajería que consiste en los registros separados por "\n" con cada valor dentro del registro separado por ";". Estos registros se envían de a batches, con un header y un body que consiste en el tamaño de cada batch seguido de los registros. El header es un string que denota el tipo de datos que se están enviando y cuando se terminan de enviar todos los datos se envía un "EOF" con un body de valor cero.

Los batches luego pasan por los middlewares y se van repartiendo a los workers para completar las queries necesarias. Cuando se van obteniendo resultados se los agrega a un middleware de resultados, que va devolviendo los mismos al servidor y a su vez este los manda al cliente.

Cuando el servidor recibe un mensaje de EOF debe propagarlo por todo el sistema. Esto se logra por un sistema de reencolamiento de los EOF, donde cada worker sabe las cantidad de réplicas que están levantadas y cuando recibe del middleware de upstream un EOF, cuando el valor del body es menor al de las réplicas, le suma un 1 al valor del body y lo reencola en el upstream. Luego, cierra la conexión con el upstream. Cuando llega a la última réplica, esta propaga el mensaje de EOF al downstream y cierra su conexión. Si el downstream es el middleware de results, entonces le agrega al body el nombre de la query que el worker estuvo resolviendo.

Así, el servidor cuenta los EOF que recibe con un body que tiene el nombre de una query y cuando obtuvo las cuatro queries envía al cliente un mensaje de EOF y cierra la conexión.

## DAG de la solución

![](docs/diagramas/DAG.png)

En este gŕafico se puede observar en forma de grafo el "camino" de los datos desde que se reciben en el servidor hasta que llegan a los resultados, luego de su correspondiente procesamiento. Cada nodo representa un worker, que procesa los datos recibidos y envía al siguiente worker los datos procesados. Finalmente, esos resultados convergen en un sink.


## Cómo correr el proyecto

- Instalación del paquete `tp`:
``` 
 pip install -e .
```

- Testear la instalación con:

```
tp --help
```   

- Configuración del sistema (valores por defecto en [workers](cli/utils/workers.py)):

```
tp configure
```
(Se puede verificar qué configuración aplicar con `tp configure --help`)

- Ejecución del sistema

```
tp run --build
```
    
(Se puede verificar qué imagen construir con `tp build --help`)

### Cliente

- Ejecución del cliente:
```
tp client --build
```

## Vistas

### Escenarios

![](docs/diagramas/casos_de_uso.png)

- Cargar Datos al Sistema:
  Permite al cliente cargar los datos al sistema para realizar consultas.
  - Precondiciones: _no hay_.
  - Flujo Básico:
    1) El cliente se conecta al servidor.
    2) El cliente envía los datos de aeropuertos e itinerarios al sistema.
- Consultar vuelos con muchas escalas _(Query 1)_
  Permite al cliente obtener información de los vuelos que tienen 3 o más escalas.
  - Precondiciones: Se realizó la carga de datos al sistema.
  - Postcondiciones: _no hay_.
- Consultar vuelos con distancia recorrida mayor a origen-destino _(Query 2)_
  Permite al cliente obtener información de los vuelos que tienen distancia recorrida 4 veces mayor o más a la distancia origen-destino.
  - Precondiciones: Se realizó la carga de datos al sistema.
  - Postcondiciones: _no hay_.
- Consultar vuelos más rápidos por tramo _(Query 3)_
  Permite al cliente obtener los 2 vuelos más rápidos (con menor tiempo) por cada tramo para aquellos vuelos con 3 o más escalas.
  - Precondiciones: Se realizó la carga de datos al sistema.
  - Postcondiciones: _no hay_.
- Consultar métricas de precios por trayecto _(Query 4)_
  Obtener, para los vuelos con precio mayor a la media, el valor medio y máximo de precio por cada trayecto.
  - Precondiciones: Se realizó la carga de datos al sistema.
  - Postcondiciones: _no hay_.

### Física

_[Volver al Indice](#indice)_

#### Despliegue

![](docs/diagramas/despliegue.png)

En este diagrama de despliegue se puede observar que se posee una instancia del Server, una del Middleware y múltiples workers. Tanto para el Server como para los workers se utiliza Docker y Python, y para el Middleware Docker y RabbitMQ.

#### Robustez

![](docs/diagramas/robustez.png)

En el diagrama de robustez se muestra la arquitectura del sistema, con instancias de servidor y workers, así como qué tipo de interfaz de middleware se está usando (PS o PC). Hay workers que están duplicados, lo que implica que se pueden instanciar réplicas de los mismos y hay dos workers que no se pueden replicar (_fastest_by_route_ y _price_by_route_). Se puede observar que este diagrama es prácticamente análogo al DAG, lo que tiene sentido ya que el sistema procesa datos de manera distribuída.

### Procesos

_[Volver al Indice](#indice)_

#### Actividad

![](docs/diagramas/actividad.png)

En este diagrama se muestra cómo los distintos nodos se comunican entre sí para completar la Query 4 (Obtener media y máximo de precio por tramo para los vuelos con precio mayor a la media general). El flujo de los datos pasa por un filtro general para luego dividirse en: un worker que calcula la media general y otro que sólo acumula precios agrupados por tramo (para luego ser filtrados por la media general). Finalmente el segundo de estos envía los valores filtrados a un último nodo que realiza la agregación final para luego enviar los resultados al servidor.

#### Secuencia

![](docs/diagramas/sequence.png)

Cuando un mensaje de fin arriba a un filter replicado, se compara el valor que acompaña el EOF para conocer si es el máximo posible (cantidad de réplicas de ese worker). En caso de que no sea el máximo el mensaje se envía a un filtro del mismo tipo, si no se envía al downstream correspondiente.

### Desarrollo

_[Volver al Indice](#indice)_

#### Paquetes

![](docs/diagramas/paquetes.png)

El diagrama de paquetes muestra la distribución del código. Se tiene un paquete server, al cual se accede por un main. Lo mismo sucede para el módulo de cada worker, que se crea con un _dynamic import_ que sirve para determinar por configuración qué worker se estará ejecutando. Además, se tiene un paquete 'lib' que publica otros módulos (`tcp`, `serde`, `config`, `logs`) con clases y funciones compartidas en todos los otros paquetes, y define configuraciones y protocolos de envío de mensajes. Finalmente, el módulo Middleware posee una clase abstracta `MiddlewareType`, lo que permite implementar el patrón de diseño Strategy para poder abstraerse del tipo de Middleware que se desea usar (Producer-Subscriber, Producer-Consumer o Publisher). Todos utilizan la librería externa Pika para conectarse con RabbitMQ.



## Video demostración

Video demostración del programa corriendo con todos los datos: https://www.youtube.com/watch?v=ygr7mpo0nO4&ab