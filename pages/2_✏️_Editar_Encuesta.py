import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import DataManager
from utils.auth import Auth

st.set_page_config(
    page_title="Editar Encuesta - Reportes",
    page_icon="✏️",
    layout="wide"
)

data_manager = DataManager()
auth = Auth()

def main():
    # Verificar autenticación
    if not auth.login():
        return
    
    # Mostrar info de usuario
    auth.mostrar_info_usuario()
    st.title("✏️ Editar Encuesta")
    st.markdown("---")
    
    if not data_manager.usar_database:
        st.error("❌ La función de edición requiere PostgreSQL. Actualmente usando almacenamiento CSV.")
        st.info("Por favor contacte al administrador para habilitar PostgreSQL.")
        return
    
    # Cargar todas las encuestas
    df = data_manager.cargar_datos()
    
    if df.empty:
        st.warning("📭 No hay encuestas registradas para editar.")
        return
    
    # Selector de encuesta
    st.subheader("📋 Seleccionar Encuesta para Editar")
    
    # Crear opciones de selección
    opciones = []
    for _, row in df.iterrows():
        opcion = f"ID: {row['id']} | {row['nombre_reporte']} - {row['persona_responsable']}"
        opciones.append(opcion)
    
    seleccion = st.selectbox(
        "Encuesta:",
        ["Seleccione una encuesta..."] + opciones,
        help="Seleccione la encuesta que desea editar"
    )
    
    if seleccion == "Seleccione una encuesta...":
        st.info("👆 Seleccione una encuesta de la lista para comenzar a editarla")
        return
    
    # Extraer ID de la selección
    encuesta_id = int(seleccion.split("|")[0].replace("ID:", "").strip())
    
    # Cargar datos de la encuesta
    encuesta = data_manager.obtener_encuesta_por_id(encuesta_id)
    
    if encuesta is None:
        st.error("Error al cargar la encuesta seleccionada")
        return
    
    st.markdown("---")
    st.subheader("📝 Editar Información")
    
    # Formulario de edición
    with st.form("editar_encuesta"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_reporte = st.text_input(
                "Nombre del Reporte *",
                value=str(encuesta['nombre_reporte']) if pd.notna(encuesta['nombre_reporte']) else ""
            )
            
            periodicidad_reporte = st.selectbox(
                "Periodicidad del Reporte *",
                ["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"],
                index=["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"].index(
                    str(encuesta['periodicidad_reporte']) if pd.notna(encuesta['periodicidad_reporte']) else ""
                ) if pd.notna(encuesta['periodicidad_reporte']) and str(encuesta['periodicidad_reporte']) in ["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"] else 0
            )
            
            sistema_origen = st.text_input(
                "Sistema de Origen *",
                value=str(encuesta['sistema_origen']) if pd.notna(encuesta['sistema_origen']) else ""
            )
            
            persona_responsable = st.text_input(
                "Persona Responsable *",
                value=str(encuesta['persona_responsable']) if pd.notna(encuesta['persona_responsable']) else ""
            )
            
            email_responsable = st.text_input(
                "Email del Responsable *",
                value=str(encuesta['email_responsable']) if pd.notna(encuesta['email_responsable']) else ""
            )
        
        with col2:
            auditoria_utilizacion = st.text_area(
                "Auditoría donde se Utiliza *",
                value=str(encuesta['auditoria_utilizacion']) if pd.notna(encuesta['auditoria_utilizacion']) else ""
            )
            
            periodicidad_auditoria = st.selectbox(
                "Periodicidad de la Auditoría",
                ["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"],
                index=["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"].index(
                    str(encuesta['periodicidad_auditoria']) if pd.notna(encuesta['periodicidad_auditoria']) else ""
                ) if pd.notna(encuesta['periodicidad_auditoria']) and str(encuesta['periodicidad_auditoria']) in ["", "Diario", "Semanal", "Quincenal", "Mensual", "Bimestral", "Trimestral", "Semestral", "Anual", "Ad-hoc"] else 0
            )
            
            departamento = st.selectbox(
                "Departamento *",
                ["", "Finanzas", "Recursos Humanos", "Operaciones", "IT", "Ventas", "Marketing", "Legal", "Auditoría Interna", "Otro"],
                index=["", "Finanzas", "Recursos Humanos", "Operaciones", "IT", "Ventas", "Marketing", "Legal", "Auditoría Interna", "Otro"].index(
                    str(encuesta['departamento']) if pd.notna(encuesta['departamento']) else ""
                ) if pd.notna(encuesta['departamento']) and str(encuesta['departamento']) in ["", "Finanzas", "Recursos Humanos", "Operaciones", "IT", "Ventas", "Marketing", "Legal", "Auditoría Interna", "Otro"] else 0
            )
            
            criticidad = st.selectbox(
                "Nivel de Criticidad *",
                ["", "Alto", "Medio", "Bajo"],
                index=["", "Alto", "Medio", "Bajo"].index(
                    str(encuesta['criticidad']) if pd.notna(encuesta['criticidad']) else ""
                ) if pd.notna(encuesta['criticidad']) and str(encuesta['criticidad']) in ["", "Alto", "Medio", "Bajo"] else 0
            )
            
            # Parsear formato_entrega desde string
            formatos_actuales = []
            if pd.notna(encuesta['formato_entrega']) and encuesta['formato_entrega']:
                formatos_actuales = [f.strip() for f in str(encuesta['formato_entrega']).split(',')]
            
            formato_entrega = st.multiselect(
                "Formato de Entrega",
                ["Excel", "PDF", "CSV", "Dashboard", "Email", "Portal Web", "Otro"],
                default=formatos_actuales
            )
        
        st.subheader("📝 Información Adicional")
        
        col3, col4 = st.columns(2)
        
        with col3:
            descripcion_reporte = st.text_area(
                "Descripción del Reporte",
                value=str(encuesta['descripcion_reporte']) if pd.notna(encuesta['descripcion_reporte']) else ""
            )
            
            stakeholders = st.text_area(
                "Stakeholders/Usuarios",
                value=str(encuesta['stakeholders']) if pd.notna(encuesta['stakeholders']) else ""
            )
        
        with col4:
            automatizado = st.selectbox(
                "¿Está Automatizado?",
                ["", "Sí", "No", "Parcialmente"],
                index=["", "Sí", "No", "Parcialmente"].index(
                    str(encuesta['automatizado']) if pd.notna(encuesta['automatizado']) else ""
                ) if pd.notna(encuesta['automatizado']) and str(encuesta['automatizado']) in ["", "Sí", "No", "Parcialmente"] else 0
            )
            
            observaciones = st.text_area(
                "Observaciones",
                value=str(encuesta['observaciones']) if pd.notna(encuesta['observaciones']) else ""
            )
        
        # Motivo del cambio
        st.markdown("---")
        motivo_cambio = st.text_area(
            "Motivo del Cambio (Opcional)",
            help="Describa brevemente por qué se está realizando esta modificación"
        )
        
        # Botones
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            guardar = st.form_submit_button(
                "💾 Guardar Cambios",
                use_container_width=True,
                type="primary"
            )
        
        with col_btn2:
            cancelar = st.form_submit_button(
                "❌ Cancelar",
                use_container_width=True
            )
        
        if cancelar:
            st.info("Edición cancelada")
            st.rerun()
        
        if guardar:
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
                # Validar email
                if "@" not in email_responsable or "." not in email_responsable:
                    st.error("❌ Por favor ingrese un email válido")
                else:
                    # Preparar datos actualizados
                    datos_actualizados = {
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
                    
                    try:
                        data_manager.actualizar_encuesta(
                            encuesta_id, 
                            datos_actualizados, 
                            usuario=persona_responsable
                        )
                        st.success("✅ ¡Encuesta actualizada exitosamente!")
                        st.balloons()
                        
                        # Mostrar resumen
                        st.markdown("### 📋 Cambios Guardados")
                        st.write(f"**Reporte:** {nombre_reporte}")
                        st.write(f"**Actualizado por:** {persona_responsable}")
                        st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                        
                        if motivo_cambio:
                            st.write(f"**Motivo:** {motivo_cambio}")
                        
                    except Exception as e:
                        st.error(f"❌ Error al actualizar la encuesta: {str(e)}")
    
    # Mostrar historial de cambios
    st.markdown("---")
    st.subheader("📜 Historial de Cambios")
    
    historial = data_manager.obtener_historial(encuesta_id)
    
    if historial.empty:
        st.info("No hay cambios registrados para esta encuesta")
    else:
        # Mostrar en formato expandible
        for _, cambio in historial.iterrows():
            fecha_str = pd.to_datetime(cambio['fecha_modificacion']).strftime('%d/%m/%Y %H:%M:%S')
            
            with st.expander(f"🕐 {fecha_str} - {cambio['campo_modificado']}"):
                col_h1, col_h2 = st.columns(2)
                
                with col_h1:
                    st.write("**Valor Anterior:**")
                    st.text(cambio['valor_anterior'] if pd.notna(cambio['valor_anterior']) else "(vacío)")
                
                with col_h2:
                    st.write("**Valor Nuevo:**")
                    st.text(cambio['valor_nuevo'] if pd.notna(cambio['valor_nuevo']) else "(vacío)")
                
                st.write(f"**Usuario:** {cambio['usuario_modificacion']}")
                
                if pd.notna(cambio['motivo_cambio']) and cambio['motivo_cambio']:
                    st.write(f"**Motivo:** {cambio['motivo_cambio']}")

if __name__ == "__main__":
    main()
