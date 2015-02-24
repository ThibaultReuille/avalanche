import json
import uuid
import time
import datetime

from json2html import *

import smtplib
import email.utils
from email.mime.text import MIMEText

class Plugin(object):
	def __init__(self, info):
		self.smtp_server = info['attributes']['emailer:smtp-server']
		self.mail_from = info['attributes']['emailer:mail-from']
		self.mail_to = info['attributes']['emailer:mail-to']
		self.mail_name = info['attributes']['emailer:mail-name']
		self.mail_subject = info['attributes']['emailer:mail-subject']

	def make_content(self, uid, message):
		content = "<!-- Generated by Avalanche Emailer Plugin -->\n"
		content += "<html>\n"
		content += "<head></head>\n"
		content += "<body>\n"
		content += "\t<b>{0}</b><br/><br/>\n".format(uid)

		d = message
		if type(message) is list:
			d = dict()
			for i in xrange(0, len(message) - 1):
				d[i] = message[i]
		content += "\t{0}\n".format(json2html.convert(json = d))

		content += "\t<br/><br/><b>{0}</b>\n".format(uid)
		content += "</body>\n"
		content += "</html>\n"
	 	return content

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			uid = uuid.uuid4()
			timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

			subject = "{0} - {1}".format(self.mail_subject, timestamp)
			text = self.make_content(uid, message)

			msg = MIMEText(text, 'html')
			msg['From'] = email.utils.formataddr((self.mail_name, self.mail_from))
			msg['To'] = email.utils.formataddr(('Recipient', self.mail_to))
			msg['Subject'] = subject

			if True:
				server = smtplib.SMTP(self.smtp_server)
				try:
					server.sendmail(self.mail_name, [self.mail_to], msg.as_string())
				finally:
					server.quit()
			else:
				print(text)

			node.output.send_json({
				'From' : [self.mail_name, self.mail_from],
				'To' : self.mail_to,
				'Subject' : subject,
				'uid' : "{0}".format(uid)
			})
	
if __name__ == "__main__":
	print("Please import this file!")