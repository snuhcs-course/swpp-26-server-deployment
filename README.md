# SWPP 2026 Django API deployment exercise

This starter exposes one JSON endpoint: `/api/health`. The commands match the eight exercise slides. Use your assigned server B team container and keep the same SSH shell open through the exercise. Replace `N` with your team number.

The nginx commands assume it is running with `/etc/nginx/sites-enabled/default` as its only active site. If another application uses port 80, follow your team's migration guide instead.

## 1. Clone the starter

On your laptop, connect to your team container:

```bash
ssh swpp-b
```

In the team container, clone the public repository:

```bash
cd ~
git clone https://github.com/snuhcs-course/swpp-26-server-deployment.git django-deployment-student
cd django-deployment-student
ls README.md manage.py deploy/
```

## 2. Install and configure

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export WEB_HOST=teamN.swpp-2026-b.snu.ac.kr
export DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost,$WEB_HOST"
export DJANGO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
.venv/bin/python manage.py check
```

Use a hostname without `http://`. If `venv` reports missing `ensurepip`, install `python3-venv` in your container and retry.

## 3. Run port 8001

```bash
CLASS26_LAB_WORKER=worker-1 \
  .venv/bin/gunicorn --daemon --workers 2 \
  --bind 127.0.0.1:8001 \
  --pid /tmp/swpp26-api-8001.pid \
  labsite.wsgi:application
curl -i http://127.0.0.1:8001/api/health
cat /tmp/swpp26-api-8001.pid
```

Expect HTTP 200 JSON with `worker-1`.

## 4. Run port 8002

```bash
CLASS26_LAB_WORKER=worker-2 \
  .venv/bin/gunicorn --daemon --workers 2 \
  --bind 127.0.0.1:8002 \
  --pid /tmp/swpp26-api-8002.pid \
  labsite.wsgi:application
curl -s http://127.0.0.1:8001/api/health
echo
curl -s http://127.0.0.1:8002/api/health
echo
```

The two responses should have different worker labels.

## 5. Activate nginx

The repository's `deploy/nginx-site.conf` is a reference. `/etc/nginx/nginx.conf` loads active files from `/etc/nginx/sites-enabled/`. Verify the default site is the only active site:

```bash
sudo systemctl is-active nginx
ls -l /etc/nginx/sites-enabled/
sudo nginx -t
```

Copy the reference to `/etc/nginx/sites-available/swpp26-django-api` and enable its link in `/etc/nginx/sites-enabled/`:

```bash
sudo cp deploy/nginx-site.conf /etc/nginx/sites-available/swpp26-django-api
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/swpp26-django-api /etc/nginx/sites-enabled/swpp26-django-api
sudo nginx -t && sudo systemctl reload nginx
```

If the syntax check fails, restore the default link before reloading:

```bash
sudo rm -f /etc/nginx/sites-enabled/swpp26-django-api
sudo ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
sudo nginx -t
```

## 6. Check the route

```bash
curl -i http://127.0.0.1/
curl -i "http://$WEB_HOST/api/health"
for n in 1 2 3 4; do
  curl -s "http://$WEB_HOST/api/health"
  echo
done
```

The local root is nginx HTML. The public API path is Django JSON. The public root of a `teamN` hostname may show the course HAProxy notice page.

## 7. Observe failover

```bash
kill "$(cat /tmp/swpp26-api-8001.pid)"
sleep 2
curl -i "http://$WEB_HOST/api/health"
kill "$(cat /tmp/swpp26-api-8002.pid)"
sleep 2
curl -i "http://$WEB_HOST/api/health"
```

One port down should still give JSON 200 from `worker-2`; both ports down should give nginx 502. This protects against a local Gunicorn failure, not a whole container or HAProxy failure.

## 8. Restore the API

```bash
CLASS26_LAB_WORKER=worker-1 \
  .venv/bin/gunicorn --daemon --workers 2 \
  --bind 127.0.0.1:8001 \
  --pid /tmp/swpp26-api-8001.pid \
  labsite.wsgi:application
CLASS26_LAB_WORKER=worker-2 \
  .venv/bin/gunicorn --daemon --workers 2 \
  --bind 127.0.0.1:8002 \
  --pid /tmp/swpp26-api-8002.pid \
  labsite.wsgi:application
sleep 1
curl -i "http://$WEB_HOST/api/health"
```

The daemon processes do not restart after reboot. For a lasting deployment, adapt `deploy/env.example` and `deploy/swpp26-django-api@.service.template` with your own paths, Linux user and group, and hostname, then use systemd. Do not commit a real secret key.
