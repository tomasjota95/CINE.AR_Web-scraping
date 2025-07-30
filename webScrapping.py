from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv, find_dotenv, get_key

load_dotenv(find_dotenv())

email = get_key(find_dotenv(), 'EMAIL')
passkey = get_key(find_dotenv(), 'PASSKEY')

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")  # Opcional en Windows
options.add_argument("--window-size=1920,1080")  # Establece un tamaño virtual

# Configurar el navegador (Chrome en este caso)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Ir al sitio de inicio de sesión
driver.get('https://play.cine.ar/inicio')

# Esperar hasta que el campo de login esté presente (puedes usar las clases de la página)
#WebDriverWait(driver, 10).until(
#    EC.presence_of_element_located((By.NAME, "email"))
#)

# Esperar y hacer click en el botón de iniciar sesión
login_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "INICIAR SESIÓN")]'))
)
login_button.click()

# Ingresar credenciales (ajusta los elementos con las clases/campos correctos)
username = driver.find_element(By.NAME, "email")
password = driver.find_element(By.NAME, "password")

time.sleep(2)

# Reemplaza 'usuario' y 'contraseña' con tus credenciales
username.send_keys(email)
password.send_keys(passkey)

# Enviar formulario de login
password.send_keys(Keys.RETURN)

# Esperar después de iniciar sesión
WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'afiche'))
)

# Ahora puedes proceder con el scraping (similar a antes)
# Esperar explícitamente hasta que las tarjetas de las películas estén visibles
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'afiche'))
    )
    print("Contenido cargado correctamente.")
except TimeoutException:
    print("Timeout: No se cargaron las tarjetas a tiempo.")

# Ahora vamos a cargar las películas en el html
peliculas = []

# Buscamos las tarjetas (esto depende de las clases reales del HTML)
cards = driver.find_elements(By.CLASS_NAME, 'image')

for card in cards:
    try:
        try:
            img_title = card.find_element(By.CLASS_NAME, 'img-title')
            titulo = img_title.find_element(By.CLASS_NAME, 'ellipsis').get_attribute('title')
            print(titulo)
        except Exception as e:
            print(f"Error encontrando título: {e}")
        imagen = card.find_element(By.TAG_NAME, 'img').get_attribute('src')
        link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')

        peliculas.append({
            'titulo': titulo,
            'imagen': imagen,
            'link': link
        })
    except Exception as e:
        print(f'Error en una tarjeta: {e}')

# Crear el HTML con Bootstrap (similar al código anterior)

html_output = '''
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Películas Cine.AR</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body.light-mode {
      background-color: #f8f9fa;
      color: #212529;
    }
    body.dark-mode {
      background-color: #121212;
      color: #ffffff;
    }
    .card {
      transition: all 0.3s ease;
    }
    .card:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .light-mode .card {
      background-color: #ffffff;
      color: #212529;
      border: 1px solid #ccc;
    }
    .dark-mode .card {
      background-color: #1e1e1e;
      color: #ffffff;
      border: 1px solid #333;
    }
    .dark-mode .navbar {
      background-color: #1f1f1f !important;
    }
    .light-mode .navbar {
      background-color: #0d6efd !important;
    }
  </style>
</head>
<body class="light-mode">

  <!-- Navbar -->
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container d-flex justify-content-between">
      <a class="navbar-brand" href="#">Cine.AR Películas</a>
      <button id="toggleMode" class="btn btn-outline-light">Modo Oscuro</button>
    </div>
  </nav>

  <!-- Contenido principal -->
  <div class="container my-5">
    <h1 class="mb-4 text-center">Películas Disponibles</h1>
    <div class="row g-4">
'''

for peli in peliculas:
    html_output += f'''
      <div class="col-12 col-sm-6 col-md-4 col-lg-3 d-flex">
        <div class="card h-100 shadow-sm w-100">
          <img src="{peli['imagen']}" class="card-img-top" alt="{peli['titulo']}">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">{peli['titulo']}</h5>
            <a href="{peli['link']}" class="btn btn-primary mt-auto" target="_blank">Ver más</a>
          </div>
        </div>
      </div>
    '''

html_output += '''
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
  <script>
    const toggleButton = document.getElementById('toggleMode');
    const body = document.body;

    function setMode(mode) {
      if (mode === 'dark') {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
        toggleButton.textContent = 'Modo Claro';
      } else {
        body.classList.remove('dark-mode');
        body.classList.add('light-mode');
        toggleButton.textContent = 'Modo Oscuro';
      }
      localStorage.setItem('theme', mode);
    }

    // Inicializar modo guardado
    document.addEventListener('DOMContentLoaded', () => {
      const savedTheme = localStorage.getItem('theme') || 'light';
      setMode(savedTheme);
    });

    // Cambiar modo manualmente
    toggleButton.addEventListener('click', () => {
      const currentTheme = body.classList.contains('light-mode') ? 'light' : 'dark';
      const newTheme = currentTheme === 'light' ? 'dark' : 'light';
      setMode(newTheme);
    });
  </script>
</body>
</html>
'''

# Guardar el HTML en un archivo
with open('peliculas.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

# Cerrar navegador
driver.quit()

print('Archivo "peliculas.html" generado con éxito.')