# !/bin/bash

# This script is related to the following issue:
# https://github.com/rocketchat/rocket.chat/issues/37058

CONTAINER_ID=$(docker ps | grep mongodb: | awk '{print $1}')
docker exec -i $CONTAINER_ID mongosh rocketchat --eval '
db.rocketchat_message.updateMany({ "t": null }, { $unset: { "t": "" } });
db.rocketchat_message.updateMany({ "groupable": null }, { $unset: { "groupable": "" } });
db.rocketchat_message.updateMany({ "tmid": null }, { $unset: { "tmid": "" } });
db.rocketchat_message.updateMany({ "tlm": null }, { $unset: { "tlm": "" } });
db.rocketchat_message.updateMany({ "tcount": null }, { $unset: { "tcount": "" } });
db.rocketchat_message.updateMany({ "replies": null }, { $unset: { "replies": "" } });
db.rocketchat_message.updateMany({ "editedBy": null }, { $unset: { "editedBy": "" } });
db.rocketchat_message.updateMany({ "_importFile": null }, { $unset: { "_importFile": "" } });
db.rocketchat_message.updateMany({ "url": null }, { $unset: { "url": "" } });
db.rocketchat_message.updateMany({ "bot": null }, { $unset: { "bot": "" } });
db.rocketchat_message.updateMany({ "alias": null }, { $unset: { "alias": "" } });
db.rocketchat_message.updateMany({ "mentions": null },{ $set: { "mentions": [] } });
db.rocketchat_message.updateMany({ "urls": null },{ $set: { "urls": [] } });
'
