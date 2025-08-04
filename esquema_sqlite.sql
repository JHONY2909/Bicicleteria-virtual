-- Crear las tablas para la base de datos en SQLite

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    contrasena TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    telefono TEXT,
    rol TEXT NOT NULL CHECK(rol IN ('administrador', 'cliente', 'vendedor')) DEFAULT 'cliente',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de categorías
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT
);

-- Tabla de productos
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL,
    categoria_id INTEGER,
    url_imagen TEXT,
    estado TEXT CHECK(estado IN ('activo', 'inactivo')) DEFAULT 'activo',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- Tabla de direcciones
CREATE TABLE direcciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    direccion TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    codigo_postal TEXT,
    pais TEXT NOT NULL,
    telefono_contacto TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de pedidos
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    direccion_id INTEGER,
    monto_total DECIMAL(10, 2) NOT NULL,
    metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('tarjeta', 'transferencia', 'efectivo', 'otro')),
    estado TEXT CHECK(estado IN ('pendiente', 'pagado', 'enviado', 'entregado', 'cancelado')) DEFAULT 'pendiente',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (direccion_id) REFERENCES direcciones(id)
);

-- Tabla de detalles de pedidos
CREATE TABLE detalles_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Tabla de facturas
CREATE TABLE facturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER,
    numero_factura TEXT NOT NULL UNIQUE,
    fecha_emision DATETIME DEFAULT CURRENT_TIMESTAMP,
    monto_total DECIMAL(10, 2) NOT NULL,
    estado TEXT CHECK(estado IN ('emitida', 'pagada', 'anulada')) DEFAULT 'emitida',
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
);

-- Tabla de reseñas
CREATE TABLE resenas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER,
    usuario_id INTEGER,
    calificacion INTEGER NOT NULL CHECK(calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Tabla de carrito
CREATE TABLE carrito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    producto_id INTEGER,
    cantidad INTEGER NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Insertar usuarios iniciales (ejemplo)
-- Nota: Reemplaza 'hashed_password_here' con contraseñas hasheadas
INSERT INTO usuarios (nombre_usuario, contrasena, correo, rol) 
VALUES ('admin', 'pbkdf2:sha256:1000000$EnAOpJdhsAVi2bqw$e3ec8422ebd96e806a3a66054a5b3ec8a5f02ee281fc05e0436347b1c98b09d8', 'admin@bicicleteria.com', 'administrador'),
       ('cliente1', 'pbkdf2:sha256:1000000$1GUy6AX0xQXMWtM3$f614d6e48e9d594ff6f5e670d50e58e1563a292c8352088c01a7d5f1a285f058', 'cliente1@bicicleteria.com', 'cliente'),
       ('vendedor1', 'pbkdf2:sha256:1000000$GobQzrNMPnAhzJtq$88acfdd0f3b37743afc622ac25dbd44371dd1bbe0fbf02cb3c1fb974b7f61c3d', 'vendedor1@bicicleteria.com', 'vendedor');