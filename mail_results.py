#!/usr/bin/env python
import smtplib,sys,os
from email.mime.text import MIMEText
from datetime import datetime
import ConfigParser
#TODO cont: load json results

def send_email(config, to, subj, msg):
    me = config.get('email','mailfrom')
    msg = MIMEText(msg)
    msg['Subject'] = subj
    msg['From'] = me
    msg['To'] = to

    # Credentials (if needed)  
    username = config.get('email','username')
    password = config.get('email','password')
    server = config.get('email','server')
    port = config.getint('email','port')
      
    # The actual mail send  
    try:
        server = smtplib.SMTP(server, port=port)
        server.login(username,password)  
        server.sendmail(me, to, msg.as_string())  
        server.quit() 
        print "Sent email:",msg.as_string()
    except smtplib.SMTPException:
        print "Error: unable to send email"

if __name__=='__main__':
    config = ConfigParser.RawConfigParser()
    fn = os.path.join(os.environ['HOME'],'conf', 'twitter_mining.cfg')
    config.read(fn)
    email(config, 'telvis07@gmail.com', "This is a test message", "This is a test message @ '%s'"%str(datetime.today()))
