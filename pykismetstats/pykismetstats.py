#!/usr/bin/env python
'''
pykismetstats parse .netxml file generated by kismet 
and write statistics to CSV file.

XML parsing based on pykismetkml
http://code.google.com/p/pykismetkml

Following stats are implemented:
 - channel usage ( how many networks works on each channel )
 - manufacturer ( how many AP by each vendor )
 - encryption ( none/wep/wpa+wpa2, do not distinguish between wpa/wpa2 )


@author: ziherung.pl
'''
import optparse
import xml.dom.minidom
import csv

class OptionParser (optparse.OptionParser):
    def check_required (self, opt, stop):
        option = self.get_option(opt)
        if getattr(self.values, option.dest) is None:
            if stop:
                return False
            else:
                self.error("%s option not supplied" % option)
        else:
            return True

def parse(filename,networks):
    
    document = xml.dom.minidom.parse(filename)
    items = document.getElementsByTagName("wireless-network")
    
    for item in items:
        network = dict()
        # work only on 'infrastructure' networks
        if item.getAttribute('type') == 'infrastructure':
            
            # get ssid / cloaked
            if ( item.getElementsByTagName('essid').item(0).getAttribute('cloaked') ) == 'false':
                network['cloaked'] = 'false'
                network['ssid'] = item.getElementsByTagName('essid').item(0).firstChild.data
            else:
                network['cloaked'] = 'true'
                network['ssid'] = ' '
                
            network['manuf'] = item.getElementsByTagName('manuf').item(0).firstChild.data
            network['channel'] = item.getElementsByTagName('channel').item(0).firstChild.data
            network['encryption'] = item.getElementsByTagName('encryption').item(0).firstChild.data
            network['bssid'] = item.getElementsByTagName('BSSID').item(0).firstChild.data
        
            networks.append(network)
        
def save_output(outputfile,networks,stats):
    '''Save parsed data to .csv'''
    with open(outputfile,'wb') as csvoutput:
        csvwriter = csv.writer(csvoutput,delimiter=';',quotechar='"')
        
        for el in stats:
            csvwriter.writerow(el)
            
        csvwriter.writerow(['ssid','cloaked','encryption','manufacturer','channel','bssid'])
        for net in networks:
            csvwriter.writerow([net['ssid'],net['cloaked'],net['encryption'],net['manuf'],
                               net['channel'],net['bssid']])
            
    
        
def make_stats(networks,stats):
    '''Function get statistics about channel usage, encryption and AP manufacturers'''
    
    channels_desc = range(1,15,1)
    channels_amount = [0]*14
    
    manuf = dict()
    enc = {'wpa/wpa2':0,'wep':0,'none':0}
    
    for net in networks:
        channels_amount[int(net['channel'])-1]+=1
        if manuf.has_key(net['manuf']):
            manuf[net['manuf']]+=1
        else:
            manuf[net['manuf']]=1
        if net['encryption'].find('WPA') != -1:
            enc['wpa/wpa2']+=1
        elif net['encryption'].find('WEP') != -1:
            enc['wep']+=1
        else:
            enc['none']+=1
            
        
        
        
    stats.append(['channel usage:'])
    stats.append(channels_desc)
    stats.append(channels_amount)
    
    stats.append(['----------'])
    stats.append(['manufacturer','amount'])
    for k,v in manuf.iteritems():
        stats.append([k,v])
        
    stats.append(['----------'])
    stats.append(['encryption','amount'])
    for k,v in enc.iteritems():
        stats.append([k,v])
    
    stats.append(['----------'])
    
    
    


if __name__ == '__main__':
    usage = "%prog -i <kismet_netxml_file> [ optional -o <csv_output> ]"
    parser = OptionParser(usage=usage)
    parser.add_option("-i","--input", dest="netxml",help="NetXML input file generated by kismet")
    parser.add_option("-o", "--output", dest="csvoutput", help="( Optional ) Path to CSV output file, out.csv if not specified.")
    
    (options, args) = parser.parse_args()
    parser.check_required("-i", False)
    filename = options.netxml
    
    if parser.check_required("-o", True):
        outputfile = options.csvoutput
    else:
        outputfile = "out.csv"
    
    networks = []
    stats = []
    
    parse(filename,networks)
    make_stats(networks, stats)
    save_output(outputfile,networks,stats)
        