import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from utils.data_manager import DataManager

# Configuración de la página
st.set_page_config(
    page_title="Panel de Administración - Reportes",
    page_icon="📊",
    layout="wide"
)

# Inicializar el gestor de datos
data_manager = DataManager()

def main():
    st.title("📊 Panel de Administración")
    st.markdown("---")
    
    # Verificar si hay datos
    df = data_manager.cargar_datos()
    
    if df.empty:
        st.warning("📭 No hay encuestas registradas aún.")
        st.info("Las encuestas completadas aparecerán automáticamente en este panel.")
        return
    
    # Métricas generales
    st.subheader("📈 Métricas Generales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Encuestas", len(df))
    
    with col2:
        # Encuestas de la última semana
        fecha_semana = datetime.now() - timedelta(days=7)
        df['fecha_envio'] = pd.to_datetime(df['fecha_envio'])
        encuestas_semana = len(df[df['fecha_envio'] >= fecha_semana])
        st.metric("Última Semana", encuestas_semana)
    
    with col3:
        # Departamento más activo
        if 'departamento' in df.columns:
            dept_mas_activo = df['departamento'].mode().iloc[0] if len(df['departamento'].mode()) > 0 else "N/A"
            st.metric("Dept. Más Activo", dept_mas_activo)
        else:
            st.metric("Dept. Más Activo", "N/A")
    
    with col4:
        # Reportes críticos
        if 'criticidad' in df.columns:
            reportes_criticos = len(df[df['criticidad'] == 'Alto'])
            st.metric("Reportes Críticos", reportes_criticos)
        else:
            st.metric("Reportes Críticos", "N/A")
    
    st.markdown("---")
    
    # Filtros
    st.subheader("🔍 Filtros y Búsqueda")
    
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        # Filtro por departamento
        departamentos_disponibles = ["Todos"] + sorted(df['departamento'].dropna().unique().tolist()) if 'departamento' in df.columns else ["Todos"]
        filtro_departamento = st.selectbox("Departamento", departamentos_disponibles)
    
    with col_filter2:
        # Filtro por criticidad
        criticidades_disponibles = ["Todas"] + sorted(df['criticidad'].dropna().unique().tolist()) if 'criticidad' in df.columns else ["Todas"]
        filtro_criticidad = st.selectbox("Criticidad", criticidades_disponibles)
    
    with col_filter3:
        # Filtro por periodicidad
        periodicidades_disponibles = ["Todas"] + sorted(df['periodicidad_reporte'].dropna().unique().tolist()) if 'periodicidad_reporte' in df.columns else ["Todas"]
        filtro_periodicidad = st.selectbox("Periodicidad", periodicidades_disponibles)
    
    # Búsqueda por texto
    busqueda_texto = st.text_input("🔎 Buscar en nombres de reportes, responsables o sistemas:", placeholder="Escriba para buscar...")
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if filtro_departamento != "Todos":
        df_filtrado = df_filtrado[df_filtrado['departamento'] == filtro_departamento]
    
    if filtro_criticidad != "Todas":
        df_filtrado = df_filtrado[df_filtrado['criticidad'] == filtro_criticidad]
    
    if filtro_periodicidad != "Todas":
        df_filtrado = df_filtrado[df_filtrado['periodicidad_reporte'] == filtro_periodicidad]
    
    if busqueda_texto:
        mask = (
            df_filtrado['nombre_reporte'].str.contains(busqueda_texto, case=False, na=False) |
            df_filtrado['persona_responsable'].str.contains(busqueda_texto, case=False, na=False) |
            df_filtrado['sistema_origen'].str.contains(busqueda_texto, case=False, na=False)
        )
        df_filtrado = df_filtrado[mask]
    
    st.write(f"**Mostrando {len(df_filtrado)} de {len(df)} encuestas**")
    
    if df_filtrado.empty:
        st.warning("No se encontraron resultados con los filtros aplicados.")
        return
    
    # Botones de exportación
    st.subheader("📤 Exportar Datos")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        # Exportar a CSV
        csv_data = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📄 Descargar CSV",
            data=csv_data,
            file_name=f"encuestas_reportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Exportar a Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, sheet_name='Encuestas', index=False)
            
            # Crear hoja de resumen
            resumen_data = {
                'Métrica': ['Total Encuestas', 'Encuestas Críticas', 'Departamentos Únicos', 'Sistemas Únicos'],
                'Valor': [
                    len(df_filtrado),
                    len(df_filtrado[df_filtrado['criticidad'] == 'Alto']) if 'criticidad' in df_filtrado.columns else 0,
                    df_filtrado['departamento'].nunique() if 'departamento' in df_filtrado.columns else 0,
                    df_filtrado['sistema_origen'].nunique() if 'sistema_origen' in df_filtrado.columns else 0
                ]
            }
            pd.DataFrame(resumen_data).to_excel(writer, sheet_name='Resumen', index=False)
        
        excel_buffer.seek(0)
        st.download_button(
            label="📊 Descargar Excel",
            data=excel_buffer.getvalue(),
            file_name=f"encuestas_reportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col_export3:
        if st.button("🗑️ Limpiar Filtros"):
            st.rerun()
    
    st.markdown("---")
    
    # Tabla de datos
    st.subheader("📋 Datos de Encuestas")
    
    # Configurar columnas para mostrar
    columnas_mostrar = [
        'fecha_envio', 'nombre_reporte', 'persona_responsable', 
        'departamento', 'criticidad', 'periodicidad_reporte', 
        'sistema_origen', 'automatizado'
    ]
    
    # Filtrar solo las columnas que existen en el DataFrame
    columnas_existentes = [col for col in columnas_mostrar if col in df_filtrado.columns]
    
    if columnas_existentes:
        df_mostrar = df_filtrado[columnas_existentes].copy()
        
        # Formatear la fecha para mejor visualización
        if 'fecha_envio' in df_mostrar.columns:
            df_mostrar['fecha_envio'] = pd.to_datetime(df_mostrar['fecha_envio']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Mostrar tabla con configuración personalizada
        st.dataframe(
            df_mostrar,
            use_container_width=True,
            hide_index=True,
            column_config={
                "fecha_envio": st.column_config.TextColumn("Fecha Envío"),
                "nombre_reporte": st.column_config.TextColumn("Nombre Reporte"),
                "persona_responsable": st.column_config.TextColumn("Responsable"),
                "departamento": st.column_config.TextColumn("Departamento"),
                "criticidad": st.column_config.TextColumn("Criticidad"),
                "periodicidad_reporte": st.column_config.TextColumn("Periodicidad"),
                "sistema_origen": st.column_config.TextColumn("Sistema Origen"),
                "automatizado": st.column_config.TextColumn("Automatizado")
            }
        )
    
    # Detalles de encuesta seleccionada
    st.markdown("---")
    st.subheader("🔍 Detalles de Encuesta")
    
    if len(df_filtrado) > 0:
        opciones_detalle = [f"{row['nombre_reporte']} - {row['persona_responsable']}" for _, row in df_filtrado.iterrows()]
        seleccion_detalle = st.selectbox("Seleccione una encuesta para ver detalles completos:", ["Seleccione una encuesta..."] + opciones_detalle)
        
        if seleccion_detalle != "Seleccione una encuesta...":
            indice_seleccionado = opciones_detalle.index(seleccion_detalle)
            encuesta_seleccionada = df_filtrado.iloc[indice_seleccionado]
            
            col_det1, col_det2 = st.columns(2)
            
            with col_det1:
                st.write("**Información General:**")
                st.write(f"• **Fecha:** {pd.to_datetime(encuesta_seleccionada['fecha_envio']).strftime('%d/%m/%Y %H:%M')}")
                st.write(f"• **Nombre:** {encuesta_seleccionada['nombre_reporte']}")
                st.write(f"• **Responsable:** {encuesta_seleccionada['persona_responsable']}")
                st.write(f"• **Email:** {encuesta_seleccionada['email_responsable']}")
                st.write(f"• **Departamento:** {encuesta_seleccionada['departamento']}")
                st.write(f"• **Criticidad:** {encuesta_seleccionada['criticidad']}")
            
            with col_det2:
                st.write("**Detalles Técnicos:**")
                st.write(f"• **Sistema Origen:** {encuesta_seleccionada['sistema_origen']}")
                st.write(f"• **Periodicidad:** {encuesta_seleccionada['periodicidad_reporte']}")
                st.write(f"• **Automatizado:** {encuesta_seleccionada['automatizado']}")
                if 'formato_entrega' in encuesta_seleccionada and encuesta_seleccionada['formato_entrega']:
                    st.write(f"• **Formatos:** {encuesta_seleccionada['formato_entrega']}")
            
            if 'auditoria_utilizacion' in encuesta_seleccionada and encuesta_seleccionada['auditoria_utilizacion']:
                st.write("**Auditoría:**")
                st.write(encuesta_seleccionada['auditoria_utilizacion'])
            
            if 'descripcion_reporte' in encuesta_seleccionada and encuesta_seleccionada['descripcion_reporte']:
                st.write("**Descripción:**")
                st.write(encuesta_seleccionada['descripcion_reporte'])
            
            if 'observaciones' in encuesta_seleccionada and encuesta_seleccionada['observaciones']:
                st.write("**Observaciones:**")
                st.write(encuesta_seleccionada['observaciones'])

    # Gráficos y análisis
    st.markdown("---")
    st.subheader("📈 Análisis Visual")
    
    if len(df_filtrado) > 1:
        tab1, tab2, tab3 = st.tabs(["📊 Por Departamento", "⏱️ Por Periodicidad", "🔥 Por Criticidad"])
        
        with tab1:
            if 'departamento' in df_filtrado.columns:
                dept_counts = df_filtrado['departamento'].value_counts()
                if len(dept_counts) > 0:
                    st.bar_chart(dept_counts)
                else:
                    st.info("No hay datos de departamento para mostrar.")
        
        with tab2:
            if 'periodicidad_reporte' in df_filtrado.columns:
                period_counts = df_filtrado['periodicidad_reporte'].value_counts()
                if len(period_counts) > 0:
                    st.bar_chart(period_counts)
                else:
                    st.info("No hay datos de periodicidad para mostrar.")
        
        with tab3:
            if 'criticidad' in df_filtrado.columns:
                crit_counts = df_filtrado['criticidad'].value_counts()
                if len(crit_counts) > 0:
                    st.bar_chart(crit_counts)
                else:
                    st.info("No hay datos de criticidad para mostrar.")

if __name__ == "__main__":
    main()
