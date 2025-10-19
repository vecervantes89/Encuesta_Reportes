import streamlit as st
import hashlib
import os

class Auth:
    def __init__(self):
        # Usuario y contraseña por defecto (en producción usar variables de entorno o DB)
        self.admin_user = os.getenv("ADMIN_USER", "admin")
        self.admin_password_hash = self._hash_password(os.getenv("ADMIN_PASSWORD", "admin123"))
    
    def _hash_password(self, password):
        """Hash de contraseña usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verificar_credenciales(self, username, password):
        """Verificar si las credenciales son correctas"""
        password_hash = self._hash_password(password)
        return username == self.admin_user and password_hash == self.admin_password_hash
    
    def login(self):
        """Mostrar formulario de login y manejar autenticación"""
        # Verificar si ya está autenticado
        if 'autenticado' not in st.session_state:
            st.session_state.autenticado = False
        
        if st.session_state.autenticado:
            return True
        
        # Mostrar formulario de login
        st.markdown("### 🔐 Inicio de Sesión")
        st.info("Por favor inicie sesión para acceder al panel de administración")
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión")
            
            if submit:
                if self.verificar_credenciales(username, password):
                    st.session_state.autenticado = True
                    st.session_state.username = username
                    st.success("✅ Login exitoso")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
                    return False
        
        st.markdown("---")
        st.caption("**Credenciales por defecto:** usuario: `admin` | contraseña: `admin123`")
        st.caption("Para cambiar las credenciales, configure las variables de entorno ADMIN_USER y ADMIN_PASSWORD")
        
        return False
    
    def logout(self):
        """Cerrar sesión"""
        st.session_state.autenticado = False
        if 'username' in st.session_state:
            del st.session_state.username
        st.rerun()
    
    def mostrar_info_usuario(self):
        """Mostrar información del usuario autenticado en la sidebar"""
        if st.session_state.get('autenticado', False):
            with st.sidebar:
                st.markdown("---")
                st.markdown(f"👤 **Usuario:** {st.session_state.get('username', 'N/A')}")
                if st.button("🚪 Cerrar Sesión"):
                    self.logout()
