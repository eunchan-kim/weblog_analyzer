'''
Created on 2014. 11. 28.

@author: biscuit
'''
from Orange import feature

ip, time, par, ua = [feature.String(x) for x in ['ip', 'time', 'uri_parameter', 'user-agent']]

date, uri, method, status = [feature.Discrete(x) for x in ['date', 'query_uri', 'query_method', 'rcode']]

t_offset, length, ref, lineNo = [feature.Continuous(x) for x in ['t_offset', 'length', 'referer', 'lineNo']]

DoC_t, DoC_ua, DoC_p, DoC_s = [feature.Continuous(x) for x in ['time_DoC', 'u_agent_DoC', 'page_DoC', 'status_DoC']]

ip_freq, page_freq = feature.Continuous('ip_freq'), feature.Continuous('page_freq')
