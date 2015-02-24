import json
import uuid
import time
import datetime

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
		content = ""
		content += "{0}\n\n".format(uid)
		content += json.dumps(message, indent=4, sort_keys=True)
		content += "\n\n{0}\n".format(uid)
	 	return content

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			uid = uuid.uuid4()
			timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

			subject = "{0} - {1}".format(self.mail_subject, timestamp)
			text = self.make_content(uid, message)

			msg = MIMEText(text, 'plain')
			msg['From'] = email.utils.formataddr((self.mail_name, self.mail_from))
			msg['To'] = email.utils.formataddr(('Recipient', self.mail_to))
			msg['Subject'] = subject

			server = smtplib.SMTP(self.smtp_server)
			try:
				server.sendmail(self.mail_name, [self.mail_to], msg.as_string())
			finally:
				server.quit()

			node.output.send_json({
				'From' : [self.mail_name, self.mail_from],
				'To' : self.mail_to,
				'Subject' : subject,
				'uid' : "{0}".format(uid)
			})
	
if __name__ == "__main__":
	print("Please import this file!")