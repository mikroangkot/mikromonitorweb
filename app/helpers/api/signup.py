from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config
from app.helpers.utility.supabase import supabase

class SignupApp:

    @staticmethod
    async def signup(nama, email, no_telp, password):
        try:
            cleaned_nama = ' '.join(nama.split()).title()
            cleaned_email = email.strip()
            cleaned_phone = no_telp.strip()
            response = supabase.auth.sign_up({
                'email': cleaned_email,
                'password': password,
                'options': {
                    'data': {
                        'nama': cleaned_nama,
                        'no_telp': cleaned_phone,
                        'image': 'user.png',
                        'role': 'user'
                    }
                }
            })
            if response.user:
                return {
                    'status': 'success',
                    'message': 'Registrasi berhasil, silahkan cek email anda'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Registrasi gagal, silahkan ulangi'
                }
        except Exception as err:
            err_message = getattr(err, 'message', str(err))
            DataFormatter.log_msg(f'Signup error: {err_message}', tag='registrasi_error')
            return {
                'status': 'error',
                'message': err_message
            }