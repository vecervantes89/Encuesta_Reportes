import psycopg2
import os
from datetime import datetime
import pandas as pd
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise Exception("DATABASE_URL no está configurada")
        self._inicializar_tablas()
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones a la base de datos"""
        conn = psycopg2.connect(self.database_url)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _inicializar_tablas(self):
        """Crear tablas si no existen"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla principal de encuestas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS encuestas (
                    id SERIAL PRIMARY KEY,
                    fecha_envio TIMESTAMP NOT NULL,
                    nombre_reporte VARCHAR(500) NOT NULL,
                    periodicidad_reporte VARCHAR(100),
                    sistema_origen VARCHAR(300) NOT NULL,
                    persona_responsable VARCHAR(300) NOT NULL,
                    email_responsable VARCHAR(300) NOT NULL,
                    auditoria_utilizacion TEXT,
                    periodicidad_auditoria VARCHAR(100),
                    departamento VARCHAR(200),
                    criticidad VARCHAR(50),
                    formato_entrega TEXT,
                    descripcion_reporte TEXT,
                    stakeholders TEXT,
                    automatizado VARCHAR(50),
                    observaciones TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de historial de cambios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_cambios (
                    id SERIAL PRIMARY KEY,
                    encuesta_id INTEGER REFERENCES encuestas(id) ON DELETE CASCADE,
                    campo_modificado VARCHAR(200),
                    valor_anterior TEXT,
                    valor_nuevo TEXT,
                    usuario_modificacion VARCHAR(300),
                    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    motivo_cambio TEXT
                )
            """)
            
            # Índices para mejorar rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_encuestas_departamento 
                ON encuestas(departamento)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_encuestas_criticidad 
                ON encuestas(criticidad)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_encuestas_fecha 
                ON encuestas(fecha_envio)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_historial_encuesta 
                ON historial_cambios(encuesta_id)
            """)
            
            conn.commit()
            cursor.close()
    
    def guardar_encuesta(self, datos_encuesta):
        """Guardar una nueva encuesta"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                INSERT INTO encuestas (
                    fecha_envio, nombre_reporte, periodicidad_reporte, 
                    sistema_origen, persona_responsable, email_responsable,
                    auditoria_utilizacion, periodicidad_auditoria, 
                    departamento, criticidad, formato_entrega,
                    descripcion_reporte, stakeholders, automatizado, observaciones
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """
            
            valores = (
                datos_encuesta.get("fecha_envio"),
                datos_encuesta.get("nombre_reporte"),
                datos_encuesta.get("periodicidad_reporte"),
                datos_encuesta.get("sistema_origen"),
                datos_encuesta.get("persona_responsable"),
                datos_encuesta.get("email_responsable"),
                datos_encuesta.get("auditoria_utilizacion"),
                datos_encuesta.get("periodicidad_auditoria"),
                datos_encuesta.get("departamento"),
                datos_encuesta.get("criticidad"),
                datos_encuesta.get("formato_entrega"),
                datos_encuesta.get("descripcion_reporte"),
                datos_encuesta.get("stakeholders"),
                datos_encuesta.get("automatizado"),
                datos_encuesta.get("observaciones")
            )
            
            cursor.execute(query, valores)
            encuesta_id = cursor.fetchone()[0]
            cursor.close()
            
            return encuesta_id
    
    def obtener_todas_encuestas(self):
        """Obtener todas las encuestas"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    id, fecha_envio, nombre_reporte, periodicidad_reporte,
                    sistema_origen, persona_responsable, email_responsable,
                    auditoria_utilizacion, periodicidad_auditoria,
                    departamento, criticidad, formato_entrega,
                    descripcion_reporte, stakeholders, automatizado, 
                    observaciones, created_at, updated_at
                FROM encuestas
                ORDER BY fecha_envio DESC
            """
            
            df = pd.read_sql_query(query, conn)
            return df
    
    def obtener_encuesta_por_id(self, encuesta_id):
        """Obtener una encuesta específica por ID"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    id, fecha_envio, nombre_reporte, periodicidad_reporte,
                    sistema_origen, persona_responsable, email_responsable,
                    auditoria_utilizacion, periodicidad_auditoria,
                    departamento, criticidad, formato_entrega,
                    descripcion_reporte, stakeholders, automatizado, 
                    observaciones, created_at, updated_at
                FROM encuestas
                WHERE id = %s
            """
            
            df = pd.read_sql_query(query, conn, params=(encuesta_id,))
            return df.iloc[0] if not df.empty else None
    
    def actualizar_encuesta(self, encuesta_id, datos_actualizados, usuario_modificacion="Sistema"):
        """Actualizar una encuesta existente y registrar historial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Obtener datos actuales
            encuesta_actual = self.obtener_encuesta_por_id(encuesta_id)
            
            if encuesta_actual is None:
                raise Exception(f"Encuesta con ID {encuesta_id} no encontrada")
            
            # Preparar campos a actualizar
            campos_actualizar = []
            valores = []
            
            for campo, valor_nuevo in datos_actualizados.items():
                if campo in encuesta_actual.index and campo not in ['id', 'created_at', 'updated_at']:
                    valor_anterior = str(encuesta_actual[campo]) if pd.notna(encuesta_actual[campo]) else ""
                    valor_nuevo_str = str(valor_nuevo) if valor_nuevo is not None else ""
                    
                    # Solo actualizar si el valor cambió
                    if valor_anterior != valor_nuevo_str:
                        campos_actualizar.append(f"{campo} = %s")
                        valores.append(valor_nuevo)
                        
                        # Registrar en historial
                        self._registrar_cambio(
                            cursor, encuesta_id, campo, 
                            valor_anterior, valor_nuevo_str, 
                            usuario_modificacion
                        )
            
            if campos_actualizar:
                # Actualizar timestamp
                campos_actualizar.append("updated_at = CURRENT_TIMESTAMP")
                
                # Construir y ejecutar query de actualización
                query = f"""
                    UPDATE encuestas 
                    SET {', '.join(campos_actualizar)}
                    WHERE id = %s
                """
                valores.append(encuesta_id)
                
                cursor.execute(query, valores)
                conn.commit()
            
            cursor.close()
            return True
    
    def _registrar_cambio(self, cursor, encuesta_id, campo, valor_anterior, 
                         valor_nuevo, usuario, motivo=""):
        """Registrar un cambio en el historial"""
        query = """
            INSERT INTO historial_cambios (
                encuesta_id, campo_modificado, valor_anterior, 
                valor_nuevo, usuario_modificacion, motivo_cambio
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            encuesta_id, campo, valor_anterior, 
            valor_nuevo, usuario, motivo
        ))
    
    def obtener_historial(self, encuesta_id):
        """Obtener historial de cambios de una encuesta"""
        with self.get_connection() as conn:
            query = """
                SELECT 
                    id, campo_modificado, valor_anterior, valor_nuevo,
                    usuario_modificacion, fecha_modificacion, motivo_cambio
                FROM historial_cambios
                WHERE encuesta_id = %s
                ORDER BY fecha_modificacion DESC
            """
            
            df = pd.read_sql_query(query, conn, params=(encuesta_id,))
            return df
    
    def eliminar_encuesta(self, encuesta_id):
        """Eliminar una encuesta (también elimina historial por CASCADE)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM encuestas WHERE id = %s", (encuesta_id,))
            conn.commit()
            cursor.close()
            return True
    
    def obtener_estadisticas(self):
        """Obtener estadísticas generales"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total de encuestas
            cursor.execute("SELECT COUNT(*) FROM encuestas")
            stats['total_encuestas'] = cursor.fetchone()[0]
            
            # Departamentos únicos
            cursor.execute("SELECT COUNT(DISTINCT departamento) FROM encuestas WHERE departamento IS NOT NULL")
            stats['departamentos_unicos'] = cursor.fetchone()[0]
            
            # Sistemas únicos
            cursor.execute("SELECT COUNT(DISTINCT sistema_origen) FROM encuestas WHERE sistema_origen IS NOT NULL")
            stats['sistemas_unicos'] = cursor.fetchone()[0]
            
            # Reportes críticos
            cursor.execute("SELECT COUNT(*) FROM encuestas WHERE criticidad = 'Alto'")
            stats['reportes_criticos'] = cursor.fetchone()[0]
            
            # Reportes automatizados
            cursor.execute("SELECT COUNT(*) FROM encuestas WHERE automatizado = 'Sí'")
            stats['reportes_automatizados'] = cursor.fetchone()[0]
            
            cursor.close()
            return stats
    
    def migrar_desde_csv(self, csv_file):
        """Migrar datos desde CSV existente a PostgreSQL"""
        try:
            if not os.path.exists(csv_file):
                return 0
            
            df = pd.read_csv(csv_file, encoding='utf-8')
            migrados = 0
            
            for _, row in df.iterrows():
                datos_encuesta = {
                    "fecha_envio": row.get("fecha_envio"),
                    "nombre_reporte": row.get("nombre_reporte"),
                    "periodicidad_reporte": row.get("periodicidad_reporte"),
                    "sistema_origen": row.get("sistema_origen"),
                    "persona_responsable": row.get("persona_responsable"),
                    "email_responsable": row.get("email_responsable"),
                    "auditoria_utilizacion": row.get("auditoria_utilizacion"),
                    "periodicidad_auditoria": row.get("periodicidad_auditoria"),
                    "departamento": row.get("departamento"),
                    "criticidad": row.get("criticidad"),
                    "formato_entrega": row.get("formato_entrega"),
                    "descripcion_reporte": row.get("descripcion_reporte"),
                    "stakeholders": row.get("stakeholders"),
                    "automatizado": row.get("automatizado"),
                    "observaciones": row.get("observaciones")
                }
                
                self.guardar_encuesta(datos_encuesta)
                migrados += 1
            
            return migrados
            
        except Exception as e:
            print(f"Error en migración: {str(e)}")
            return 0
