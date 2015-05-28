#!/usr/bin/env python
#-*- encoding:utf8 -*-

"""
Mail sending helpers

smtp mail server.
"""
from cStringIO import StringIO
from email.MIMEMultipart import MIMEMultipart
from email.MIMENonMultipart import MIMENonMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import logging
import smtplib

class MailSender(object):
    """
    Note: connect to server with ssl strategy not implement.
    """
    
    log = logging.getLogger('toos.mail')
    log.addHandler(logging.StreamHandler())

    def __init__(self, smtphost='localhost', mailfrom='scrapy@localhost',
            smtpuser=None, smtppass=None, smtpport=25, smtptls=False, smtpssl=False):
        self.smtphost = smtphost
        self.smtpport = smtpport
        self.smtpuser = smtpuser
        self.smtppass = smtppass
        self.smtptls = smtptls
        self.smtpssl = smtpssl
        self.mailfrom = mailfrom
        
        if self.smtpssl==True:
            raise NotImplementedError('SSL connect strategy not yet implement')

    def send(self, to, subject, body, cc=None, attachs=(), mimetype='text/plain',body_encode='utf8'):
        if attachs:
            msg = MIMEMultipart()
        else:
            msg = MIMENonMultipart(*mimetype.split('/', 1))
        msg['From'] = self.mailfrom
        msg['To'] = COMMASPACE.join(to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        rcpts = to[:]
        if cc:
            rcpts.extend(cc)
            msg['Cc'] = COMMASPACE.join(cc)

        if attachs:
            msg.attach(MIMEText(body, 'plain', body_encode))
            for attach_name, mimetype, f in attachs:
                part = MIMEBase(*mimetype.split('/'))
                part.set_payload(f.read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' \
                    % attach_name)
                msg.attach(part)
        else:
            msg.set_payload(body)

        try:
            self._sendmail(rcpts, msg.as_string())
        except smtplib.SMTPException, e:
            self._sent_failed(e, to, cc, subject, len(attachs))
            return False
        else:
            self._sent_ok(to, cc, subject, len(attachs))
            return True

    def _sent_ok(self, to, cc, subject, nattachs):
        self.log.info(u'Mail sent OK: To={mailto} Cc={mailcc} '
                       'Subject="{mailsubject}" Attachs={mailattachs}'.format(
                mailto=to, mailcc=cc, mailsubject=subject, mailattachs=nattachs))

    def _sent_failed(self, failure, to, cc, subject, nattachs):
        errstr = str(failure)
        self.log.error(u'Unable to send mail: To={mailto} Cc={mailcc} '
                       'Subject="{mailsubject}" Attachs={mailattachs}'
                       '- {mailerr}'.format(mailto=to, mailcc=cc, mailsubject=subject,
                mailattachs=nattachs, mailerr=errstr)
                )

    def _sendmail(self, to_addrs, msg):
        #msg = StringIO(msg)
        s = smtplib.SMTP()
        s.connect(self.smtphost, self.smtpport)
        if self.smtptls:
            s.starttls()
        s.login(self.smtpuser, self.smtppass)
        s.sendmail(self.mailfrom, to_addrs, msg, )
        s.close()

if __name__ == "__main__":
    EMAIL_HOST = 'smtp.qq.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = '1537740966@qq.com'
    EMAIL_HOST_PASSWORD = 'zzp,2191307'
    
    ms = MailSender(smtphost = EMAIL_HOST, smtpport=EMAIL_PORT,
                    smtpuser=EMAIL_HOST_USER, smtppass=EMAIL_HOST_PASSWORD,
                    mailfrom = '1537740966@qq.com', smtptls=EMAIL_USE_TLS)
    ms.send(['zzpwelkin@163.com',], 'my mail tool test', 'this mai was send by python machine, may be what he want to say is "hello man"')