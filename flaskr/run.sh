source ~/virtualenv/bin/activate
sudo pip install --editable .
export FLASK_DEBUG=true
export FLASK_APP=flaskr
flask initdb
flask run