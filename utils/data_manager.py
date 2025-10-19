import pandas as pd
import os
from datetime import datetime
from utils.database import Database

class DataManager:
    def __init__(self):
        self.data_file = "encuestas_reportes.csv"
        self.backup_dir = "backups"
        
        # Inicializar base de datos PostgreSQL
        try:
            self.db = Database()
            self.usar_database = True
            
            # Migrar datos de CSV si existe y la DB está vacía
            self._migrar_csv_a_db_si_necesario()
            
        except Exception as e:
            print(f"Advertencia: No se pudo conectar a PostgreSQL: {str(e)}")
            print("Usando almacenamiento CSV como respaldo")
            self.usar_database = False
            self._crear_directorio_backups()
            self._inicializar_archivo_datos()
    
    def _migrar_csv_a_db_si_necesario(self):
        """Migrar datos de CSV a PostgreSQL si la DB está vacía"""
        try:
            if os.path.exists(self.data_file):
                stats = self.db.obtener_estadisticas()
                if stats.get('total_encuestas', 0) == 0:
                    print("Migrando datos de CSV a PostgreSQL...")
                    migrados = self.db.migrar_desde_csv(self.data_file)
                    if migrados > 0:
                        print(f"✓ {migrados} encuestas migradas exitosamente")
                        # Hacer backup del CSV original
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        backup_file = f"{self.data_file}.migrado_{timestamp}.bak"
                        import shutil
                        shutil.copy2(self.data_file, backup_file)
        except Exception as e:
            print(f"Error en migración automática: {str(e)}")
    
    def _crear_directorio_backups(self):
        """Crear directorio de backups si no existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def _inicializar_archivo_datos(self):
        """Crear archivo CSV con headers si no existe (modo fallback)"""
        if not os.path.exists(self.data_file):
            headers = [
                "fecha_envio",
                "nombre_reporte", 
                "periodicidad_reporte",
                "sistema_origen",
                "persona_responsable",
                "email_responsable",
                "auditoria_utilizacion",
                "periodicidad_auditoria",
                "departamento",
                "criticidad",
                "formato_entrega",
                "descripcion_reporte",
                "stakeholders",
                "automatizado",
                "observaciones"
            ]
            
            import csv
            with open(self.data_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
    
    def guardar_respuesta(self, datos_encuesta):
        """Guardar una nueva respuesta de encuesta"""
        try:
            if self.usar_database:
                # Guardar en PostgreSQL
                encuesta_id = self.db.guardar_encuesta(datos_encuesta)
                return encuesta_id
            else:
                # Fallback a CSV
                return self._guardar_en_csv(datos_encuesta)
                
        except Exception as e:
            raise Exception(f"Error al guardar los datos: {str(e)}")
    
    def _guardar_en_csv(self, datos_encuesta):
        """Método de respaldo para guardar en CSV"""
        import csv
        self._crear_backup()
        
        row_data = [
            datos_encuesta.get("fecha_envio", ""),
            datos_encuesta.get("nombre_reporte", ""),
            datos_encuesta.get("periodicidad_reporte", ""),
            datos_encuesta.get("sistema_origen", ""),
            datos_encuesta.get("persona_responsable", ""),
            datos_encuesta.get("email_responsable", ""),
            datos_encuesta.get("auditoria_utilizacion", ""),
            datos_encuesta.get("periodicidad_auditoria", ""),
            datos_encuesta.get("departamento", ""),
            datos_encuesta.get("criticidad", ""),
            datos_encuesta.get("formato_entrega", ""),
            datos_encuesta.get("descripcion_reporte", ""),
            datos_encuesta.get("stakeholders", ""),
            datos_encuesta.get("automatizado", ""),
            datos_encuesta.get("observaciones", "")
        ]
        
        with open(self.data_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(row_data)
        
        return True
    
    def cargar_datos(self):
        """Cargar todos los datos"""
        try:
            if self.usar_database:
                # Cargar desde PostgreSQL
                df = self.db.obtener_todas_encuestas()
                return df
            else:
                # Fallback a CSV
                return self._cargar_desde_csv()
                
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            return pd.DataFrame()
    
    def _cargar_desde_csv(self):
        """Método de respaldo para cargar desde CSV"""
        try:
            if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
                df = pd.read_csv(self.data_file, encoding='utf-8')
                return df
            else:
                return pd.DataFrame(columns=[
                    "fecha_envio", "nombre_reporte", "periodicidad_reporte",
                    "sistema_origen", "persona_responsable", "email_responsable",
                    "auditoria_utilizacion", "periodicidad_auditoria", 
                    "departamento", "criticidad", "formato_entrega",
                    "descripcion_reporte", "stakeholders", "automatizado", "observaciones"
                ])
        except Exception as e:
            print(f"Error al cargar desde CSV: {str(e)}")
            return pd.DataFrame()
    
    def obtener_total_respuestas(self):
        """Obtener el número total de respuestas"""
        try:
            if self.usar_database:
                stats = self.db.obtener_estadisticas()
                return stats.get('total_encuestas', 0)
            else:
                df = self.cargar_datos()
                return len(df)
        except:
            return 0
    
    def obtener_encuesta_por_id(self, encuesta_id):
        """Obtener una encuesta específica por ID"""
        if self.usar_database:
            return self.db.obtener_encuesta_por_id(encuesta_id)
        else:
            return None
    
    def actualizar_encuesta(self, encuesta_id, datos_actualizados, usuario="Sistema"):
        """Actualizar una encuesta existente"""
        if self.usar_database:
            return self.db.actualizar_encuesta(encuesta_id, datos_actualizados, usuario)
        else:
            raise Exception("La función de edición requiere PostgreSQL")
    
    def obtener_historial(self, encuesta_id):
        """Obtener historial de cambios de una encuesta"""
        if self.usar_database:
            return self.db.obtener_historial(encuesta_id)
        else:
            return pd.DataFrame()
    
    def eliminar_encuesta(self, encuesta_id):
        """Eliminar una encuesta"""
        if self.usar_database:
            return self.db.eliminar_encuesta(encuesta_id)
        else:
            raise Exception("La función de eliminación requiere PostgreSQL")
    
    def _crear_backup(self):
        """Crear backup del archivo de datos CSV"""
        try:
            if os.path.exists(self.data_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.backup_dir}/encuestas_backup_{timestamp}.csv"
                
                import shutil
                shutil.copy2(self.data_file, backup_filename)
                self._limpiar_backups_antiguos()
                
        except Exception as e:
            print(f"Warning: No se pudo crear backup: {str(e)}")
    
    def _limpiar_backups_antiguos(self):
        """Mantener solo los últimos 10 backups"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('encuestas_backup_')]
            backups.sort(reverse=True)
            
            for backup in backups[10:]:
                backup_path = os.path.join(self.backup_dir, backup)
                os.remove(backup_path)
                
        except Exception as e:
            print(f"Warning: Error al limpiar backups: {str(e)}")
    
    def buscar_por_criterio(self, criterio, valor):
        """Buscar encuestas por un criterio específico"""
        try:
            df = self.cargar_datos()
            if df.empty:
                return df
            
            if criterio in df.columns:
                mask = df[criterio].str.contains(valor, case=False, na=False)
                return df[mask]
            else:
                return pd.DataFrame()
                
        except Exception as e:
            print(f"Error en búsqueda: {str(e)}")
            return pd.DataFrame()
    
    def obtener_estadisticas(self):
        """Obtener estadísticas básicas de los datos"""
        try:
            if self.usar_database:
                return self.db.obtener_estadisticas()
            else:
                df = self.cargar_datos()
                if df.empty:
                    return {}
                
                stats = {
                    'total_encuestas': len(df),
                    'departamentos_unicos': df['departamento'].nunique() if 'departamento' in df.columns else 0,
                    'sistemas_unicos': df['sistema_origen'].nunique() if 'sistema_origen' in df.columns else 0,
                    'reportes_criticos': len(df[df['criticidad'] == 'Alto']) if 'criticidad' in df.columns else 0,
                    'reportes_automatizados': len(df[df['automatizado'] == 'Sí']) if 'automatizado' in df.columns else 0
                }
                
                return stats
                
        except Exception as e:
            print(f"Error al calcular estadísticas: {str(e)}")
            return {}
    
    def exportar_a_excel(self, df=None, filename=None):
        """Exportar datos a Excel con múltiples hojas"""
        try:
            if df is None:
                df = self.cargar_datos()
                
            if df.empty:
                raise Exception("No hay datos para exportar")
            
            if filename is None:
                filename = f"encuestas_reportes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Hoja principal con todos los datos
                df.to_excel(writer, sheet_name='Todas las Encuestas', index=False)
                
                # Hoja por departamento
                if 'departamento' in df.columns:
                    for dept in df['departamento'].dropna().unique():
                        df_dept = df[df['departamento'] == dept]
                        sheet_name = dept[:30]
                        df_dept.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Hoja de estadísticas
                stats = self.obtener_estadisticas()
                if stats:
                    stats_df = pd.DataFrame(list(stats.items()), columns=['Métrica', 'Valor'])
                    stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error al exportar a Excel: {str(e)}")
