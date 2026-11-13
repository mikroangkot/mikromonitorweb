from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config
from app.helpers.utility.supabase import supabase

class SigninApp:

    @staticmethod
    async def signin(email, password):
        try:
            cleaned_email = email.strip()
            response = supabase.auth.sign_in_with_password({
                'email': cleaned_email,
                'password': password
            })
            if response.user and response.session:
                user_metadata = response.user.user_metadata or {}
                nama = user_metadata.get('nama', 'user')
                role = user_metadata.get('role', 'user')
                return {
                    'status': 'success',
                    'message': f'Selamat datang kembali\n{nama}',
                    'session': response.session,
                    'user': response.user,
                    'role': role
                }
            else:
                DataFormatter.log_msg('Login gagal: session atau user tidak ditemukan', tag='signin_error')
                return {
                    'status': 'error',
                    'message': 'Login gagal\nsilahkan periksa kembali email dan password anda...!!!'
                }
        except Exception as err:
            err_message = getattr(err, 'message', str(err))
            DataFormatter.log_msg(f'Signin error: {err_message}', tag='signin_error')
            if 'Invalid login credentials' in err_message:
                err_message = 'Email atau password anda salah...!!!!'
            elif 'Email not confirmed' in err_message:
                err_message = 'Email belum dikonfirmasi\nsilahkan cek link verifikasi di email anda...!!!'
            return {
                'status': 'error',
                'message': err_message
            }