"""
    wsgi.py

    This is the file used to run the web server using a WSGI server like gunicorn
"""

from webServer import app

if __name__ == "__main__":
    app.run()

# https://medium.com/faun/deploy-flask-app-with-nginx-using-gunicorn-7fda4f50066a

# https://www.linode.com/docs/guides/flask-and-gunicorn-on-ubuntu/
