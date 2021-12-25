#!/usr/bin/env python
import os,sys


splunkhome = os.environ['SPLUNK_HOME']

sys.path.append('/usr/bin/python')
sys.path.append('/usr/local/lib/python3.8/site-packages')
sys.path.append('/usr/local/lib/python3.7/site-packages')
sys.path.append('/usr/local/lib/python3.9/site-packages')
sys.path.append('/usr/local/lib/python2.7/site-packages')
sys.path.append(os.path.join(splunkhome, 'etc', 'apps', 'command_pokernow_payment', 'lib'))


from splunklib.searchcommands import dispatch, ReportingCommand, Configuration
@Configuration()
class pokernowpaymentCommand(ReportingCommand):
     @Configuration()
     def map(self, events):
        for event in events:
            yield event

     def reduce(self, events):
          players = {}
          for event in events:
              players[event['player']] = float(event['total'])
              winners = {}
              losers = {}
              neutral = {}
              final = {}

          for k, v in list(players.items()):
               if v > 0:
                    winners[k] = v
               elif v == 0:
                    neutral[k] = v
               else:
                    losers[k] = v

          x = 0

          for k_winner, v_winner in list(winners.items()):
               for k_loser, v_loser in list(losers.items()):
                    if (v_winner==0) or (v_loser==0):
                         continue
                    elif (abs(v_loser)<=v_winner):
                         final[x] = {k_winner:[k_loser,round(abs(v_loser),2)]}
                         v_winner = v_winner - abs(v_loser)
                         losers[k_loser] = 0
                         winners[k_winner] = v_winner
                         x = x + 1
                    elif (abs(v_loser)>v_winner):
                         v_loser = abs(v_loser) - v_winner
                         final[x] = {k_winner:[k_loser,round(v_winner,2)]}
                         losers[k_loser] = -1*v_loser
                         winners[k_winner] = 0
                         v_winner = 0
                         x = x + 1
                         continue
                    else:
                         continue

          for k_winner, loser in list(final.items()):
               result = {}
               for k in list(loser.keys()):
                   result['winner'] = k
                   result['loser'] = loser[k][0]
                   result['pays'] = loser[k][1]
               yield result

dispatch(pokernowpaymentCommand, sys.argv, sys.stdin, sys.stdout, __name__)
