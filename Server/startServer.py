from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import time
import json
import requests
import pprint
import datetime
import os

import gamestate, payloadparser

x = datetime.datetime.now()
x = x.ctime()
x = str(x).replace(' ', '_').replace(':', '_')
# print(x)
path = os.getcwd()
d = 'data'
files = os.path.join(path, d)
isdir = os.path.isdir(files)
if not isdir:
    os.mkdir(files)
# files = path + "/" + filename
# print(files)\

filename = files +'/' + 'payload_' + x + '.json'
# print(filename)
open(filename, 'a')


class CSGOGameStateServer(HTTPServer):

    def __init__(self, server_address):

        # super(MyServer, self).__init__(server_address, CSGOGameStateRequestHandler)
        # super(CSGOGameStateServer, self).__init__(server_address, CSGOGameStateRequestHandler)
        # self.auth_token = auth_token

        self.gamestate = gamestate.GameState()

        super(CSGOGameStateServer, self).__init__(server_address, CSGOGameStateRequestHandler)
        self.payload_parser = payloadparser.PayloadParser()

        # self.round_phase = ''
        # self.name = ''
        # self.kills = ''
        # self.deaths =''
        # self.health =''
        # self.score = ''
        # self.team = ''
        # self.opponent_team = ''
        # self.team_score = ''
        # self.opponent_team_score = ''
        # # print(opponent_team_score)
        # self.match_win = ''
        # self.reward = ''
        # self.round_win_reward = ''
        # self.round_loss_reward = ''
        # self.kill_reward = ''
        # self.death_reward = ''
        # self.total_reward = ''


        self.reward = 0
        self.total_reward = 0
        self.round_phase = None
        self.deaths = 0
        self.name = None
        self.kills = 0
        self.health = 0
        self.score = 0
        self.data = []
        self.team = None
        self.team_score = 0
        self.opponent_team = None
        self.opponent_team_score = 0
        self.match_win = None

        self.kill_reward = 1000
        self.round_win_reward = 3000
        self.match_win_reward = 10000
        self.death_reward = -2000
        self.round_loss_reward = -6000
        self.match_loss_reward = -20000

    def add_reward(self, n):
        self.reward = self.reward + n
        # print(self.reward)

    def get_reward(self):
        print('get_reward')
        return self.reward

    def reset_reward(self):
        self.reward = 0


class CSGOGameStateRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # print(self.headers)
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')
        # print(body)
        # print('\n\n')
        # print(pprint.pprint(self.responses))
        # print('\n\n')

        a = self.parse_gamestate_payload(json.loads(body))
        print(a)
        # a = json.loads(body)
        #print (a)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def is_payload_authentic(self, payload):
        path = os.getcwd()
        with open(filename, 'a') as outfile:
            json.dump(payload, outfile, indent=4, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
        #Get auth token and redirect packet to correct function
        if 'auth' in payload and 'token' in payload['auth']:
            return 'gamestate'
        elif 'auth' in payload and 'frameSync' in payload['auth']:
            return 'frameSync'
        else:
            return False

    def parse_gamestate_payload(self, payload):
        if self.is_payload_authentic(payload) != 'gamestate':
            print("Not GS")
            return None


        #Local variables for temp payload saving using functions below
        round_phase = self.get_round_phase(payload)
        # print("Round Number :" + str(round_phase))

        name = self.get_player_name(payload)
        kills = self.get_player_kills(payload)
        deaths = self.get_player_deaths(payload)
        health = self.get_player_health(payload)
        score = self.get_player_score(payload)

        # ct_score = self.get_ct_score(payload)
        # print("Team CT Score : " + str(ct_score))

        # t_score = self.get_t_score(payload)
        # print("Team T Score : " + str(t_score))

        ## This line will print
        team = self.get_player_team(payload)
        # print("Your team is : " + str(team))

        # This wont
        opponent_team = ''

        if team=='T':
            t_score = self.get_t_score(payload)
            # print("Your Team Score is : " + str(t_score))
            opponent_team = 'CT'
            ct_score = self.get_ct_score(payload)
            # print("Your Opponent team is : " + opponent_team)
            # print("Opponent Team Score is : " + str(ct_score))
        if team=='CT':
            ct_score = self.get_ct_score(payload)
            # print("Your Team Score is : " + str(ct_score))
            opponent_team = 'T'
            t_score = self.get_t_score(payload)
            # print("Your Opponent team is : " + opponent_team)
            # print("Opponent Team Score is : " + str(t_score))


        team_score = self.get_player_team_score(payload)
        #print(team_score)
        opponent_team_score = self.get_player_opponent_team_score(payload)
        #print(opponent_team_score)
        match_win = self.get_match_win(payload)
        #print(match_win)

        #If there was a change then adjust server data
        #Also add reward
        if round_phase != self.server.round_phase:
            self.server.round_phase = round_phase

        if team != self.server.team:
            self.server.team = team

        if opponent_team != self.server.team:
            self.server.opponent_team = opponent_team

        if team_score != self.server.team_score:
            self.server.team_score = team_score
            self.server.reward += self.server.round_win_reward
            self.server.total_reward += self.server.round_win_reward

        if opponent_team_score != self.server.opponent_team_score:
            self.server.opponent_team_score = opponent_team_score
            self.server.reward += self.server.round_loss_reward
            self.server.total_reward += self.server.round_loss_reward

        if name != self.server.name:
            self.server.name = name

        if kills != self.server.kills:
            self.server.kills = kills
            self.server.reward += self.server.kill_reward
            self.server.total_reward += self.server.kill_reward

        if deaths != self.server.deaths:
            self.server.deaths = deaths
            self.server.reward += self.server.death_reward
            self.server.total_reward += self.server.death_reward

        if health != self.server.health:
            self.server.health = health

        if score != self.server.score:
            self.server.score = score

        if match_win != self.server.match_win:
            self.server.match_win = match_win

        self.server.add_reward(self.server.reward)
        #print(self.server.reward)


#########################################################################################################
    #Functions to get data from payload
    def get_round_phase(self, payload):
        if 'map' in payload and 'round' in payload['map']:
            # roundchanged = False
            # round_phase = 'phase'
            return payload['map']['round']

            # return round_phase
        else:
            return None

    def get_ct_score(self, payload):
        if 'map' in payload and 'team_ct' in payload['map'] and 'score' in payload['map']['team_ct']:

            return payload['map']['team_ct']['score']

            # return round_phase
        else:
            return None

    def get_t_score(self, payload):
        if 'map' in payload and 'team_t' in payload['map'] and 'score' in payload['map']['team_t']:

            return payload['map']['team_t']['score']

            # return round_phase
        else:
            return None

    # Own Team and Opponent team
    def get_player_team(self, payload):
        if 'player' in payload and 'team' in payload['player']:
            #print(self.server.team)
            return payload['player']['team']
        else:
            return None


###################################################################################################
    def get_player_health(self, payload):
        if 'player' in payload and 'state' in payload['player'] and 'health' in payload['player']['state']:
            return payload['player']['state']['health']
        else:
            return None

    def get_player_kills(self, payload):
        if 'player' in payload and 'match_stats' in payload['player'] and 'kills' in payload['player']['match_stats']:
            return payload['player']['match_stats']['kills']
        else:
            return None

    def get_player_deaths(self, payload):
        if 'player' in payload and 'match_stats' in payload['player'] and 'deaths' in payload['player']['match_stats']:
            return payload['player']['match_stats']['deaths']
        else:
            return None

    def get_player_score(self, payload):
        if 'player' in payload and 'match_stats' in payload['player'] and 'score' in payload['player']['match_stats']:
            return payload['player']['match_stats']['score']
        else:
            return None

    def get_player_name(self, payload):
        if 'player_id' in payload and 'name' in payload['player_id']:
            return payload['player_id']['name']
        else:
            return None




    # def get_player_opponent_team(self, payload):
    #     if self.server.team == 'T':
    #         #print("Your opponent is CT")
    #         return 'CT'
    #     elif self.server.team == 'CT':
    #         #print("Your opponent is T")
    #         return 'T'
    #     else:
    #         return None


    # def get_opponent_team(self, payload):
    #     if 'player_id' in payload and 'team' in payload['player_id']:
    #         return payload['player_id']['team']
    #     else:
    #         return None

    def get_player_team_score(self, payload):
        if 'map' in payload and ('team_' + str(self.server.team)) in payload['map']:
            #print(self.server.team)
            return payload['map']['team_' + str(self.server.team)]
        else:
            return None

    def get_match_win(self, payload):
        if self.server.opponent_team_score == 16:
            self.server.match_win = False
            self.server.reward += self.server.match_loss_reward
        elif self.server.team_score == 16:
            self.server.match_win = True
            self.server.reward += self.server.match_win_reward

    def get_player_opponent_team_score(self, payload):
        if 'map' in payload and ('team_' + str(self.server.opponent_team)) in payload['map']:
            return payload['map']['team_' + str(self.server.opponent_team)]
        else:
            return None

    def log_message(self, format, *args):
        """
        Prevents requests from printing into the console
        """
        return

# def start_server():

#     print(time.asctime(), '-', 'CS:GO gamestate server starting')

#     try:
#         CSGOGameStateServer.serve_forever()
#     except (KeyboardInterrupt, SystemExit):
#         print('Server unable to start!')
#         pass

#     start_server.server_close()


def start_server():
    server = CSGOGameStateServer(('localhost', 3000))

    print(time.asctime(), '-', 'CS:GO GSI server starting...\n')

    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

    server.server_close()
    print(time.asctime(), '-', 'CS:GO GSI server stopped\n')

if __name__ == '__main__':
    start_server()