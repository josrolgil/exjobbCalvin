import json
from calvin.utilities import calvinconfig
from calvin.utilities import calvinlogger
_log = calvinlogger.get_logger(__name__)
_conf = calvinconfig.get()

#policy_file=_conf.get("security","security_conf")['translation']['policy_storage_file']

class TranslationPolicy:
	def __init__(self, policy_file):
		try:
			json_policy=open(policy_file, 'r')
			self.json_data=json.load(json_policy)
			json_policy.close()
			self.id=self.json_data["id"]
			self.description=self.json_data["description"]
			self.rules=self.json_data['rules']
		except:
			_log.exception("Failed opening/loading JSON policy file.\n")

	def get_policy_id(self):
		return self.id

	def get_policy_description(self):
		return self.description

	def translate(self, identifier):
		#TODO: check the id format is ok.
		domain=identifier[identifier.find("@")+1:len(identifier)]
		flag=False
		new_id=identifier
		for rule in self.rules:
			if rule["translation_category"]=="domain" and not flag:
				for domains in rule["source"]:
					if domains == domain:
						new_id=rule["result"]
						flag=True
						break
			elif rule["translation_category"]=="identifier" and not flag:
				for ids in rule['source']:
					if ids==identifier:
						new_id=rule["result"]
						flag=True
						break

			elif rule["translation_category"]=="default" and not flag:
				new_id=rule["result"]
				flag=True
		return new_id

	def no_cheating(self, identifier_domain, domain, link_category):
		"""An interdomain transport can not have an identifier of the target domain."""	
		if link_category == "interdomain":
			if identifier_domain == domain:
				raise Exception('\nTried to cheat during the translation.')
				return False
		return True
#identifier[identifier.find("@")+1:len(identifier)]