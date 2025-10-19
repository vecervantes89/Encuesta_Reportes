import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.auth import Auth

st.set_page_config(
    page_title="Dashboard y Estadísticas",
    page_icon="📈",
    layout="wide"
)

data_manager = DataManager()
auth = Auth()

def crear_grafico_periodicidad(df):
    """Crear gráfico de periodicidad de reportes"""
    if 'periodicidad_reporte' not in df.columns or df.empty:
        return None
    
    periodicidad_counts = df['periodicidad_reporte'].value_counts().reset_index()
    periodicidad_counts.columns = ['Periodicidad', 'Cantidad']
    
    fig = px.bar(
        periodicidad_counts,
        x='Periodicidad',
        y='Cantidad',
        title='Distribución de Reportes por Periodicidad',
        color='Cantidad',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title="Periodicidad",
        yaxis_title="Número de Reportes",
        showlegend=False
    )
    
    return fig

def crear_grafico_departamentos(df):
    """Crear gráfico circular de departamentos"""
    if 'departamento' not in df.columns or df.empty:
        return None
    
    dept_counts = df['departamento'].value_counts().reset_index()
    dept_counts.columns = ['Departamento', 'Cantidad']
    
    fig = px.pie(
        dept_counts,
        values='Cantidad',
        names='Departamento',
        title='Distribución de Reportes por Departamento',
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def crear_grafico_criticidad(df):
    """Crear gráfico de criticidad"""
    if 'criticidad' not in df.columns or df.empty:
        return None
    
    criticidad_counts = df['criticidad'].value_counts().reset_index()
    criticidad_counts.columns = ['Criticidad', 'Cantidad']
    
    # Ordenar por nivel de criticidad
    orden_criticidad = {'Alto': 0, 'Medio': 1, 'Bajo': 2}
    criticidad_counts['orden'] = criticidad_counts['Criticidad'].map(orden_criticidad)
    criticidad_counts = criticidad_counts.sort_values('orden')
    
    colores = {'Alto': '#dc3545', 'Medio': '#ffc107', 'Bajo': '#28a745'}
    criticidad_counts['color'] = criticidad_counts['Criticidad'].map(colores)
    
    fig = go.Figure(data=[
        go.Bar(
            x=criticidad_counts['Criticidad'],
            y=criticidad_counts['Cantidad'],
            marker_color=criticidad_counts['color'],
            text=criticidad_counts['Cantidad'],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Distribución de Reportes por Nivel de Criticidad',
        xaxis_title="Nivel de Criticidad",
        yaxis_title="Número de Reportes",
        showlegend=False
    )
    
    return fig

def crear_grafico_sistemas(df):
    """Crear gráfico de sistemas más utilizados"""
    if 'sistema_origen' not in df.columns or df.empty:
        return None
    
    sistemas_counts = df['sistema_origen'].value_counts().head(10).reset_index()
    sistemas_counts.columns = ['Sistema', 'Cantidad']
    
    fig = px.bar(
        sistemas_counts,
        y='Sistema',
        x='Cantidad',
        title='Top 10 Sistemas Más Utilizados',
        orientation='h',
        color='Cantidad',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Número de Reportes",
        yaxis_title="Sistema de Origen",
        showlegend=False
    )
    
    return fig

def crear_grafico_automatizacion(df):
    """Crear gráfico de automatización"""
    if 'automatizado' not in df.columns or df.empty:
        return None
    
    auto_counts = df['automatizado'].value_counts().reset_index()
    auto_counts.columns = ['Estado', 'Cantidad']
    
    fig = px.pie(
        auto_counts,
        values='Cantidad',
        names='Estado',
        title='Estado de Automatización de Reportes',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    return fig

def crear_grafico_tendencia_temporal(df):
    """Crear gráfico de tendencia temporal"""
    if 'fecha_envio' not in df.columns or df.empty:
        return None
    
    df_temp = df.copy()
    df_temp['fecha_envio'] = pd.to_datetime(df_temp['fecha_envio'])
    df_temp['fecha'] = df_temp['fecha_envio'].dt.date
    
    tendencia = df_temp.groupby('fecha').size().reset_index(name='cantidad')
    
    fig = px.line(
        tendencia,
        x='fecha',
        y='cantidad',
        title='Tendencia de Encuestas Recibidas',
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Número de Encuestas",
        showlegend=False
    )
    
    return fig

def main():
    # Verificar autenticación
    if not auth.login():
        return
    
    # Mostrar info de usuario
    auth.mostrar_info_usuario()
    
    st.title("📈 Dashboard y Estadísticas")
    st.markdown("---")
    
    # Cargar datos
    df = data_manager.cargar_datos()
    
    if df.empty:
        st.warning("📭 No hay datos disponibles para mostrar estadísticas.")
        st.info("Complete algunas encuestas para ver el dashboard con estadísticas detalladas.")
        return
    
    # Métricas principales
    st.subheader("🎯 Métricas Principales")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_encuestas = len(df)
        st.metric("Total Reportes", total_encuestas)
    
    with col2:
        if 'departamento' in df.columns:
            dept_unicos = df['departamento'].nunique()
            st.metric("Departamentos", dept_unicos)
        else:
            st.metric("Departamentos", "N/A")
    
    with col3:
        if 'sistema_origen' in df.columns:
            sistemas_unicos = df['sistema_origen'].nunique()
            st.metric("Sistemas", sistemas_unicos)
        else:
            st.metric("Sistemas", "N/A")
    
    with col4:
        if 'criticidad' in df.columns:
            criticos = len(df[df['criticidad'] == 'Alto'])
            st.metric("Críticos", criticos, delta=f"{(criticos/total_encuestas*100):.1f}%")
        else:
            st.metric("Críticos", "N/A")
    
    with col5:
        if 'automatizado' in df.columns:
            automatizados = len(df[df['automatizado'] == 'Sí'])
            st.metric("Automatizados", automatizados, delta=f"{(automatizados/total_encuestas*100):.1f}%")
        else:
            st.metric("Automatizados", "N/A")
    
    st.markdown("---")
    
    # Gráficos principales
    st.subheader("📊 Análisis Visual")
    
    # Primera fila de gráficos
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        fig_periodicidad = crear_grafico_periodicidad(df)
        if fig_periodicidad:
            st.plotly_chart(fig_periodicidad, use_container_width=True)
    
    with col_g2:
        fig_departamentos = crear_grafico_departamentos(df)
        if fig_departamentos:
            st.plotly_chart(fig_departamentos, use_container_width=True)
    
    # Segunda fila de gráficos
    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        fig_criticidad = crear_grafico_criticidad(df)
        if fig_criticidad:
            st.plotly_chart(fig_criticidad, use_container_width=True)
    
    with col_g4:
        fig_auto = crear_grafico_automatizacion(df)
        if fig_auto:
            st.plotly_chart(fig_auto, use_container_width=True)
    
    # Tercera fila - Sistemas y Tendencia
    st.markdown("---")
    
    col_g5, col_g6 = st.columns(2)
    
    with col_g5:
        fig_sistemas = crear_grafico_sistemas(df)
        if fig_sistemas:
            st.plotly_chart(fig_sistemas, use_container_width=True)
    
    with col_g6:
        fig_tendencia = crear_grafico_tendencia_temporal(df)
        if fig_tendencia:
            st.plotly_chart(fig_tendencia, use_container_width=True)
    
    # Análisis detallado
    st.markdown("---")
    st.subheader("🔍 Análisis Detallado")
    
    tabs = st.tabs(["📋 Por Periodicidad", "🏢 Por Departamento", "🔥 Por Criticidad", "🤖 Automatización"])
    
    with tabs[0]:
        if 'periodicidad_reporte' in df.columns:
            st.write("### Análisis por Periodicidad")
            
            periodicidad_stats = df.groupby('periodicidad_reporte').agg({
                'nombre_reporte': 'count',
                'criticidad': lambda x: (x == 'Alto').sum()
            }).reset_index()
            periodicidad_stats.columns = ['Periodicidad', 'Total Reportes', 'Reportes Críticos']
            
            st.dataframe(
                periodicidad_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # Listar reportes por periodicidad
            st.write("### Reportes por Periodicidad")
            periodicidad_sel = st.selectbox(
                "Seleccione periodicidad:",
                df['periodicidad_reporte'].dropna().unique()
            )
            
            if periodicidad_sel:
                reportes_filtrados = df[df['periodicidad_reporte'] == periodicidad_sel][
                    ['nombre_reporte', 'persona_responsable', 'departamento', 'criticidad']
                ]
                st.dataframe(reportes_filtrados, use_container_width=True, hide_index=True)
    
    with tabs[1]:
        if 'departamento' in df.columns:
            st.write("### Análisis por Departamento")
            
            dept_stats = df.groupby('departamento').agg({
                'nombre_reporte': 'count',
                'criticidad': lambda x: (x == 'Alto').sum(),
                'automatizado': lambda x: (x == 'Sí').sum()
            }).reset_index()
            dept_stats.columns = ['Departamento', 'Total Reportes', 'Críticos', 'Automatizados']
            
            st.dataframe(
                dept_stats,
                use_container_width=True,
                hide_index=True
            )
    
    with tabs[2]:
        if 'criticidad' in df.columns:
            st.write("### Análisis por Criticidad")
            
            for criticidad in ['Alto', 'Medio', 'Bajo']:
                reportes_crit = df[df['criticidad'] == criticidad]
                if not reportes_crit.empty:
                    color = {'Alto': '🔴', 'Medio': '🟡', 'Bajo': '🟢'}[criticidad]
                    
                    with st.expander(f"{color} {criticidad} - {len(reportes_crit)} reportes"):
                        st.dataframe(
                            reportes_crit[['nombre_reporte', 'persona_responsable', 'departamento', 'periodicidad_reporte']],
                            use_container_width=True,
                            hide_index=True
                        )
    
    with tabs[3]:
        if 'automatizado' in df.columns:
            st.write("### Análisis de Automatización")
            
            col_a1, col_a2, col_a3 = st.columns(3)
            
            with col_a1:
                auto_si = len(df[df['automatizado'] == 'Sí'])
                st.metric("Automatizados", auto_si, f"{(auto_si/len(df)*100):.1f}%")
            
            with col_a2:
                auto_no = len(df[df['automatizado'] == 'No'])
                st.metric("No Automatizados", auto_no, f"{(auto_no/len(df)*100):.1f}%")
            
            with col_a3:
                auto_parcial = len(df[df['automatizado'] == 'Parcialmente'])
                st.metric("Parcialmente", auto_parcial, f"{(auto_parcial/len(df)*100):.1f}%")
            
            # Oportunidades de automatización
            st.write("### 🎯 Oportunidades de Automatización")
            
            no_automatizados = df[df['automatizado'] == 'No']
            if not no_automatizados.empty:
                # Priorizar por periodicidad alta y criticidad
                periodicidad_prio = {'Diario': 5, 'Semanal': 4, 'Quincenal': 3, 'Mensual': 2, 'Bimestral': 1, 'Trimestral': 1}
                criticidad_prio = {'Alto': 3, 'Medio': 2, 'Bajo': 1}
                
                no_auto_priorizados = no_automatizados.copy()
                no_auto_priorizados['prioridad'] = (
                    no_auto_priorizados['periodicidad_reporte'].map(periodicidad_prio).fillna(0) +
                    no_auto_priorizados['criticidad'].map(criticidad_prio).fillna(0)
                )
                
                no_auto_priorizados = no_auto_priorizados.sort_values('prioridad', ascending=False)
                
                st.dataframe(
                    no_auto_priorizados[['nombre_reporte', 'periodicidad_reporte', 'criticidad', 'departamento', 'persona_responsable']].head(10),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ ¡Excelente! Todos los reportes están automatizados.")
    
    # Insights y recomendaciones
    st.markdown("---")
    st.subheader("💡 Insights y Recomendaciones")
    
    insights = []
    
    # Insight 1: Periodicidad más común
    if 'periodicidad_reporte' in df.columns:
        periodicidad_top = df['periodicidad_reporte'].mode().iloc[0] if len(df['periodicidad_reporte'].mode()) > 0 else "N/A"
        count_top = len(df[df['periodicidad_reporte'] == periodicidad_top])
        insights.append(f"📊 La periodicidad más común es **{periodicidad_top}** con {count_top} reportes ({count_top/len(df)*100:.1f}%)")
    
    # Insight 2: Departamento con más reportes
    if 'departamento' in df.columns:
        dept_top = df['departamento'].mode().iloc[0] if len(df['departamento'].mode()) > 0 else "N/A"
        count_dept = len(df[df['departamento'] == dept_top])
        insights.append(f"🏢 **{dept_top}** es el departamento con más reportes ({count_dept} reportes)")
    
    # Insight 3: Nivel de automatización
    if 'automatizado' in df.columns:
        pct_auto = len(df[df['automatizado'] == 'Sí']) / len(df) * 100
        if pct_auto < 50:
            insights.append(f"⚠️ Solo el {pct_auto:.1f}% de los reportes están automatizados. Considere priorizar la automatización.")
        else:
            insights.append(f"✅ El {pct_auto:.1f}% de los reportes están automatizados. ¡Buen trabajo!")
    
    # Insight 4: Reportes críticos
    if 'criticidad' in df.columns:
        pct_criticos = len(df[df['criticidad'] == 'Alto']) / len(df) * 100
        if pct_criticos > 30:
            insights.append(f"🔴 El {pct_criticos:.1f}% de los reportes son de criticidad alta. Asegure procesos robustos para estos.")
    
    # Insight 5: Sistema más usado
    if 'sistema_origen' in df.columns:
        sistema_top = df['sistema_origen'].mode().iloc[0] if len(df['sistema_origen'].mode()) > 0 else "N/A"
        count_sistema = len(df[df['sistema_origen'] == sistema_top])
        insights.append(f"💻 **{sistema_top}** es el sistema más utilizado ({count_sistema} reportes)")
    
    # Mostrar insights
    for insight in insights:
        st.info(insight)

if __name__ == "__main__":
    main()
