import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils.data_manager import DataManager
from utils.email_sender import EmailSender

# Configuración de la página
st.set_page_config(
    page_title="Encuesta de Reportes Corporativos",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar el gestor de datos
data_manager = DataManager()

def main():
    st.title("📋 Encuesta de Reportes Corporativos")
    st.markdown("---")
    
    st.markdown("""
    ### Bienvenido al Sistema de Gestión de Reportes
    
    Esta encuesta tiene como objetivo recopilar información detallada sobre los reportes utilizados en nuestra compañía. 
    Por favor, complete todos los campos obligatorios marcados con (*).
    """)
    
    # Crear el formulario
    with st.form("encuesta_reportes"):
        st.subheader("📄 Información del Reporte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_reporte = st.text_input(
                "Nombre del Reporte *", 
                help="Ingrese el nombre completo del reporte"
            )
            
            periodicidad_reporte = st.selectbox(
                "Periodicidad del Reporte *",
                ["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"],
                help="Seleccione la frecuencia de generación del reporte"
            )
            
            sistema_origen = st.text_input(
                "Sistema de Origen *",
                help="Sistema o aplicación donde se genera el reporte"
            )
            
            persona_responsable = st.text_input(
                "Persona Responsable *",
                help="Nombre completo del responsable del reporte"
            )
            
            email_responsable = st.text_input(
                "Email del Responsable *",
                help="Correo electrónico del responsable"
            )
        
        with col2:
            auditoria_utilizacion = st.text_area(
                "Auditoría donde se Utiliza *",
                help="Describa en qué auditorías o procesos se utiliza este reporte"
            )
            
            periodicidad_auditoria = st.selectbox(
                "Periodicidad de la Auditoría",
                ["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"],
                help="Frecuencia con la que se realiza la auditoría"
            )
            
            departamento = st.selectbox(
                "Departamento *",
                ["", "Finanzas", "Recursos Humanos", "Operaciones", "IT", "Ventas", "Marketing", "Legal", "Auditoría Interna", "Otro"],
                help="Departamento al que pertenece el reporte"
            )
            
            criticidad = st.selectbox(
                "Nivel de Criticidad *",
                ["", "Alto", "Medio", "Bajo"],
                help="Nivel de importancia del reporte para el negocio"
            )
            
            formato_entrega = st.multiselect(
                "Formato de Entrega",
                ["Excel", "PDF", "CSV", "Dashboard", "Email", "Portal Web", "Otro"],
                help="Seleccione todos los formatos aplicables"
            )
        
        st.subheader("📝 Información Adicional")
        
        col3, col4 = st.columns(2)
        
        with col3:
            descripcion_reporte = st.text_area(
                "Descripción del Reporte",
                help="Breve descripción del contenido y propósito del reporte"
            )
            
            stakeholders = st.text_area(
                "Stakeholders/Usuarios",
                help="Liste las personas o departamentos que reciben o utilizan este reporte"
            )
        
        with col4:
            automatizado = st.selectbox(
                "¿Está Automatizado?",
                ["", "Sí", "No", "Parcialmente"],
                help="Indique si el reporte se genera automáticamente"
            )
            
            observaciones = st.text_area(
                "Observaciones",
                help="Cualquier información adicional relevante"
            )
        
        # Botón de envío
        submitted = st.form_submit_button(
            "📤 Enviar Encuesta",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validar campos obligatorios
            campos_obligatorios = {
                "Nombre del Reporte": nombre_reporte,
                "Periodicidad del Reporte": periodicidad_reporte,
                "Sistema de Origen": sistema_origen,
                "Persona Responsable": persona_responsable,
                "Email del Responsable": email_responsable,
                "Auditoría donde se Utiliza": auditoria_utilizacion,
                "Departamento": departamento,
                "Nivel de Criticidad": criticidad
            }
            
            campos_faltantes = [campo for campo, valor in campos_obligatorios.items() if not valor or valor == ""]
            
            if campos_faltantes:
                st.error(f"❌ Por favor complete los siguientes campos obligatorios: {', '.join(campos_faltantes)}")
            else:
                # Validar formato de email
                if "@" not in email_responsable or "." not in email_responsable:
                    st.error("❌ Por favor ingrese un email válido")
                else:
                    # Preparar datos para guardar
                    datos_encuesta = {
                        "fecha_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "nombre_reporte": nombre_reporte,
                        "periodicidad_reporte": periodicidad_reporte,
                        "sistema_origen": sistema_origen,
                        "persona_responsable": persona_responsable,
                        "email_responsable": email_responsable,
                        "auditoria_utilizacion": auditoria_utilizacion,
                        "periodicidad_auditoria": periodicidad_auditoria,
                        "departamento": departamento,
                        "criticidad": criticidad,
                        "formato_entrega": ", ".join(formato_entrega) if formato_entrega else "",
                        "descripcion_reporte": descripcion_reporte,
                        "stakeholders": stakeholders,
                        "automatizado": automatizado,
                        "observaciones": observaciones
                    }
                    
                    # Guardar datos
                    try:
                        data_manager.guardar_respuesta(datos_encuesta)
                        st.success("✅ ¡Encuesta enviada exitosamente! Gracias por su colaboración.")
                        
                        # Enviar email de confirmación (opcional)
                        try:
                            email_sender = EmailSender()
                            email_sender.enviar_confirmacion(email_responsable, nombre_reporte)
                        except Exception as e:
                            st.info("ℹ️ La encuesta fue guardada correctamente, pero no se pudo enviar el email de confirmación.")
                        
                        # Mostrar resumen
                        st.markdown("### 📋 Resumen de la Información Enviada:")
                        col_res1, col_res2 = st.columns(2)
                        
                        with col_res1:
                            st.write(f"**Reporte:** {nombre_reporte}")
                            st.write(f"**Periodicidad:** {periodicidad_reporte}")
                            st.write(f"**Sistema:** {sistema_origen}")
                            st.write(f"**Responsable:** {persona_responsable}")
                        
                        with col_res2:
                            st.write(f"**Departamento:** {departamento}")
                            st.write(f"**Criticidad:** {criticidad}")
                            st.write(f"**Automatizado:** {automatizado}")
                            st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                        
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Error al guardar la encuesta: {str(e)}")

    # Información adicional en la barra lateral
    with st.sidebar:
        st.markdown("### ℹ️ Información")
        st.info("""
        **Objetivo:** Recopilar información sobre los reportes corporativos para mejorar la gestión y auditoría.
        
        **Confidencialidad:** Toda la información proporcionada será tratada de forma confidencial.
        
        **Soporte:** Para dudas o problemas técnicos, contacte al administrador del sistema.
        """)
        
        st.markdown("### 📊 Estadísticas")
        total_respuestas = data_manager.obtener_total_respuestas()
        st.metric("Total de Encuestas", total_respuestas)
        
        if total_respuestas > 0:
            st.markdown("### 🔗 Enlaces Útiles")
            st.markdown("[📊 Panel de Administración](pages/1_📊_Panel_Administración)")

if __name__ == "__main__":
    main()
