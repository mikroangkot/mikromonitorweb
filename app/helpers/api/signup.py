import httpx
from app.helpers.dataformatter import DataFormatter
from app.helpers.utility.config import config


class SignupApp:

    @classmethod
    async def signup(cls, nama, email, no_telp, password):
        hashed_password = DataFormatter.password_encrypt(password)
        timeout = httpx.Timeout(10.0, connect=5.0)
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
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=timeout
            ) as client:
                response = await client.post(
                    url=config.API_URL,
                    headers=config.HEADERS,
                    params=query_params,
                    json=payload,
                )
                response.raise_for_status()
                ress_json = response.json()
                return {
                    "status": ress_json.get("status", "success"),
                    "message": ress_json.get("message", "Registrasi Sukses...!!!"),
                }
        except httpx.HTTPStatusError as err:
            try:
                server_message = err.response.json().get("message", err.response.text)
            except Exception:
                server_message = (
                    err.response.text or f"HTTP Error {err.response.status_code}"
                )
            DataFormatter.log_msg(
                f"Server Error ({err.response.status_code}): {server_message}",
                tag="registrasi_error",
            )
            return {"status": "error", "message": server_message}
        except httpx.NetworkError as err:
            DataFormatter.log_msg(f"Network Error: {err}", tag="registrasi_error")
            return {
                "status": "error",
                "message": "Koneksi internet terputus atau tidak stabil",
            }
        except httpx.TimeoutException as err:
            DataFormatter.log_msg(f"Timeout Error: {err}", tag="registrasi_error")
            return {
                "status": "error",
                "message": "Waktu koneksi habis. Silakan coba lagi",
            }
        except Exception as err:
            DataFormatter.log_msg(f"Unexpected Error: {err}", tag="registrasi_error")
            return {"status": "error", "message": "Terjadi kesalahan tak terduga"}