import httpx
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config


class SignupApp:

    @classmethod
    async def signup(cls, nama, email, no_telp, password):
        hashed_password = DataFormatter.password_encrypt(password)
        timeout = httpx.Timeout(20.0, connect=10.0)
        transport = httpx.AsyncHTTPTransport(retries=3)
        query_params = {"page": "signup"}
        payload = {
            "nama": " ".join(nama.split()).title(),
            "email": email.strip(),
            "no_telp": no_telp.strip(),
            "image": "user.png",
            "role": "user",
            "password": hashed_password,
        }
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, transport=transport) as client:
                response = await client.post(url=config.API_URL, headers=config.HEADERS, params=query_params, json=payload)
                response.raise_for_status()
                result = response.json()
                return {"status": result.get("status", "success"), "message": result.get("message", "Registrasi Sukses...!!!")}
        except httpx.HTTPStatusError as err:
            try:
                server_message = err.response.json().get("message", err.response.text)
            except Exception:
                server_message = (err.response.text or f"HTTP Error {err.response.status_code}")
            DataFormatter.log_msg(f"server error ({err.response.status_code}): {server_message}", tag="registrasi_error")
            return {"status": "error", "message": server_message}
        except httpx.NetworkError as err:
            DataFormatter.log_msg(f"network error: {err}", tag="registrasi_error")
            return {"status": "error", "message": "Koneksi internet terputus atau tidak stabil"}
        except httpx.TimeoutException as err:
            DataFormatter.log_msg(f"timeout error: {err}", tag="registrasi_error")
            return {"status": "error", "message": "Waktu koneksi habis. Silakan coba lagi"}
        except Exception as err:
            DataFormatter.log_msg(f"unexpected error: {err}", tag="registrasi_error")
            return {"status": "error", "message": "Terjadi kesalahan tak terduga"}