import pandas as pd
import os
from datetime import datetime
import csv

class DataManager:
    def __init__(self):
        self.data_file = "encuestas_reportes.csv"
        self.backup_dir = "backups"
        self._crear_directorio_backups()
        self._inicializar_archivo_datos()
    
    def _crear_directorio_backups(self):
        """Crear directorio de backups si no existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def _inicializar_archivo_datos(self):
        """Crear archivo CSV con headers si no existe"""
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
            
            with open(self.data_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
    
    def guardar_respuesta(self, datos_encuesta):
        """Guardar una nueva respuesta de encuesta"""
        try:
            # Crear backup antes de guardar
            self._crear_backup()
            
            # Preparar los datos en el orden correcto
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
            
            # Escribir al archivo CSV
            with open(self.data_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(row_data)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error al guardar los datos: {str(e)}")
    
    def cargar_datos(self):
        """Cargar todos los datos del archivo CSV"""
        try:
            if os.path.exists(self.data_file) and os.path.getsize(self.data_file) > 0:
                df = pd.read_csv(self.data_file, encoding='utf-8')
                return df
            else:
                # Retornar DataFrame vacío con las columnas esperadas
                return pd.DataFrame(columns=[
                    "fecha_envio", "nombre_reporte", "periodicidad_reporte",
                    "sistema_origen", "persona_responsable", "email_responsable",
                    "auditoria_utilizacion", "periodicidad_auditoria", 
                    "departamento", "criticidad", "formato_entrega",
                    "descripcion_reporte", "stakeholders", "automatizado", "observaciones"
                ])
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            return pd.DataFrame()
    
    def obtener_total_respuestas(self):
        """Obtener el número total de respuestas"""
        try:
            df = self.cargar_datos()
            return len(df)
        except:
            return 0
    
    def _crear_backup(self):
        """Crear backup del archivo de datos"""
        try:
            if os.path.exists(self.data_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"{self.backup_dir}/encuestas_backup_{timestamp}.csv"
                
                # Copiar archivo actual al backup
                import shutil
                shutil.copy2(self.data_file, backup_filename)
                
                # Mantener solo los últimos 10 backups
                self._limpiar_backups_antiguos()
                
        except Exception as e:
            print(f"Warning: No se pudo crear backup: {str(e)}")
    
    def _limpiar_backups_antiguos(self):
        """Mantener solo los últimos 10 backups"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.startswith('encuestas_backup_')]
            backups.sort(reverse=True)  # Más recientes primero
            
            # Eliminar backups antiguos (mantener solo 10)
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
    
    def exportar_a_excel(self, filename=None):
        """Exportar datos a Excel con múltiples hojas"""
        try:
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
                        sheet_name = dept[:30]  # Limitar longitud del nombre
                        df_dept.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Hoja de estadísticas
                stats = self.obtener_estadisticas()
                if stats:
                    stats_df = pd.DataFrame(list(stats.items()), columns=['Métrica', 'Valor'])
                    stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error al exportar a Excel: {str(e)}")
