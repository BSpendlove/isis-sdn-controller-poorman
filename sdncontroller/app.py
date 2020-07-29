from config import Config
from flask import Flask, request, render_template
from flask_migrate import Migrate
import json

app = Flask(__name__)
app.config.from_object(Config)

from models import db
migrate = Migrate(app, db)

from models import BGPLSNode, BGPLSLink, BGPLSPrefixV4
from modules import dbfunctions
from modules.ted import build_visual_ted
from views import exabgptype as exabgp_view

db.init_app(app)
db.create_all()

@app.route("/", methods=["GET"])
def index():
    nodes = dbfunctions.get_bgpls_nodes_all()
    ted_topology = [node.as_dict() for node in nodes]
    app.logger.debug("This is what nodes look like:\n{}".format(str(nodes)))
    topology = build_visual_ted(ted_topology)
    #return json.dumps(topology, indent=4)
    return render_template("index.html", ted=json.dumps(ted_topology,indent=4), ted_json=topology)

if __name__ == "__main__":
    app.register_blueprint(exabgp_view.bp)
    app.run(host="0.0.0.0", port=5000, debug=True)
