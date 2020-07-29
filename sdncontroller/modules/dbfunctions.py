from app import app, db
from models import (
    BGPNeighborship,
    BGPLSNode,
    BGPLSLink,
    BGPLSPrefixV4
)

def add_bgp_state(update):
    neighborship = BGPNeighborship(**update)
    db.session.add(neighborship)
    db.session.commit()
    return neighborship

def get_bgp_state(id):
    neighborship = BGPNeighborship.query.filter_by(id).first()
    return neighborship

def get_bgp_states_all():
    all_neighborships = BGPNeighborship.query.all()
    return all_neighborships

def delete_bgp_states_all():
    all_neighborships = BGPNeighborship.query.delete()
    db.session.commit()
    return all_neighborships

def add_bgpls_node(update):
    if get_bgpls_node(update["node_id"]):
        node = update_bgpls_node(update)
        return node
    node = BGPLSNode(**update)
    db.session.add(node)
    db.session.commit()
    return node

def delete_bgpls_node(id):
    return BGPLSNode.query.filter_by(id).delete()

def get_bgpls_node(node_id):
    node = BGPLSNode.query.filter_by(node_id=node_id).first()
    return node

def get_bgpls_nodes_all():
    all_nodes = BGPLSNode.query.all()
    return all_nodes

def delete_bgpls_nodes_all():
    nodes = BGPLSNode.query.delete()
    db.session.commit()
    return nodes

def update_bgpls_node(update):
    node = get_bgpls_node(update["node_id"])
    for key,value in update.items():
        setattr(node, key, value)
    db.session.commit()
    app.logger.debug("Updated Node in database...\n{}".format(node))
    return node

def add_bgpls_link(node, link):
    if not get_bgpls_node(node):
        node = add_bgpls_node({"node_id": node})
    else:
        node = get_bgpls_node(node)
    
    # Check if current link exists..

    app.logger.debug("Trying to see if Link {} exist already...".format(link))
    check_link = BGPLSLink.query.filter_by(
        node_id=node.id,
        local_interface_address=link["local_interface_address"],
        peer_interface_address=link["peer_interface_address"]
    ).first()

    app.logger.debug("check_link value is {}".format(check_link))
    if check_link:
        app.logger.debug("Link already exist {}".format(str(check_link)))
        # Temp solution atm...
        link["node_id"] = node.id
        for key,value in link.items():
            setattr(check_link, key, value)
        db.session.commit()
        app.logger.debug("Updated existing link {}".format(str(check_link)))
        return check_link
    new_link = BGPLSLink(**link)
    app.logger.debug("Attempting to add Link {} to node {}".format(new_link, node))
    node.bgpls_links.append(new_link)
    db.session.commit()
    return new_link

def delete_bgpls_link(id):
    return BGPLSLink.query.filter_by(id=id).delete()

def get_bgpls_link(id):
    link = BGPLSLink.query.get(id)
    return link

def get_bgpls_links_all(node_id):
    links = BGPLSLink.query.filter_by(node_id=node_id)
    return links

def update_bgpls_link(update):
    link = get_bgpls_link(update["id"])
    for key,value in update.items():
        setattr(link, key, value)
    db.session.commit()
    app.logger.debug("Updated Link in database...\n{}".format(node))
    return link

def add_bgpls_prefix(node, prefix):
    note.bgpls_prefixes.append(prefix)
    db.session.commit()
    return prefix

def delete_bgpls_prefix(id):
    return BGPLSPrefixV4.query.filter_by(id).delete()

def get_bgpls_prefix(id):
    prefix = BGPLSPrefixV4.query.get(id)
    return prefix

def get_bgpls_prefixes_all(node_id):
    prefixes = BGPLSPrefixV4.query.filter_by(node_id=node_id)
    return prefixes

def withdraw_update(update):
    if "withdraw" in str(update):
        for withdraw in update["neighbor"]["message"]["update"]["withdraw"]["bgp-ls bgp-ls"]:
            if withdraw["ls-nlri-type"] == "bgpls-link":
                app.logger.debug("withdraw_update found bgpls-link")
                node_id = "{}{}{}".format(
                    withdraw["local-node-descriptors"]["autonomous-system"],
                    withdraw["local-node-descriptors"]["bgp-ls-identifier"],
                    withdraw["local-node-descriptors"]["router-id"]
                
                
                )
                node_id = get_bgpls_node(node_id).id
                app.logger.debug("Filtering based on these columns:\n{}\n{}\n{}".format(
                    node_id,
                    withdraw["interface-address"]["interface-address"],
                    withdraw["neighbor-address"]["neighbor-address"]
                ))
                link = BGPLSLink.query.filter_by(
                        node_id=node_id,
                        #l3_routing_topology=withdraw["l3-routing-topology"],
                        #protocol_id=withdraw["protocol-id"],
                        #local_asn=withdraw["local-node-descriptors"]["autonomous-system"],
                        #local_bgp_ls_id=withdraw["local-node-descriptors"]["bgp-ls-identifier"],
                        #local_router_id=withdraw["local-node-descriptors"]["router-id"],
                        #peer_asn=withdraw["remote-node-descriptors"]["autonomous-system"],
                        #peer_bgp_ls_id=withdraw["remote-node-descriptors"]["bgp-ls-identifier"],
                        #peer_router_id=withdraw["remote-node-descriptors"]["router-id"],
                        local_interface_address=withdraw["interface-address"]["interface-address"],
                        peer_interface_address=withdraw["neighbor-address"]["neighbor-address"]
                ).first()
                app.logger.debug("Query withdraw link results: {}".format(link))
                if link:
                    db.session.delete(link)
                    db.session.commit()
                    app.logger.debug("Removed BGPLSLink {}".format(link))
                return "Successfully deleted link {}".format(str(link))
            if withdraw["ls-nlri-type"] == "bgpls-prefix-v4":
                app.logger.debug("withdraw_update found bgpls-prefix-v4")
                node_id = "{}{}{}".format(
                    withdraw["node-descriptors"]["autonomous-system"],
                    withdraw["node-descriptors"]["bgp-ls-identifier"],
                    withdraw["node-descriptors"]["router-id"]
                )
                prefix = BGPLSPrefixV4.query.filter_by(
                    node_id=node_id,
                    l3_routing_topology=withdraw["l3-routing-topology"],
                        protocol_id=withdraw["protocol-id"],
                        local_asn=withdraw["node-descriptors"]["autonomous-system"],
                        local_bgp_ls_id=withdraw["node-descriptors"]["bgp-ls-identifier"],
                        local_router_id=withdraw["node-descriptors"]["router-id"],
                        ip_reachability_tlv=withdraw["ip-reachability-tlv"],
                        ip_reachability_prefix=withdraw["ip-reach-prefix"]
                ).first()
                if prefix:
                    db.session.delete(prefix)
                    db.session.commit()
                    app.logger.debug("Removed BGPLSPrefixV4 {}".format(prefix))
                return "Successfully deleted prefix {}".format(str(prefix))
