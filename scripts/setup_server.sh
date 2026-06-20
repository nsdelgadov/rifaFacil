#!/bin/bash
# Ejecutar UNA SOLA VEZ conectado por PuTTY como ec2-user.
#
# ANTES de correr este script, crear el archivo de configuración:
#   sudo nano /etc/rifafacil.env
#
# Con este contenido (valores reales, no ejemplos):
#   RIFA_DB_PATH=/data/rifafacil/rifa.db
#   RIFA_NOMBRE=...
#   RIFA_PRECIO_BOLETO=...
#   RIFA_CANTIDAD_BOLETOS=...
#   RIFA_TELEFONO_ADMIN=...
#   ADMIN_USER=...
#   ADMIN_PASSWORD=...
#   GRILLA_REFRESH_SEGUNDOS=60
#
# Verificar también el nombre del volumen EBS con: lsblk
# El volumen raíz es nvme0n1. El disco de datos debería ser nvme1n1.

set -e

if [ ! -f /etc/rifafacil.env ]; then
  echo "ERROR: falta /etc/rifafacil.env — créalo con tus variables antes de correr este script."
  exit 1
fi

# 1. Actualizar sistema e instalar dependencias
sudo dnf update -y
sudo dnf install -y git python3.12 python3.12-pip nginx certbot python3-certbot-nginx

# 2. Montar volumen EBS
DEVICE=/dev/nvme1n1
MOUNT=/data/rifafacil

sudo mkfs -t xfs $DEVICE
sudo mkdir -p $MOUNT
sudo mount $DEVICE $MOUNT
echo "$DEVICE $MOUNT xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab

sudo chmod 600 /etc/rifafacil.env

# 3. Clonar repo e instalar dependencias
sudo mkdir -p /srv/rifafacil
sudo chown ec2-user:ec2-user /srv/rifafacil
git clone https://github.com/nsdelgadov/rifaFacil.git /srv/rifafacil
cd /srv/rifafacil
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e . --quiet

# 4. Crear servicio systemd
sudo tee /etc/systemd/system/rifafacil.service << 'EOF'
[Unit]
Description=rifaFacil FastAPI app
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/srv/rifafacil
EnvironmentFile=/etc/rifafacil.env
ExecStart=/srv/rifafacil/.venv/bin/uvicorn rifafacil.web.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable rifafacil
sudo systemctl start rifafacil

# 5. Configurar nginx como reverse proxy
sudo cp /srv/rifafacil/nginx/rifafacil.conf /etc/nginx/conf.d/rifafacil.conf
sudo systemctl enable nginx
sudo systemctl start nginx

# 6. Certificado HTTPS (requiere que el DNS ya esté propagado)
# Correr manualmente cuando rifafacil.xyz apunte a esta IP:
#   sudo certbot --nginx -d rifafacil.xyz -d www.rifafacil.xyz

echo "Listo. App corriendo en http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "Cuando el DNS propague, correr: sudo certbot --nginx -d rifafacil.xyz -d www.rifafacil.xyz"
