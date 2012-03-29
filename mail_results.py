#!/usr/bin/env python
import smtplib,sys,os
from email.mime.text import MIMEText
from datetime import datetime
import ConfigParser

def send_email(config, to, subj, msg, dryrun=False):
    """
    Send email based on config. Sample below:

    [email]
    mailfrom = Foo <foo@bar.com>
    username = foo
    password = fooF00!
    server=mail.bar.com
    port=25
    """
    toaddrs = [addr.strip() for addr in to.split(',')]
    # Config and Credentials (if needed)  
    me = config.get('email','mailfrom')
    username = config.get('email','username')
    password = config.get('email','password')
    server = config.get('email','server')
    port = config.getint('email','port')

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            msg.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
          
    # The actual mail send  
    try:
        msg = MIMEText(msg.encode(body_charset), 'plain', body_charset)
        msg['Subject'] = subj
        msg['From'] = me
        msg['To'] = ", ".join(toaddrs)

        if dryrun:
            print "Dry-run email:",msg.as_string()
            return

        server = smtplib.SMTP(server, port=port)
        server.login(username,password)  
        server.sendmail(me, toaddrs, msg.as_string())  
        server.quit() 
        print "Sent email:",msg.as_string()
    except smtplib.SMTPException:
        print "Error: unable to send email"

if __name__=='__main__':
    config = ConfigParser.RawConfigParser()
    fn = os.path.join(os.environ['HOME'],'conf', 'twitter_mining.cfg')
    config.read(fn)
    email(config, 'example@example.com', "This is a test message", "This is a test message @ '%s'"%str(datetime.today()))
