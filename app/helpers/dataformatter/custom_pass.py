import bcrypt

class PasswordBcrypt:

	@staticmethod
	def password_encrypt(password: str) -> str:
		salt = bcrypt.gensalt()
		hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
		return hashed.decode('utf-8')

	def password_bcrypt(password: str, hashed_password: str | bytes) -> bool:
		password_bytes = password.encode("utf-8")
		if isinstance(hashed_password, str):
			hashed_password = hashed_password.encode("utf-8")
		match: bool = bcrypt.checkpw(password_bytes, hashed_password)
		return match