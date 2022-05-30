import jwt


def decode_jwt_token(jwt_token):
    try:
        data = jwt.decode(jwt_token, options={"verify_signature": False})
        return {
            "email": data["sub"],
            "id": data["userId"],
            "tenant_id": data["tenantId"],
            "customer_id": data["customerId"],
            "authority": data["scopes"][0],
            "enabled": data["enabled"],
            "exp": int(data["exp"]*1000)
        }
    except:
        return False