Este proyecto es **un backend para una tienda habanera de venta de productos electrónicos**, desarrollado íntegramente con **Django**. Lo particular y curioso de este proyecto es que **todo se gestiona a través del panel de administración de Django**, usando únicamente **models** para estructurar y controlar la información.

Sin frontend, sin APIs externas, sin interfaces personalizadas — solo puro Django Admin bien usado.

## 🛠️ Tecnologías  

- **Python 3**
- **Django**
- **Django Admin**
- **PostgreSQL**

## 🚀 Cómo levantarlo  

1. Clona el proyecto  
```bash
git clone https://github.com/tuusuario/tu-repo.git
cd tu-repo
```

2. Instala dependencias  
```bash
pip install -r requirements.txt
```

3. Aplica migraciones  
```bash
python manage.py migrate
```

4. Crea un superusuario  
```bash
python manage.py createsuperuser
```

5. Corre el servidor  
```bash
python manage.py runserver
```

6. Entra al admin  
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
---
