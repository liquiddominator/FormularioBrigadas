from flask import Flask, render_template_string, request, redirect, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# ========================
# CREAR BASE DE DATOS
# ========================
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()

    # Eliminar tablas existentes para recrearlas correctamente
    cursor.executescript("""
    DROP TABLE IF EXISTS Costos;
    DROP TABLE IF EXISTS Logistica;
    DROP TABLE IF EXISTS Equipos;
    DROP TABLE IF EXISTS TallasRopa;
    
    CREATE TABLE IF NOT EXISTS Brigadas (
        ID_Brigada INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombre_Brigada TEXT NOT NULL,
        Cant_Bomberos INTEGER,
        Cel_Comandante TEXT,
        Encargado_Logistica TEXT,
        Cel_Logistica TEXT,
        Nro_Emergencia TEXT
    );

    CREATE TABLE IF NOT EXISTS TallasRopa (
        ID_Talla INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Brigada INTEGER NOT NULL,
        Tipo_Ropa TEXT NOT NULL,
        Talla_XS INTEGER DEFAULT 0,
        Talla_S INTEGER DEFAULT 0,
        Talla_M INTEGER DEFAULT 0,
        Talla_L INTEGER DEFAULT 0,
        Talla_XL INTEGER DEFAULT 0,
        Observaciones TEXT,
        FOREIGN KEY (ID_Brigada) REFERENCES Brigadas(ID_Brigada)
    );

    CREATE TABLE IF NOT EXISTS Equipos (
        ID_Equipo INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Brigada INTEGER NOT NULL,
        Categoria_Equipo TEXT NOT NULL,
        Nombre_Articulo TEXT NOT NULL,
        Cantidad INTEGER DEFAULT 0,
        Observacion TEXT,
        FOREIGN KEY (ID_Brigada) REFERENCES Brigadas(ID_Brigada)
    );

    CREATE TABLE IF NOT EXISTS Logistica (
        ID_Logistica INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Brigada INTEGER NOT NULL,
        Nombre TEXT NOT NULL,
        Costo_Unitario REAL DEFAULT 0,
        Observaciones TEXT,
        FOREIGN KEY (ID_Brigada) REFERENCES Brigadas(ID_Brigada)
    );
    """)
    conn.commit()
    conn.close()

init_db()

