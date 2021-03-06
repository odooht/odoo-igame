# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
_logger = logging.getLogger(__name__)

from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID, registry, api


from odoo.addons.bus.controllers.main import BusController

class Message(BusController):

    @http.route('/longpolling/igame', type="json", auth="user")
    def poll2(self, channels, last, options=None):
        msgs = self.poll(channels, last, options)
        new_msgs = []

        for msg in msgs:
            nmsg = self._message(msg)
            nmsg = nmsg and nmsg or msg
            new_msgs.append(nmsg)

        return new_msgs


    def _message(self, msg):
        msg_channel = msg['channel']

        if not isinstance(msg_channel, list):
            return None

        db, model, channel_id = msg_channel
        if request.db != db:
            return None

        if model != 'mail.channel':
            return None

        with registry(db).cursor() as cr:
            uid = request.env.uid
            env = api.Environment(cr, uid, {})
            domain = [('mail_channel_id','=',channel_id)]
            game_channel = env['og.channel'].sudo().search([],limit=1)
            game_channel = game_channel.sudo(uid)

            if not game_channel:
                return None
                
            # no game_channel, return nothing. just soso. a filter
            # msg['message'].body is wrap up by message_post
            # to unwrap msg['message'].body by message_get

            nmsg = msg.copy()
            message_id = msg['message']['id']
            nmsg['msg'] = game_channel.message_get(message_id)
            return nmsg


        return None
