from app import app
from flask import Blueprint, request
from modules import dbfunctions
from modules.bgp_message_handler import (
    create_bgp_state,
    create_bgp_node,
    create_bgp_link,
    create_bgp_prefix_v4,
    create_bgp_prefix_v6
)
import json
import logging

app.logger.setLevel(logging.DEBUG)

bp = Blueprint("exabgp", __name__, url_prefix="/exabgp")

@bp.route("/state", methods=["POST"])
def exabgp_state():
    if not request.is_json:
        return {"error": True, "message": "Incorrect format (must be JSON)."}

    data = request.get_json()
    #Sanity check to confirm message type is 'state' (eg neighbor state up/down/connect)
    if data["type"] == "state":
        if data["neighbor"]["state"] == "up":
            app.logger.debug("Neighbor UP detected ({})...".format(data["host"]))
            bgp_state = create_bgp_state(data)
            app.logger.debug("BGP State created for database...\n{}".format(json.dumps(bgp_state, indent=4)))
            #dbfunctions.add_bgp_state(bgp_state)
            return data

        if data["neighbor"]["state"] == "down":
            app.logger.debug("Neighbor DOWN detected ({})...".format(data["host"]))
            ted_id = generate_ted_id(data)
            return data

    return data

@bp.route("/update", methods=["POST"])
def exabgp_update():
    if not request.is_json:
        return {"error": True, "message": "Incorrect format (must be JSON)."}

    data = request.get_json()
    #Sanity check to confirm message type is 'update' (eg. withdraw/announce update)
    if data["type"] == "update":
        app.logger.debug("Received 'update' message from {}.".format(data["neighbor"]["address"]["peer"]))
        """
        if INITIAL_TOPOLOGY:
            TOPOLOGY.append(data)
            #app.logger.debug("Appending 'initial_topology' message to TOPOLOGY.\n{}".format(json.dumps(data, indent=4)))
            if "eor" in data["neighbor"]["message"]:
                ted_id = generate_ted_id(data)
                app.logger.debug("Generate ted_id ({}) from update...".format(ted_id))
                INITIAL_TOPOLOGY = False
                new_topology = None
                try:
                    new_topology = build_ted(TOPOLOGY)
                except Exception as error:
                    app.logger.debug("Exception building TED/topology: {}".format(error))
                app.logger.debug("EOR detected ({}).\nINITIAL_TOPOLOGY={}\nHere is what the topology looks like: {}".format(data["host"], INITIAL_TOPOLOGY, json.dumps(new_topology, indent=4)))
                if new_topology:
                    try:
                        pass
                        #topology_id = db_add_ted(id=ted_id, ted=new_topology)
                    except Exception as error:
                        app.logger.debug("Error adding TED ({}) topology in database... Error: {}".format(ted_id, error))
                    if topology_id:
                        app.logger.debug("Successfully generated TED/Topology... Datbase entry = {}".format(topology_id))
                return {"ted_topology": new_topology }
        else:
            app.logger.debug("UPDATE message json dump:\n{}".format(data))
            ted_id = generate_ted_id(data)
            app.logger.debug("Generate ted_id ({}) from update...".format(ted_id))
            """
    return data

