#!/usr/bin/env PYTHON
#-*- encoding:utf8 -*-

##
# ip proxy util
#
# Note: sqlite version need newer than 3.8.2 
##

MIN_SQLITE_VERSION = (3, 8, 2)

import sqlite3
import sys

for i, v in enumerate(sqlite3.sqlite_version.split('.')):
    if int(v)>MIN_SQLITE_VERSION[i]:
        break
    elif int(v)<MIN_SQLITE_VERSION[i]:
        raise Exception("The version of current sqlite3 is {0} and older than {1}".format(
                        sqlite3.sqlite_version, '.'.join(MIN_SQLITE_VERSION))) 

class IpsManager(object):
    """
    ips manager which are used by proxying. batch_put method should be used 
    to initial manager. MAX_ELAPSED should be used to update some ips of domains
    when them have been not used for this domains.
    
    There are two strategy ${TIME_ELASPED} and ${TIME_UNUSED} for getting ip 
    from ips manager. ${latest_time_interval} can be set to filter ips which 
    was not been in interval from latest time to now when ${TIME_ELASPED} 
    strategy was used. ${high_elasped} means time elapsed threshold when 
    ${TIME_UNUSED} strategy was used. 
    
    more decribe:
        tables schema: ips(ip, domain , last_elapsed, aver_elapsed, used_num, lock, latest_used).
        The ${last_elapsed} and ${aver_elapsed} is last request and average request 
        elapsed time respectively, the total requests have been send was saved 
        in ${used_num}, and the ip record was locked when it was getted by 
        setting ${lock} to True and was unlocked when ${update_time_elapsed} 
        method was issued.  
    """
    _handle = None
    MAX_ELAPSED = sys.float_info.max
    
    # get ip from proxy strategy 
    TIME_ELASPED = 1
    TIME_UNUSED = 2
    
    def __init__(self, file, get_strategy=TIME_ELASPED, latest_time_interval=1, 
                    high_elapsed=60):
        self._handle = sqlite3.connect(file)
        self._get_strategy = get_strategy
        self._latest_time_interval = latest_time_interval
        self._high_elapsed = high_elapsed
        try:
            self._handle.execute("select 1 from ips")
        except sqlite3.OperationalError:
            import time
            self._handle.execute('create table ips(ip varchar(30),\
            domain varchar(20), last_elapsed float default 0.0, \
            aver_elapsed float default 0.0, \
            used_num int default 1, \
            lock boolean default 0,\
            latest_used int default {0},\
            constraint ips_primary_key primary key (ip, domain));'.format(
                            int(time.time())))
            
            self._handle.execute('create index ips_ip_domain_idx on ips(ip, domain)')
            self._handle.execute('create index ips_domain_last_idx on ips(domain, last_elapsed)')
            self._handle.execute('create index ips_domain_aver_idx on ips(domain, aver_elapsed)')
            self._handle.execute('create index ips_domain_latest_used_idx on ips(domain, latest_used)')
            self._handle.commit()
            
    def __del__(self):
        self._handle.close()
            
    def _insert(self, ips, domains):
        pre_sql = "insert or ignore into ips(ip, domain) values "
        for ip in ips:
            for d in domains:
                self._handle.execute(pre_sql + "('{0}','{1}')".format(ip, d))

        self._handle.commit()
        
    def dump(self, file, max_elapsed=60):
        """
        dump ip manager data to ${file}
        
        @param max_elapsed: the record that ${last_elapsed} and ${aver_elapsed} 
            bigger than this value will not be dumped 
        """
        cur = self._handle.execute("select ip, domain, last_elapsed, aver_elapsed, \
            used_num, latest_used from ips where last_elapsed<{0} and aver_elapsed<{0}".format(max_elapsed))
        with open(file, 'w') as f:
            for r in cur.fetchall():
                f.write(','.join([str(v) for v in r]))
                f.write('\n')
    
    def load(self, file):
        """
        load data to ip manager
        """
        ins = "insert or ignore into ips(ip, domain, last_elapsed, aver_elapsed, used_num, latest_used) values "
        with open(file, 'r') as f:
            cnt = f.read()
        
        ins += ','.join(['({0})'.format(','.join([ "'{0}'".format(_v) for _v in v.split(',')])) 
                        for v in cnt.strip().split('\n')])
        self._handle.execute(ins)
        self._handle.commit()
        
    def update_time_elapsed(self, ip, domain, elasped):
        """
        update time elapsed information to ${ip} with domain ${domain}. The 
        """
        upsql = "update ips set last_elapsed={le}, used_num=used_num+1, \
        aver_elapsed={le}/used_num+aver_elapsed*used_num/(used_num+1), lock=0 \
        where ip='{ip}' and domain='{dm}'".format(le=elasped, ip=ip, dm=domain)
        self._handle.execute(upsql)
        self._handle.commit()
        
    def unlock(self, ip, domain):
        """
        unlock ip record
        """
        upsql = "update ips set lock=0 where ip='{ip}' and domain='{dm}'".format(
                        ip=ip, dm=domain)
        self._handle.execute(upsql)
        self._handle.commit()
        
    def lockclear(self):
        """
        clear lock flag of all ips
        """
        self._handle.execute("update ips set lock=0")
        self._handle.commit()
        
    def get(self, domain, last_elapsed=False, delay=30):
        """
        get one ip of ${domain} and max request elapsed time less than ${delay}
        
        @param domain: 
        @param last_elapsed: get the fast proxy by average request 
                elapsed time or last request elapsed time
        @param delay: max delay request
        """
        type = 'last_elapsed' if last_elapsed else 'aver_elapsed'
        if self._get_strategy == self.TIME_ELASPED:
            cur = self._handle.execute("select ip from ips where domain='{0}' \
                and {1}<{2} and lock=0 and latest_used<strftime(\'%s\',\'now\')\
                - {3} order by {1} limit 1".format(domain, type, delay, 
                                self._latest_time_interval))
        else:
            cur = self._handle.execute("select ip from ips where domain='{0}' \
                and {1}<{2} and lock=0 and latest_used<strftime(\'%s\',\'now\')\
                - {3} order by latest_used limit 1".format(domain, type, 
                                min(self._high_elapsed, delay), 
                                self._latest_time_interval))
        
        ip = cur.fetchone()
        if ip:
            # lock this ip record and update the latest used time stamp
            self._handle.execute("update ips set lock=1,latest_used=strftime(\'%s\',\'now\')\
             where ip='{0}' and domain='{1}'".format(ip[0], domain))
            self._handle.commit()
            return ip[0]
        else:
            return None
    
    def put_ip(self, ips=[]):
        """
        put ${ips} to manager
        """
        cur = self._handle.execute("select domain from ips group by domain")
        domains = [r[0] for r in cur.fetchall()]
        self._insert(ips, domains)
        
    def put_domain(self, domains=[]):
        """
        put ${domains} to manager
        """
        cur = self._handle.execute("select ip from ips group by ip")
        ips = [r[0] for r in cur.fetchall()]
        self._insert(ips, domains)
    
    def batch_put(self, ips, domains):
        """
        Batch puth ${ips} with ${domains} respectively to manager.
        """
        self.put_ip(ips)
        self.put_domain(domains)
        self._insert(ips, domains)
        
    def info(self):
        """
        Get this ip manager information {total_ips, locked_ips, domains}
        """
        res = {}
        cur = self._handle.execute("select count(*) from ips")
        res['total_ips'] = cur.fetchone()[0]
        cur = self._handle.execute("select count(*) from ips where lock=1")
        res['locked_ips'] = cur.fetchone()[0]
        cur = self._handle.execute("select domain from ips group by domain")
        dm = cur.fetchall()
        res['domain'] = [ r[0] for r in dm] if dm else None
        return res
        
        