# ========================
# PÁGINA PRINCIPAL - LISTADO DE BRIGADAS
# ========================
@app.route("/")
def index():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Brigadas ORDER BY ID_Brigada DESC")
    brigadas = cursor.fetchall()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Brigadas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d32f2f; text-align: center; margin-bottom: 30px; }
            h2 { color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 5px; }
            .form-section { background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #1976d2; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            input[type="text"], input[type="number"], select { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
            button { background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
            button:hover { background-color: #45a049; }
            .btn-secondary { background-color: #2196F3; }
            .btn-secondary:hover { background-color: #1976D2; }
            .success-message { color: #4CAF50; background: #e8f5e8; padding: 10px; border-radius: 4px; margin: 10px 0; }
            .nav-links { text-align: center; margin: 20px 0; }
            .nav-links a { text-decoration: none; background: #2196F3; color: white; padding: 10px 15px; border-radius: 4px; margin: 0 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚒 Sistema de Gestión de Brigadas</h1>
            
            {% with messages = get_flashed_messages() %}
                {% if messages %}
                    {% for message in messages %}
                        <div class="success-message">✅ {{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}

            <div class="form-section">
                <h2>➕ Crear Nueva Brigada</h2>
                <form method="POST" action="/crear_brigada">
                    <table>
                        <tr>
                            <td><strong>Nombre Brigada:</strong></td>
                            <td><input type="text" name="nombre_brigada" required placeholder="Ingrese nombre de la brigada"></td>
                        </tr>
                        <tr>
                            <td><strong>Cantidad Bomberos:</strong></td>
                            <td><input type="number" name="cant_bomberos" placeholder="Número de bomberos"></td>
                        </tr>
                        <tr>
                            <td><strong>Celular Comandante:</strong></td>
                            <td><input type="text" name="cel_comandante" placeholder="Número de celular"></td>
                        </tr>
                        <tr>
                            <td><strong>Encargado Logística:</strong></td>
                            <td><input type="text" name="encargado_logistica" placeholder="Nombre del encargado"></td>
                        </tr>
                        <tr>
                            <td><strong>Celular Logística:</strong></td>
                            <td><input type="text" name="cel_logistica" placeholder="Número de celular"></td>
                        </tr>
                        <tr>
                            <td><strong>Número Emergencia:</strong></td>
                            <td><input type="text" name="nro_emergencia" placeholder="Número de emergencia"></td>
                        </tr>
                        <tr>
                            <td colspan="2" style="text-align: center;">
                                <button type="submit">🆕 Crear Brigada</button>
                            </td>
                        </tr>
                    </table>
                </form>
            </div>

            <div class="nav-links">
                <a href="/ver_todas">📋 Ver Todas las Brigadas con sus Artículos</a>
            </div>
            
            <h2>📋 Brigadas Existentes</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Nombre Brigada</th>
                    <th>N° Bomberos</th>
                    <th>Cel. Comandante</th>
                    <th>Encargado Logística</th>
                    <th>Cel. Logística</th>
                    <th>N° Emergencia</th>
                    <th>Acciones</th>
                </tr>
                {% for brigada in brigadas %}
                <tr>
                    <td><strong>{{ brigada[0] }}</strong></td>
                    <td>{{ brigada[1] }}</td>
                    <td>{{ brigada[2] or 'N/A' }}</td>
                    <td>{{ brigada[3] or 'N/A' }}</td>
                    <td>{{ brigada[4] or 'N/A' }}</td>
                    <td>{{ brigada[5] or 'N/A' }}</td>
                    <td>{{ brigada[6] or 'N/A' }}</td>
                    <td>
                        <a href="/brigada/{{ brigada[0] }}" 
                            style="text-decoration: none; background: #FF9800; color: white; padding: 5px 10px; border-radius: 3px; margin-right: 5px;">
                            ⚙️ Gestionar
                        </a>

                        <form action="/eliminar_brigada/{{ brigada[0] }}" method="POST" style="display:inline;">
                            <button type="submit" 
                                style="background: #F44336; color: white; padding: 5px 10px; border: none; border-radius: 3px; cursor: pointer;"
                                onclick="return confirm('¿Seguro que deseas eliminar esta brigada?');">
                                🗑️ Eliminar
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """, brigadas=brigadas)

# ========================
# CREAR BRIGADA
# ========================
@app.route("/crear_brigada", methods=["POST"])
def crear_brigada():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Brigadas (Nombre_Brigada, Cant_Bomberos, Cel_Comandante, Encargado_Logistica, Cel_Logistica, Nro_Emergencia)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form['nombre_brigada'],
        request.form['cant_bomberos'],
        request.form['cel_comandante'],
        request.form['encargado_logistica'],
        request.form['cel_logistica'],
        request.form['nro_emergencia']
    ))
    conn.commit()
    conn.close()
    flash('Brigada creada exitosamente!')
    return redirect("/")

# ========================
# GESTIÓN DE BRIGADA INDIVIDUAL
# ========================
@app.route("/brigada/<int:brigada_id>")
def gestionar_brigada(brigada_id):
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    
    # Obtener datos de la brigada
    cursor.execute("SELECT * FROM Brigadas WHERE ID_Brigada = ?", (brigada_id,))
    brigada = cursor.fetchone()
    
    # Obtener tallas
    cursor.execute("SELECT * FROM TallasRopa WHERE ID_Brigada = ?", (brigada_id,))
    tallas = cursor.fetchall()
    
    # Obtener equipos
    cursor.execute("SELECT * FROM Equipos WHERE ID_Brigada = ?", (brigada_id,))
    equipos = cursor.fetchall()
    
    # Obtener logística
    cursor.execute("SELECT * FROM Logistica WHERE ID_Brigada = ?", (brigada_id,))
    logistica = cursor.fetchall()
    
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gestionar Brigada - {{ brigada[1] }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d32f2f; text-align: center; margin-bottom: 30px; }
            h2 { color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 5px; margin-top: 30px; }
            h3 { color: #388e3c; }
            .form-section { background: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #e0e0e0; }
            table { width: 100%; border-collapse: collapse; margin: 10px 0; }
            th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #1976d2; color: white; font-size: 12px; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            input[type="text"], input[type="number"], select { width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px; font-size: 12px; }
            button { background-color: #4CAF50; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; margin: 2px; }
            button:hover { background-color: #45a049; }
            .btn-delete { background-color: #F44336 !important; padding: 4px 8px !important; font-size: 10px !important; }
            .btn-delete:hover { background-color: #d32f2f !important; }
            .back-btn { background-color: #9E9E9E; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
            .back-btn:hover { background-color: #757575; }
            .section-grid { display: flex; flex-wrap: wrap; gap: 20px; }
            .section-item { flex: 1; min-width: 300px; }
            .success { color: #4CAF50; font-weight: bold; }
            .error { color: #f44336; font-weight: bold; }
        </style>
        <script>
            function agregarTalla() {
                var form = document.getElementById('form-talla');
                var formData = new FormData(form);
                
                fetch('/agregar_talla', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    if (data === 'OK') {
                        location.reload();
                    } else {
                        alert('Error al agregar talla');
                    }
                });
            }
            
            function agregarEquipo() {
                var form = document.getElementById('form-equipo');
                var formData = new FormData(form);
                
                fetch('/agregar_equipo', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    if (data === 'OK') {
                        location.reload();
                    } else {
                        alert('Error al agregar equipo');
                    }
                });
            }
            
            function agregarLogistica() {
                var form = document.getElementById('form-logistica');
                var formData = new FormData(form);
                
                fetch('/agregar_logistica', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(data => {
                    if (data === 'OK') {
                        location.reload();
                    } else {
                        alert('Error al agregar logística');
                    }
                });
            }
            
            function eliminarRegistro(tipo, id) {
                if (confirm('¿Seguro que deseas eliminar este registro?')) {
                    fetch(`/eliminar_${tipo}/${id}`, {
                        method: 'POST'
                    })
                    .then(response => response.text())
                    .then(data => {
                        if (data === 'OK') {
                            location.reload();
                        } else {
                            alert('Error al eliminar el registro');
                        }
                    })
                    .catch(error => {
                        alert('Error al eliminar el registro');
                    });
                }
            }
        </script>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">🔙 Volver a Brigadas</a>
            
            <h1>⚙️ Gestionar: {{ brigada[1] }}</h1>
            
            <div class="section-grid">
                <!-- SECCIÓN TALLAS -->
                <div class="section-item">
                    <div class="form-section">
                        <h2>👕 Agregar Talla de Ropa</h2>
                        <form id="form-talla" onsubmit="event.preventDefault(); agregarTalla();">
                            <input type="hidden" name="brigada_id" value="{{ brigada[0] }}">
                            <table>
                                <tr>
                                    <td><strong>Tipo de Ropa:</strong></td>
                                    <td colspan="5"><input type="text" name="tipo_ropa" required placeholder="Ej: Camiseta, Pantalón, etc."></td>
                                </tr>
                                <tr style="background-color: #e3f2fd;">
                                    <td><strong>XS:</strong></td><td><input type="number" name="talla_xs" value="0" min="0"></td>
                                    <td><strong>S:</strong></td><td><input type="number" name="talla_s" value="0" min="0"></td>
                                    <td><strong>M:</strong></td><td><input type="number" name="talla_m" value="0" min="0"></td>
                                </tr>
                                <tr style="background-color: #e3f2fd;">
                                    <td><strong>L:</strong></td><td><input type="number" name="talla_l" value="0" min="0"></td>
                                    <td><strong>XL:</strong></td><td><input type="number" name="talla_xl" value="0" min="0"></td>
                                    <td><strong>Observaciones:</strong></td><td><input type="text" name="observaciones" placeholder="Opcional"></td>
                                </tr>
                                <tr>
                                    <td colspan="6" style="text-align: center;"><button type="submit">➕ Agregar Talla</button></td>
                                </tr>
                            </table>
                        </form>
                    </div>

                    <h3>📋 Tallas Registradas</h3>
                    <table>
                        <tr>
                            <th>ID</th><th>Tipo</th><th>XS</th><th>S</th><th>M</th><th>L</th><th>XL</th><th>Observaciones</th><th>Acción</th>
                        </tr>
                        {% for talla in tallas %}
                        <tr>
                            <td>{{ talla[0] }}</td><td><strong>{{ talla[2] }}</strong></td><td>{{ talla[3] }}</td><td>{{ talla[4] }}</td>
                            <td>{{ talla[5] }}</td><td>{{ talla[6] }}</td><td>{{ talla[7] }}</td><td>{{ talla[8] or 'N/A' }}</td>
                            <td>
                                <button class="btn-delete" onclick="eliminarRegistro('talla', {{ talla[0] }})">
                                    🗑️
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>

                <!-- SECCIÓN EQUIPOS -->
                <div class="section-item">
                    <div class="form-section">
                        <h2>🛠️ Agregar Equipo/Artículo</h2>
                        <form id="form-equipo" onsubmit="event.preventDefault(); agregarEquipo();">
                            <input type="hidden" name="brigada_id" value="{{ brigada[0] }}">
                            <table>
                                <tr>
                                    <td><strong>Categoría:</strong></td>
                                    <td>
                                        <select name="categoria_equipo" required>
                                            <option value="">-- Seleccione Categoría --</option>
                                            <option value="EQUIPAMIENTO EPP">EQUIPAMIENTO EPP</option>
                                            <option value="HERRAMIENTAS">HERRAMIENTAS</option>
                                            <option value="ALIMENTACION Y BEBIDAS">ALIMENTACIÓN Y BEBIDAS</option>
                                            <option value="LOGISTICA Y EQUIPO DE CAMPO">LOGÍSTICA Y EQUIPO DE CAMPO</option>
                                            <option value="LIMPIEZA PERSONAL">LIMPIEZA PERSONAL</option>
                                            <option value="LIMPIEZA GENERAL">LIMPIEZA GENERAL</option>
                                            <option value="MEDICAMENTOS">MEDICAMENTOS</option>
                                            <option value="RESCATE ANIMAL">RESCATE ANIMAL</option>
                                        </select>
                                    </td>
                                </tr>
                                <tr>
                                    <td><strong>Nombre del Artículo:</strong></td>
                                    <td><input type="text" name="nombre_articulo" required placeholder="Ej: Casco, Guantes, Botiquín, etc."></td>
                                </tr>
                                <tr>
                                    <td><strong>Cantidad:</strong></td>
                                    <td><input type="number" name="cantidad" value="1" min="0"></td>
                                </tr>
                                <tr>
                                    <td><strong>Observaciones:</strong></td>
                                    <td><input type="text" name="observacion" placeholder="Detalles adicionales (opcional)"></td>
                                </tr>
                                <tr>
                                    <td colspan="2" style="text-align: center;"><button type="submit">➕ Agregar Equipo</button></td>
                                </tr>
                            </table>
                        </form>
                    </div>

                    <h3>📋 Equipos Registrados</h3>
                    <table>
                        <tr>
                            <th>ID</th><th>Categoría</th><th>Artículo</th><th>Cantidad</th><th>Observación</th><th>Acción</th>
                        </tr>
                        {% for equipo in equipos %}
                        <tr>
                            <td>{{ equipo[0] }}</td>
                            <td><span style="background: #e1f5fe; padding: 2px 6px; border-radius: 3px; font-size: 11px;"><strong>{{ equipo[2] }}</strong></span></td>
                            <td><strong>{{ equipo[3] }}</strong></td>
                            <td><span style="background: #c8e6c9; padding: 2px 6px; border-radius: 3px;"><strong>{{ equipo[4] }}</strong></span></td>
                            <td>{{ equipo[5] or 'N/A' }}</td>
                            <td>
                                <button class="btn-delete" onclick="eliminarRegistro('equipo', {{ equipo[0] }})">
                                    🗑️
                                </button>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </div>

            <!-- SECCIÓN LOGÍSTICA -->
            <div class="form-section">
                <h2>📦 Agregar Logística</h2>
                <form id="form-logistica" onsubmit="event.preventDefault(); agregarLogistica();">
                    <input type="hidden" name="brigada_id" value="{{ brigada[0] }}">
                    <table>
                        <tr>
                            <td><strong>Nombre:</strong></td>
                            <td><input type="text" name="nombre" required placeholder="Nombre del item logístico"></td>
                        </tr>
                        <tr>
                            <td><strong>Costo Unitario ($):</strong></td>
                            <td><input type="number" step="0.01" name="costo_unitario" value="0" min="0" placeholder="0.00"></td>
                        </tr>
                        <tr>
                            <td><strong>Observaciones:</strong></td>
                            <td><input type="text" name="observaciones" placeholder="Detalles adicionales (opcional)"></td>
                        </tr>
                        <tr>
                            <td colspan="2" style="text-align: center;"><button type="submit">➕ Agregar Logística</button></td>
                        </tr>
                    </table>
                </form>
            </div>

            <h3>📋 Logística Registrada</h3>
            <table>
                <tr>
                    <th>ID</th><th>Nombre</th><th>Costo Unitario</th><th>Observaciones</th><th>Acción</th>
                </tr>
                {% for item in logistica %}
                <tr>
                    <td>{{ item[0] }}</td><td><strong>{{ item[2] }}</strong></td>
                    <td><span style="background: #fff3e0; padding: 2px 6px; border-radius: 3px;"><strong>${{ "%.2f"|format(item[3] or 0) }}</strong></span></td>
                    <td>{{ item[4] or 'N/A' }}</td>
                    <td>
                        <button class="btn-delete" onclick="eliminarRegistro('logistica', {{ item[0] }})">
                            🗑️
                        </button>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """, brigada=brigada, tallas=tallas, equipos=equipos, logistica=logistica)

# ========================
# ELIMINAR BRIGADA (CORREGIDO)
# ========================
@app.route('/eliminar_brigada/<int:id>', methods=['POST'])
def eliminar_brigada(id):
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM TallasRopa WHERE ID_Brigada = ?", (id,))
    cursor.execute("DELETE FROM Equipos WHERE ID_Brigada = ?", (id,))
    cursor.execute("DELETE FROM Logistica WHERE ID_Brigada = ?", (id,))
    
    # Luego eliminar la brigada principal
    cursor.execute("DELETE FROM Brigadas WHERE ID_Brigada = ?", (id,))
    
    conn.commit()
    conn.close()
    
    flash("Brigada eliminada correctamente", "success")
    return redirect('/')

# ========================
# NUEVAS RUTAS PARA ELIMINAR REGISTROS INDIVIDUALES
# ========================
@app.route('/eliminar_talla/<int:id>', methods=['POST'])
def eliminar_talla(id):
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TallasRopa WHERE ID_Talla = ?", (id,))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

@app.route('/eliminar_equipo/<int:id>', methods=['POST'])
def eliminar_equipo(id):
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Equipos WHERE ID_Equipo = ?", (id,))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

@app.route('/eliminar_logistica/<int:id>', methods=['POST'])
def eliminar_logistica(id):
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Logistica WHERE ID_Logistica = ?", (id,))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# AGREGAR TALLA (AJAX)
# ========================
@app.route("/agregar_talla", methods=["POST"])
def agregar_talla():
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO TallasRopa (ID_Brigada, Tipo_Ropa, Talla_XS, Talla_S, Talla_M, Talla_L, Talla_XL, Observaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form['brigada_id'],
            request.form['tipo_ropa'],
            request.form['talla_xs'] or 0,
            request.form['talla_s'] or 0,
            request.form['talla_m'] or 0,
            request.form['talla_l'] or 0,
            request.form['talla_xl'] or 0,
            request.form['observaciones']
        ))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# AGREGAR EQUIPO (AJAX)
# ========================
@app.route("/agregar_equipo", methods=["POST"])
def agregar_equipo():
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Equipos (ID_Brigada, Categoria_Equipo, Nombre_Articulo, Cantidad, Observacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form['brigada_id'],
            request.form['categoria_equipo'],
            request.form['nombre_articulo'],
            request.form['cantidad'] or 0,
            request.form['observacion']
        ))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# AGREGAR LOGÍSTICA (AJAX)
# ========================
@app.route("/agregar_logistica", methods=["POST"])
def agregar_logistica():
    try:
        conn = sqlite3.connect('datos.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Logistica (ID_Brigada, Nombre, Costo_Unitario, Observaciones)
            VALUES (?, ?, ?, ?)
        """, (
            request.form['brigada_id'],
            request.form['nombre'],
            request.form['costo_unitario'] or 0,
            request.form['observaciones']
        ))
        conn.commit()
        conn.close()
        return "OK"
    except:
        return "ERROR"

# ========================
# VER TODAS LAS BRIGADAS CON SUS ARTÍCULOS
# ========================
@app.route("/ver_todas")
def ver_todas():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Brigadas")
    brigadas = cursor.fetchall()

    cursor.execute("""
        SELECT t.*, b.Nombre_Brigada
        FROM TallasRopa t
        JOIN Brigadas b ON t.ID_Brigada = b.ID_Brigada
        ORDER BY b.Nombre_Brigada, t.Tipo_Ropa
    """)
    tallas = cursor.fetchall()

    cursor.execute("""
        SELECT e.*, b.Nombre_Brigada
        FROM Equipos e
        JOIN Brigadas b ON e.ID_Brigada = b.ID_Brigada
        ORDER BY b.Nombre_Brigada, e.Categoria_Equipo, e.Nombre_Articulo
    """)
    equipos = cursor.fetchall()

    cursor.execute("""
        SELECT l.*, b.Nombre_Brigada
        FROM Logistica l
        JOIN Brigadas b ON l.ID_Brigada = b.ID_Brigada
        ORDER BY b.Nombre_Brigada, l.Nombre
    """)
    logistica = cursor.fetchall()

    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Todas las Brigadas - Reporte Completo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #d32f2f; text-align: center; margin-bottom: 30px; }
            h2 { color: #1976d2; border-bottom: 2px solid #1976d2; padding-bottom: 5px; margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 12px; }
            th, td { padding: 8px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #1976d2; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            .back-btn { background-color: #9E9E9E; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; display: inline-block; margin-bottom: 20px; }
            .back-btn:hover { background-color: #757575; }
            .categoria { background: #e1f5fe; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
            .cantidad { background: #c8e6c9; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
            .costo { background: #fff3e0; padding: 2px 6px; border-radius: 3px; font-weight: bold; }
            .print-btn { background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px; margin-left: 10px; }
            @media print { .no-print { display: none; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="no-print">
                <a href="/" class="back-btn">🔙 Volver a Brigadas</a>
                <a href="javascript:window.print()" class="print-btn">🖨️ Imprimir Reporte</a>
            </div>
            
            <h1>📋 Reporte Completo - Todas las Brigadas</h1>

            <h2>🚒 Información General de Brigadas</h2>
            <table>
                <tr>
                    <th>ID</th><th>Nombre Brigada</th><th>N° Bomberos</th><th>Cel. Comandante</th>
                    <th>Encargado Logística</th><th>Cel. Logística</th><th>N° Emergencia</th>
                </tr>
                {% for brigada in brigadas %}
                <tr>
                    <td><strong>{{ brigada[0] }}</strong></td><td><strong>{{ brigada[1] }}</strong></td><td>{{ brigada[2] or 'N/A' }}</td>
                    <td>{{ brigada[3] or 'N/A' }}</td><td>{{ brigada[4] or 'N/A' }}</td>
                    <td>{{ brigada[5] or 'N/A' }}</td><td>{{ brigada[6] or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </table>

            <h2>👕 Inventario de Tallas por Brigada</h2>
            <table>
                <tr>
                    <th>Brigada</th><th>Tipo Ropa</th><th>XS</th><th>S</th><th>M</th><th>L</th><th>XL</th><th>Total</th><th>Observaciones</th>
                </tr>
                {% for talla in tallas %}
                <tr>
                    <td><strong>{{ talla[9] }}</strong></td><td><strong>{{ talla[2] }}</strong></td>
                    <td>{{ talla[3] }}</td><td>{{ talla[4] }}</td><td>{{ talla[5] }}</td>
                    <td>{{ talla[6] }}</td><td>{{ talla[7] }}</td>
                    <td class="cantidad">{{ talla[3] + talla[4] + talla[5] + talla[6] + talla[7] }}</td>
                    <td>{{ talla[8] or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </table>

            <h2>🛠️ Inventario de Equipos y Artículos por Brigada</h2>
            <table>
                <tr>
                    <th>Brigada</th><th>Categoría</th><th>Nombre Artículo</th><th>Cantidad</th><th>Observación</th>
                </tr>
                {% for equipo in equipos %}
                <tr>
                    <td><strong>{{ equipo[6] }}</strong></td>
                    <td><span class="categoria">{{ equipo[2] }}</span></td>
                    <td><strong>{{ equipo[3] }}</strong></td>
                    <td><span class="cantidad">{{ equipo[4] }}</span></td>
                    <td>{{ equipo[5] or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </table>

            <h2>📦 Inventario de Logística por Brigada</h2>
            <table>
                <tr>
                    <th>Brigada</th><th>Nombre</th><th>Costo Unitario</th><th>Observaciones</th>
                </tr>
                {% for item in logistica %}
                <tr>
                    <td><strong>{{ item[5] }}</strong></td><td><strong>{{ item[2] }}</strong></td>
                    <td><span class="costo">${{ "%.2f"|format(item[3] or 0) }}</span></td><td>{{ item[4] or 'N/A' }}</td>
                </tr>
                {% endfor %}
            </table>

            <div class="no-print" style="text-align: center; margin-top: 30px;">
                <p><em>Reporte generado automáticamente por el Sistema de Gestión de Brigadas</em></p>
            </div>
        </div>
    </body>
    </html>
    """, brigadas=brigadas, tallas=tallas, equipos=equipos, logistica=logistica)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)