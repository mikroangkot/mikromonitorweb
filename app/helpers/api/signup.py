from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config
from app.helpers.utility.supabase import supabase

class SignupApp:

    @staticmethod
    async def signup(nama, email, no_telp, password):
        try:
            cleaned_nama = ' '.join(nama.split()).title()
            cleaned_email = email.strip().lower()
            cleaned_phone = no_telp.strip()
            rpc_res = supabase.rpc('check_email_exists', {'check_email': cleaned_email}).execute()
            if rpc_res.data and rpc_res.data.get('exists'):
                is_confirmed = rpc_res.data.get('is_confirmed', False)
                if is_confirmed:
                    return {
                        'status': 'error',
                        'message': 'Email sudah terdaftar\nSilahkan login...!!!'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Email sudah terdaftar\nSilahkan cek email anda untuk konfirmasi...!!!'
                    }
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
            if response and response.user:
                return {
                    'status': 'success',
                    'message': 'Registrasi berhasil\nSilahkan cek email anda untuk konfirmasi...!!!'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Registrasi gagal\nSilahkan ulangi...!!!'
                }
        except Exception as err:
            err_message = getattr(err, 'message', str(err))
            DataFormatter.log_msg(err_message, tag='signup_error')
            if 'already registered' in err_message.lower():
                user_message = 'Email sudah terdaftar\nSilahkan login...!!!'
            else:
                user_message = f'Terjadi kesalahan\n{err_message}...!!!'
            return {
                'status': 'error',
                'message': user_message
            }