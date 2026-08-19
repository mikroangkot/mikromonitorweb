import jwt

class DecodeToken:

	@staticmethod
	def decodetoken(token):
		payload = jwt.decode(token, options={"verify_signature": False})
		return payload