def test_proxy(file):
    ipm = IpsManager(file)
    ipm.batch_put(['221.176.14.72:80', '211.144.81.68:18000'], domains=['che168', 'ganji',])
    ipm.put_ip(['58.132.25.19:3128', ])
    ipm.put_domain(['58', ])
    ip1 = ipm.get('ganji', True)
    ip2 = ipm.get('ganji', False)
    ipm.update_time_elapsed(ip1, 'ganji', '0.07')
    ipm.update_time_elapsed(ip2, 'ganji', '0.05')
    ip3 = ipm.get('ganji')
    print 'last total information:'
    print ipm.info()
    
    # dump data to file
    print "dumped data to file"
    ipm.dump(file+'.txt')
    
    print "load data to new ip manager"
    oipm = IpsManager(':memory:')
    oipm.load(file+'.txt')
    print 'last total information:'
    print oipm.info()
    assert oipm.info()==ipm.info

def main():
    from optparse import OptionParser, OptionGroup
    usage = "%prog [OPTIONS]"
    description = u"代理IP管理. "
    parser = OptionParser(usage=usage, description=description)
    parser.add_option('-t', '--test', action='store_true', help=u"测试")
    parser.add_option('-i', '--init', action='store_true', help=u'初始化')
    parser.add_option('-a', '--add', action='store_true', help=u'添加ip或domain')
    
    tg = OptionGroup(parser, u"测试")
    tg.add_option('-f', dest='file', action='store', help=u"保存代理IP的文件")

    tg = parser.add_option_group(tg)
    
    ig = OptionGroup(parser, u"初始化")
    ig.set_description("-s IPS_FILE -d dm1,dm2 -f FILE OR -p ip1,ip2 -d dm1,dm2 -f FILE")
    ig.option_list.append(tg.get_option('-f'))
    ig.add_option('-s', dest='ips_file', action='store', help=u"从文件中获取初始化入库的ip")
    ig.add_option('-p', dest='ips', action='store', help=u"逗号分割的ip列表，如 221.176.14.72:80,211.144.81.68:18000")
    ig.add_option('-d', dest='domains', action='store', help=u"逗号分割的domain列表，如 che300,ganji")
    tg = parser.add_option_group(ig)
    
    adg = OptionGroup(parser, u"添加ip或domain")
    adg.set_description("-p ip1,ip2 -f FILE OR -d dm1,dm2 -f FILE")
    adg.option_list.append(tg.get_option('-f'))
    adg.option_list.append(ig.get_option('-p'))
    adg.option_list.append(ig.get_option('-d'))
    tg = parser.add_option_group(adg)
    
    options, _ = parser.parse_args()
    
    def valid_check(mandatories=[]):
        for m in mandatories:
            if not options.__dict__[m]:
                print u"ERROR: 必要元素 {0} 不能为空".format(m)
                exit(-1)

    if options.test:
        valid_check(['file', ])
        test_proxy(options.file)
    elif options.init:
        valid_check(['domains', 'file'])
        ipm = IpsManager(options.file)
        if options.ips_file:
            with open(options.ips_file) as ipf:
                ipm.batch_put(ipf.read().split(), options.domains.split(','))
        elif options.ips:
            ipm.batch_put(options.ips.split(','), options.domains.split(','))
        else:
            print u"ERROR: 请输入IP列表"
            exit(-1)
    elif options.add:
        valid_check(['file', ])
        ipm = IpsManager(options.file)
        if options.ips:
            ipm.put_ip(options.ips.rstrip(',').split(','))
        elif options.domains:
            ipm.put_domain(options.domains.split(','))
        else:
            print u"ERROR: 请输入IP列表或DOMAIN列表"
            exit(-1)
    else:
        print parser.print_help()

if __name__ == "__main__":
    main()